import datetime
import os
import sys

from gcn_kafka import Consumer

# Connect as a consumer.
# Warning: don't share the client secret with others.
print('Creating consumer', file=sys.stderr)
consumer = Consumer(client_id=os.environ['GCN_CLIENT_ID'],
                    client_secret=os.environ['GCN_CLIENT_SECRET'],
                    domain=os.environ.get('GCN_DOMAIN'))

# Subscribe to topics and receive alerts
print('Subscribing', file=sys.stderr)
consumer.subscribe(['igwn.gwalert'])

print('Entering consume loop', file=sys.stderr)
while True:
    for message in consumer.consume(timeout=1):
        now = datetime.datetime.utcnow().isoformat()
        if message.error():
            print(now, message.error(), file=sys.stderr)
        else:
            print(now, 'got message', file=sys.stderr)
