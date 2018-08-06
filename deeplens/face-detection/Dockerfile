FROM mxnet/python

RUN apt-get -y update
RUN apt-get install -y --fix-missing \
    build-essential \
    cmake \
    libopencv-dev python-opencv libgtk2.0-dev \
    && apt-get clean && rm -rf /tmp/* /var/tmp/*

COPY requirements.txt /opt/app/requirements.txt
WORKDIR /opt/app
RUN pip install -r requirements.txt
RUN pip install Flask

COPY face-detection/score.py /opt/app/face-detection/score.py
COPY app.py /opt/app/api.py

ENTRYPOINT ["python"]
CMD ["api.py"]
