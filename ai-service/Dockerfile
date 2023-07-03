FROM public.ecr.aws/genophore/nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

RUN apt update -y && \
    apt install python3 python3-pip -y

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
CMD [ "python3", "-u","falcon7b.py" ]