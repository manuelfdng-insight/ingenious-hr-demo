# Dockerfile for Streamlit App with Azure Storage Support

FROM python:3.10

RUN pip install --upgrade pip

EXPOSE 8080

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt 

# Set environment variable to ensure streamlit runs correctly in Docker
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

CMD streamlit run app.py