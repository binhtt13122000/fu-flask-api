FROM python:3.8

COPY requirements.txt /opt/
RUN pip install --upgrade pip
RUN pip install -r /opt/requirements.txt
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y


WORKDIR /opt
COPY . .

ENV FLASK_DEBUG=1
ENV FLASK_APP=src
ENV JWT_SECRET_KEY='JWT_SECRET_KEY'

CMD  ["flask", "run", "--host", "0.0.0.0", "--port", "5000"]