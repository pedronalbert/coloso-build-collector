FROM python:3-onbuild
RUN mkdir /app
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD sleep 5 && python ./init.py
