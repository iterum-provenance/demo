FROM python:3.8

RUN mkdir /app/
WORKDIR /app/

ADD requirements.txt .

RUN pip3 install -r requirements.txt

ADD *.py ./
RUN rm -f *_test.py

CMD python3 main.py
