FROM --platform=linux/amd64 python:3.8
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y gfortran ffmpeg libsm6 libxext6 libgl1-mesa-glx

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . /usr/src/app
RUN  pip3 install numpy
RUN  pip3 install -r requirements.txt
ENV FLASK_APP=wsgi.py
ENV FLASK_RUN_HOST=0.0.0.0
CMD ["python", "-m", "flask", "run"]