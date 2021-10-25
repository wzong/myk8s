# To rebuild:
# sudo docker build -f test_k8s_storage.Dockerfile -t wzong/test-k8s-storage .
# sudo docker push wzong/test-k8s-storage:latest
FROM python:3.7.8-alpine

RUN mkdir -p /usr/src
WORKDIR /usr/src
COPY . /usr/src

CMD python3 test_k8s_storage.py
