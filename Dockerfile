FROM python:latest
COPY . /app/server
WORKDIR /app/server
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update -y
RUN apt install libgl1-mesa-glx -y
RUN apt-get install 'ffmpeg'\
    'libsm6'\
    'libxext6' -y
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python", "flask_server.py"]

