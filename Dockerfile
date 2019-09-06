FROM python:3
ENV PYTHONUNBUFFERED 1
ENV AWS_DEFAULT_REGION eu-west-1
ENV WEDDING_CONFIG docker
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/

