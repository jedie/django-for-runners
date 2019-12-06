FROM python:3.6.0-slim

ARG work_dir=/src

# Install git
RUN apt-get update && apt-get install -y git

RUN mkdir ${work_dir}

WORKDIR ${work_dir}

COPY . ${work_dir}

RUN pip install -r requirements/base.txt
ENV PYTHONPATH=${work_dir}
