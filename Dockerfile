FROM python:3

ADD control/controller.py /
COPY requirements.txt /

RUN pip install -r requirements.txt

CMD [ "python", "./controller.py" ]
