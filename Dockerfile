FROM python:3.9

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

CMD ["python", "your_main_script.py"]
