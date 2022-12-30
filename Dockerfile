FROM python:alpine

ADD ./requirements.txt .

RUN pip install -r requirements.txt

ADD ./src/ .

CMD ["python3", "main.py"] 