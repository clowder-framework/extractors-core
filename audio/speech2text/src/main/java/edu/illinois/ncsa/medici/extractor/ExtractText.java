package edu.illinois.ncsa.medici.extractor;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;

import org.json.*;
import org.apache.commons.io.FileUtils;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

import com.fasterxml.jackson.databind.ObjectMapper;

import com.rabbitmq.client.AMQP;
import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;
import com.rabbitmq.client.DefaultConsumer;
import com.rabbitmq.client.Envelope;

import edu.cmu.sphinx.api.Configuration;
import edu.cmu.sphinx.api.SpeechResult;
import edu.cmu.sphinx.api.StreamSpeechRecognizer;
import edu.cmu.sphinx.result.WordResult;

public class ExtractText {
    private static Log logger = LogFactory.getLog(ExtractText.class);

    // ----------------------------------------------------------------------
    // BEGIN CONFIGURATION
    // ----------------------------------------------------------------------

    // name where rabbitmq is running
    private static String rabbitmqURI; // = "localhost";

    // name to show in rabbitmq queue list   
    private static String exchange; // = "medici";
    
    // name to show in rabbitmq queue list
    private static String extractorName; // = "audio2text";

    // accept any type of file that is audio
    private static String messageType; // = "*.file.audio.#";
    // ----------------------------------------------------------------------
    // END CONFIGURATION
    // ----------------------------------------------------------------------

    DateFormat dateformat = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSXXX");
    ObjectMapper mapper = new ObjectMapper();


/// MAIN /////////////////////////////////////////////////////////////////////    
    
    public static void main(String[] argv) throws Exception {
    	// get config.properties
    	Properties props = new Properties();
    	FileInputStream inStream;
    	try{
    		inStream = new FileInputStream("config.properties");
    		props.load(inStream);
    		inStream.close();
    	} catch (FileNotFoundException e) {
    		e.printStackTrace();
    	} catch (IOException e){
    		e.printStackTrace();
    	}
    	
    	rabbitmqURI = props.getProperty("rabbitmqURI","amqp://guest:guest@127.0.0.1:5672/%2f");
    	exchange = props.getProperty("exchange","clowder");
    	extractorName = props.getProperty("extractorName","ncsa.audio.speech2text");
    	messageType = "*.file.audio.#";

        // get rabbitmqURI from system env if using docker
        if(System.getenv("RABBITMQ_URI") != null){
            rabbitmqURI = System.getenv("RABBITMQ_URI");
        }
    	  	     	    
        // setup connection parameters
        ConnectionFactory factory = new ConnectionFactory();
        factory.setUri(rabbitmqURI);


        // connect to rabbitmq
        Connection connection = factory.newConnection();
        // connect to channel
        final Channel channel = connection.createChannel();
        // declare the exchange
        channel.exchangeDeclare(exchange, "topic", true);
        // declare the queue
        channel.queueDeclare(extractorName, true, false, false, null);
        // connect queue and exchange
        channel.queueBind(extractorName, exchange, messageType);
        // create listener
        channel.basicConsume(extractorName, false, "", new DefaultConsumer(channel) {
            @Override
            public void handleDelivery(String consumerTag, Envelope envelope,
                    AMQP.BasicProperties header, byte[] body) throws IOException {
                ExtractText we = new ExtractText();
                we.onMessage(channel, envelope.getDeliveryTag(), header, new String(body));
            }
        });

        // start listening
        logger.info("[*] Waiting for messages. To exit press CTRL+C");
        while (true) {
            Thread.sleep(1000);
        }
    }

/// ON MESSAGE ////////////////////////////////////////////////////////////////////////////////////////////

    public void onMessage(Channel channel, long tag, AMQP.BasicProperties header, String body) {
        File inputfile = null;
        String fileid = "";
        String secretKey = "";
        
        try {
            @SuppressWarnings("unchecked")
            Map<String, Object> jbody = mapper.readValue(body, Map.class);
            String host = jbody.get("host").toString();
            fileid = jbody.get("id").toString();
            secretKey = jbody.get("secretKey").toString();
            String intermediatefileid = jbody.get("intermediateId").toString();
            if (!host.endsWith("/")) {
                host += "/";
            }
            statusUpdate(channel, header, fileid, "Started processing file");
            
            // download the file
            inputfile = downloadFile(channel, header, host, secretKey, fileid, intermediatefileid);
                      
            // process file
            processFile(channel, header, host, secretKey, fileid, intermediatefileid, inputfile);

            inputfile.delete();

            // send ack that we are done
            channel.basicAck(tag, false);
        } catch (Throwable thr) {
            logger.error("Error processing file", thr);
            try {
                statusUpdate(channel, header, fileid, "Error processing file : " + thr.getMessage());
            } catch (IOException e) {
                logger.warn("Could not send status update.", e);
            }
        } finally {
            try {
                statusUpdate(channel, header, fileid, "Done");
            } catch (IOException e) {
                logger.warn("Could not send status update.", e);
            }
            if (inputfile != null) {
                inputfile.delete();
            }
        }
    }


    private void statusUpdate(Channel channel, AMQP.BasicProperties header, String fileid,
            String status) throws IOException {
        logger.debug("[" + fileid + "] : " + status);

        Map<String, Object> statusreport = new HashMap<String, Object>();
        statusreport.put("file_id", fileid);
        statusreport.put("extractor_id", extractorName);
        statusreport.put("status", status);
        statusreport.put("start", dateformat.format(new Date()));

        AMQP.BasicProperties props = new AMQP.BasicProperties.Builder().correlationId(
                header.getCorrelationId()).build();
        channel.basicPublish("", header.getReplyTo(), props,
                mapper.writeValueAsBytes(statusreport));
    }

/// DOWNLOAD FILE FROM MEDICI //////////////////////////////////////////////////////////////////////////	
    
    private File downloadFile(Channel channel, AMQP.BasicProperties header, String host,
            String key, String fileid, String intermediatefileid) throws IOException, JSONException, InterruptedException {
        statusUpdate(channel, header, fileid, "Downloading file");
        
        URL source = new URL(host + "api/files/" + intermediatefileid + "?key=" + key);
        URL metadataUrl = new URL(host + "api/files/" + intermediatefileid + "/metadata?key=" + key);
        
//== GET FILE TYPE ======================================
        //TODO: there is probably a simpler way to get this from the json
        HttpURLConnection conn = (HttpURLConnection) metadataUrl.openConnection();
        if (conn.getResponseCode() != 200) {
		    throw new IOException(conn.getResponseMessage());
		  }		
		BufferedReader readMetadata = new BufferedReader(new InputStreamReader(conn.getInputStream()));
		StringBuilder sbMetadata = new StringBuilder();
		String line;
		while((line = readMetadata.readLine())!=null){
			sbMetadata.append(line);
		}		
		readMetadata.close();		
		conn.disconnect();
		JSONObject jsonOut = new JSONObject(sbMetadata.toString());

		String contentType = jsonOut.getString("content-type");
		String[] contentParts = contentType.split("/");
		String fileType = contentParts[1];
		
//=== SAVE TEMP FILE ===========================================================
//		File inputFile = File("/home/marcuss/Desktop/workspace_sphinx/test_sphinx/sound_files/medici_out." + fileType);
		File inputFile = File.createTempFile("medici","."+fileType);
		inputFile.deleteOnExit();
		FileUtils.copyURLToFile(source, inputFile);
	

//		File outputFile = inputFile; //what's the point of this, think when I wrote this I forgot that this is a reference not a  copy
		
////=== GET FILE INFO FROM ffmpeg ================================================	
//		ProcessBuilder pb = new ProcessBuilder("ffmpeg","-i",inputFile.toString());
//	    final Process p = pb.start();
//	    final ArrayList<String> metadataFfmpeg = new ArrayList<String>();
//	    new Thread() {
//		      public void run() {		        
//		        String line;
//		        BufferedReader input = new BufferedReader(new InputStreamReader(p.getErrorStream()));
//		        int numLinesFfmpegOut = 0;
//				try {
//					while ((line = input.readLine()) != null) {
//					    metadataFfmpeg.add(line);
//					  }
//				} catch (IOException e1) {
//					e1.printStackTrace();
//				}
//				  try {
//					input.close();
//				} catch (IOException e) {
//					e.printStackTrace();
//				}
//		      }
//	    }.start();
//		p.waitFor();
//
////=== GET AUDIO DATA ========================================================================
//		Map<String, String> audioData = new HashMap<String, String>();
//		for(int i=0; i < metadataFfmpeg.size();i++){
//			if(metadataFfmpeg.get(i).contains("Stream")){
//				System.out.println(i + metadataFfmpeg.get(i));
//		    	String[] parts = metadataFfmpeg.get(i).split(",");
//		    	audioData.put("sample_rate", parts[1].substring(1));
//		    	audioData.put("number_channels", parts[2].substring(1));
//		    	audioData.put("precision", parts[3].substring(1));
//		    	audioData.put("bit_rate", parts[3].substring(1));
//		    }		    	
//		}		
//		System.out.println(audioData.toString());   
		    
//=== COVERT FILE TO FORMAT THAT SPHINX CAN USE =================================


		String outputFileName = "/tmp/outfile.wav";
        File outputFile = new File(outputFileName);

        System.out.println("Converting");
		// convert bitrat and bandwidth
		String intermediateFileName = "/tmp/intermediate.wav";
        try{
			String convertCmd = "ffmpeg -i " + inputFile + " -acodec pcm_s16le -ar 16000 " + intermediateFileName;
			Process convertOut = Runtime.getRuntime().exec(convertCmd);
            //convertOut.waitFor(); //This does not work, it is blocked
                        
            File intermediateFile = new File(intermediateFileName);
            while(intermediateFile.exists()== false){
                Thread.sleep(30); //if used less time, less number of phrases are extracted
            }
            System.out.println("File is created now:"+ intermediateFileName);

			// make sure it's mono
			
			String convertCmd2 = "ffmpeg -i " + intermediateFile + " -ac 1 " + outputFileName;
			
            Process convertOut2 = Runtime.getRuntime().exec(convertCmd2);
            
            
            while(!outputFile.exists()){
                System.out.println("File does not exist yet" + outputFileName);
                Thread.sleep(30);
            }
            System.out.println("File is created now:"+ outputFileName);
                    // clean up intermediate file
            if(intermediateFile.exists()){
                System.out.println("Deleting intermediate file");
                intermediateFile.delete();
            }

				             
            System.out.println("Output File: " + outputFile);
            if(inputFile.exists()){
                inputFile.delete();
            }
        } catch (Exception e){
            System.out.println("Conversion Failed");
        }
        
        return outputFile;
    }
  
/// PROCESS THE FILE //////////////////////////////////////////////////////////////////////////
    private void processFile(Channel channel, AMQP.BasicProperties header, String host, String key,
            String fileid, String intermediatefileid, File inputfile) throws IOException {
        statusUpdate(channel, header, fileid, "Processing audio file to text");        

        Configuration configuration = new Configuration();

        //	configuration.setSampleRate(8000)   Haven't used but curious about setting sample rate
    	
    	// Set path to acoustic model.
    	configuration.setAcousticModelPath("resource:/edu/cmu/sphinx/models/en-us/en-us");
    	// Set path to dictionary.
    	configuration.setDictionaryPath("resource:/edu/cmu/sphinx/models/en-us/cmudict-en-us.dict");
    	// Set language model.
    	configuration.setLanguageModelPath("resource:/edu/cmu/sphinx/models/en-us/en-us.lm.bin");

        //        configuration.setAcousticModelPath("resource:/WSJ_8gau_13dCep_16k_40mel_130Hz_6800Hz"); 
        //	  configuration.setAcousticModelPath("resource:/edu/cmu/sphinx/models/acoustic/wsj/WSJ_8gau_13dCep_16k_40mel_130Hz_6800Hz");
        //        configuration.setAcousticModelPath("resource:/WSJ_8gau_13dCep_8kHz_31mel_200Hz_3500Hz");        
        //        configuration.setDictionaryPath("resource:/WSJ_8gau_13dCep_16k_40mel_130Hz_6800Hz/dict/cmudict.0.6d");
        //        configuration.setDictionaryPath("file:/home/marcuss/Desktop/software/sphinx4/sphinx4-5prealpha/models/acoustic/wsj/dict/cmudict.0.6d");
        //        //this is a text file dictionary with spelling and phonemes 
        //        configuration.setLanguageModelPath("/home/marcuss/Desktop/workspace_sphinx/test_sphinx/models/en-us.lm.dmp");

        StreamSpeechRecognizer recognizer = 
            new StreamSpeechRecognizer(configuration);
        
        String filenameString = "file:"+inputfile ;       
        filenameString = filenameString.substring(0,filenameString.length()-3)+"wav";
        System.out.println("filenameString: " + filenameString);
        recognizer.startRecognition(new URL(filenameString).openStream());
        //=== NEED TO CHECK ABOUT wav format: does it need to be 16 khz 16bit mono?

        SpeechResult result;
        
        String contextURL = "https://clowder.ncsa.illinois.edu/contexts/metadata.jsonld";
        
        ArrayList contextArray = new ArrayList();
        Map<String, Object> metadata = new HashMap<String, Object>();
        Map<String, Object> contextObject = new HashMap<String, Object>();
        Map<String, Object> phrases = new HashMap<String, Object>();
        Map<String, Object> phraseObject = new HashMap<String, Object>();
        Map<String, Object> attachedTo = new HashMap<String, Object>();
        Map<String, Object> agent = new HashMap<String, Object>();

        int numPhrases = 0;
        while ((result = recognizer.getResult()) != null) {       	
        	System.out.println("Processing Phrase " + numPhrases);
                   
            String phraseName = "phrase" + numPhrases;
			//metadata.put(phraseName, result.getNbest(1));
            phrases.put(phraseName, result.getNbest(1));
            numPhrases++;           
        }

        recognizer.stopRecognition();
        phraseObject.put("phrases", phrases);
        
        // Required fields for JSON_LD
        contextObject.put("phrases", "http://clowder.ncsa.illinois.edu/"+ extractorName + "#phrases");
        contextArray.add(contextURL);
        contextArray.add(contextObject);

        attachedTo.put("resourceType", "file");
        attachedTo.put("id", fileid);        
        
        agent.put("@type", "cat:extractor");
        agent.put("extractor_id", "https://clowder.ncsa.illinois.edu/clowder/api/extractors/" + extractorName);
        
        metadata.put("@context", contextArray);
        metadata.put("attachedTo", attachedTo);
        metadata.put("agent", agent);
        metadata.put("content", phraseObject);  

        // Gson gson = new GsonBuilder().create();
        // String metadataJson = gson.toJson(metadata);  
        
        System.out.println("Finished Processing");  
        System.out.println("Metadata: " + metadata);
        
        postMetaData(host, key, fileid, metadata);

        // clean up 
        if(inputfile.exists()){
            inputfile.delete();
        }

        
    }

/// POST METADATA TO MEDICI //////////////////////////////////////////////////////////////////////
    
    private String postMetaData(String host, String key, String fileid, Map<String, Object> metadata)
            throws IOException {
        
        //Deprecated API: URL url = new URL(host + "api/files/" + fileid + "/metadata?key=" + key);
        // New Json-ld Metadata API
        URL url = new URL(host + "api/files/" + fileid + "/metadata.jsonld?key=" + key);

        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "application/json");
        conn.setDoOutput(true);

        DataOutputStream wr = new DataOutputStream(conn.getOutputStream());
        mapper.writeValue(wr, metadata);
        wr.flush();
        wr.close();

        int responseCode = conn.getResponseCode();
        if (responseCode != 200) {
            throw (new IOException("Error uploading metadata [code=" + responseCode + "]"));
        }

        BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
        String inputLine;
        StringBuffer response = new StringBuffer();

        while ((inputLine = in.readLine()) != null) {
            response.append(inputLine);
        }
        in.close();

        return response.toString();
    }
}

