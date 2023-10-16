FROM python:latest

ADD ./requirements.txt .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

ADD ./src .

CMD ["python3", "src/main.py"] 