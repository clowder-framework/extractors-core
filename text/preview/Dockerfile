FROM python:3.8

WORKDIR /extractor
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY text_preview_extractor.py extractor_info.json ./
CMD python text_preview_extractor.py