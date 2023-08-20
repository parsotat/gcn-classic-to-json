FROM python:slim
RUN pip install --no-cache-dir gcn-kafka
COPY test.py /
CMD ["python", "/test.py"]
USER nobody:nogroup
