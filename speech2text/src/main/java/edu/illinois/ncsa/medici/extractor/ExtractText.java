package edu.illinois.ncsa.medici.extractor;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

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
    private static String rabbitmqhost = "localhost";

    // name to show in rabbitmq queue list
    private static String exchange = "medici";

    // name to show in rabbitmq queue list
    private static String extractorName = "audio2text";

    // username and password to connect to rabbitmq
    private static String username = null;
    private static String password = null;

    // accept any type of file that is audio
    private static String messageType = "*.file.audio.#";
    // ----------------------------------------------------------------------
    // END CONFIGURATION
    // ----------------------------------------------------------------------

    DateFormat dateformat = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSXXX");
    ObjectMapper mapper = new ObjectMapper();


/// MAIN /////////////////////////////////////////////////////////////////////    
    
    public static void main(String[] argv) throws Exception {
        // setup connection parameters
        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost(rabbitmqhost);
        if ((username != null) && (password != null)) {
            factory.setUsername(username);
            factory.setPassword(password);
        }

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
        URL metadataUrl = new URL(host + "api/files/" + intermediatefileid + "/metadata");
        
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
			
		File outputFile = inputFile; //TODO: is it ok to leave this as default and only change if needed
		
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
		if(fileType.equals("mp3")){
			System.out.println("Converting mp3 to wav");			
			String outputFileName = "/tmp/outfile.wav";
			String convertCmd = "ffmpeg -i " + inputFile + " -acodec pcm_s16le -ar 16000 " + outputFileName;
	        Process convertOut = Runtime.getRuntime().exec(convertCmd);
	        outputFile = new File(outputFileName);
		}
		else if(fileType.equals("wav")){	//===NO CONVERTION
			System.out.println("Converting wav to wav");
			String outputFileName = "/tmp/outfile.wav";
			String convertCmd = "ffmpeg -i " + inputFile + " -acodec pcm_s16le -ar 16000 " + outputFileName;
	        Process convertOut = Runtime.getRuntime().exec(convertCmd);
	        outputFile = new File(outputFileName);
		}
		else{
			System.out.println("Unsupported File Type" + fileType);
			outputFile = inputFile;
		}
				             
        System.out.println("Output File: " + outputFile);
        
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
	configuration.setLanguageModelPath("resource:/edu/cmu/sphinx/models/en-us/en-us.lm.dmp");

//        configuration.setAcousticModelPath("resource:/WSJ_8gau_13dCep_16k_40mel_130Hz_6800Hz"); 
//	configuration.setAcousticModelPath("resource:/edu/cmu/sphinx/models/acoustic/wsj/WSJ_8gau_13dCep_16k_40mel_130Hz_6800Hz");
//        configuration.setAcousticModelPath("resource:/WSJ_8gau_13dCep_8kHz_31mel_200Hz_3500Hz");        
//       configuration.setDictionaryPath("resource:/WSJ_8gau_13dCep_16k_40mel_130Hz_6800Hz/dict/cmudict.0.6d");
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
        
//        tried running bush_god_bless.wav after       
//        ffmpeg -i bush_god_bless.wav -acodec pcm_s16le -ac 1 -ar 16000 out.wav       
//        it takes time, where the running with the un-converted does not
//        original:  Metadata: {} 
//        converted: outputs "processing phrase1" and Metadata: {phrase0=[]}
//		 works!, but poor accuracy ffmpeg -i 903708.mp3 -acodec pcm_s16le -ar 16000 out7.wav

        SpeechResult result;
        
        Map<String, Object> metadata = new HashMap<String, Object>();
        int numPhrases = 0;
        while ((result = recognizer.getResult()) != null) {       	
        	System.out.println("Processing Phrase " + numPhrases);
                   
            String phraseName = "phrase" + numPhrases;
			metadata.put(phraseName, result.getNbest(1));
			numPhrases++;           
        }

        recognizer.stopRecognition();
            
        System.out.println("Finished Processing");  
        System.out.println("Metadata: " + metadata);
        
        postMetaData(host, key, fileid, metadata);
    }

/// POST METADATA TO MEDICI //////////////////////////////////////////////////////////////////////
    
    private String postMetaData(String host, String key, String fileid, Map<String, Object> metadata)
            throws IOException {
        URL url = new URL(host + "api/files/" + fileid + "/metadata?key=" + key);

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


//System.out.format("Hypothesis: %s\n",
//result.getHypothesis());                             
//System.out.println("List of recognized words and their times:");
//for (WordResult r : result.getWords()) {
//System.out.println(r);
//}
//System.out.println("Best 3 hypothesis:");            
//for (String s : result.getNbest(3))
//System.out.println(s);
//System.out.println("Lattice contains " + result.getLattice().getNodes().size() + " nodes");
