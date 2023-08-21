FROM python:slim
RUN pip install --no-cache-dir click gcn-kafka prometheus-client
COPY test.py /
CMD ["python", "/test.py"]
USER nobody:nogroup
