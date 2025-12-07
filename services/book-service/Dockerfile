
FROM python:3.10
WORKDIR /app
COPY book_service.py requirements.txt ./
RUN pip install -r requirements.txt
CMD ["python", "book_service.py"]
