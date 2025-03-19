#Dockerfile for Streamlit App

FROM python:3.10

RUN pip install --upgrade pip

EXPOSE 8080

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir -r  requirements.txt 

CMD streamlit run app.py