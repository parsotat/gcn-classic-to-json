import os
import sys

from gcn_kafka import Consumer

# Connect as a consumer.
# Warning: don't share the client secret with others.
consumer = Consumer(client_id=os.environ['CLIENT_ID'],
                    client_secret=os.environ['CLIENT_SECRET'])

# Subscribe to topics and receive alerts
consumer.subscribe(['igwn.gwalert'])
while True:
    for message in consumer.consume(timeout=1):
        if message.error():
            print(message.error(), file=sys.stderr)
            continue
        else:
            print('got message')
