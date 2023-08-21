# syntax=docker/dockerfile:1
   
FROM python:3.8-bookworm
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "src/api_server.py"]
EXPOSE 5000
