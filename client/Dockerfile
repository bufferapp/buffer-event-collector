FROM grpc/python:1.4

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY client.py /usr/src/app/client.py

WORKDIR /usr/src/app

CMD ["python", "client.py"]
