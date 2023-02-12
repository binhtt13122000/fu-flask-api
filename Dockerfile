FROM python:3.8

COPY requirements.txt /opt/
RUN pip3 install -r /opt/requirements.txt

WORKDIR /opt
COPY . .

ENV FLASK_DEBUG=1
ENV FLASK_APP=src
ENV JWT_SECRET_KEY='JWT_SECRET_KEY'

CMD  ["flask", "run", "--host", "0.0.0.0", "--port", "5000"]