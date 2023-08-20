import os
import sys

from gcn_kafka import Consumer

# Connect as a consumer.
# Warning: don't share the client secret with others.
print('Creating consumer')
consumer = Consumer(client_id=os.environ['GCN_CLIENT_ID'],
                    client_secret=os.environ['GCN_CLIENT_SECRET'],
                    domain=os.environ.get('GCN_DOMAIN'))

# Subscribe to topics and receive alerts
print('Subscribing')
consumer.subscribe(['igwn.gwalert'])

print('Entering consume loop')
while True:
    for message in consumer.consume(timeout=1):
        if message.error():
            print(message.error(), file=sys.stderr)
            continue
        else:
            print('got message')
