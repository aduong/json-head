FROM python:3.5
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8006
CMD ["python", "json_head.py"]
