
FROM python:3.10
WORKDIR /app
COPY order_service.py requirements.txt ./
RUN pip install -r requirements.txt
CMD ["python", "order_service.py"]
