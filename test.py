import json
import logging
import os
import urllib

import click
import prometheus_client
from gcn_kafka import Consumer

log = logging.getLogger(__name__)


broker_state = prometheus_client.Enum(
    'state',
    'Kafka broker state (see https://github.com/confluentinc/librdkafka/blob/master/STATISTICS.md)',
    states=[
        # from https://github.com/confluentinc/librdkafka/blob/v2.2.0/src/rdkafka_broker.c#L83
        'INIT',
        'DOWN',
        'TRY_CONNECT',
        'CONNECT',
        'SSL_HANDSHAKE',
        'AUTH_LEGACY',
        'UP',
        'UPDATE',
        'APIVERSION_QUERY',
        'AUTH_HANDSHAKE',
        'AUTH_REQ',
    ],
    namespace='kafka',
    subsystem='broker',
    labelnames=['name']
)


def stats_cb(data):
    stats = json.loads(data)
    for broker in stats['brokers'].values():
        broker_state.labels(broker['name']).state(broker['state'])


def get_client_kwargs(interval_seconds=1.0):
    return {'statistics.interval.ms': 1e3 * interval_seconds,
            'stats_cb': stats_cb}


def host_port(host_port_str):
    # Parse netloc like it is done for HTTP URLs.
    # This ensures that we will get the correct behavior for hostname:port
    # splitting even for IPv6 addresses.
    return urllib.parse.urlparse(f'http://{host_port_str}')


@click.command()
@click.option(
    '--prometheus', type=host_port, default=':8000', show_default=True,
    help='Hostname and port to listen on for Prometheus metric reporting')
@click.option(
    '--loglevel', type=click.Choice(logging._levelToName.values()),
    default='DEBUG', show_default=True, help='Log level')
def test(prometheus, loglevel):
    logging.basicConfig(level=loglevel)

    prometheus_client.start_http_server(prometheus.port,
                                        prometheus.hostname or '0.0.0.0')
    log.info('Prometheus listening on %s', prometheus.netloc)

    # Connect as a consumer.
    # Warning: don't share the client secret with others.
    log.info('Creating consumer')
    consumer = Consumer(client_id=os.environ['GCN_CLIENT_ID'],
                        client_secret=os.environ['GCN_CLIENT_SECRET'],
                        domain=os.environ.get('GCN_DOMAIN'),
                        **get_client_kwargs())

    # Subscribe to topics and receive alerts
    log.info('Subscribing')
    topics = list(consumer.list_topics().topics.keys())
    consumer.subscribe(topics)

    log.info('Entering consume loop')
    while True:
        for message in consumer.consume(timeout=1):
            if error := message.error():
                log.error('got error %s', error)
            else:
                log.info('got message')


if __name__ == '__main__':
    test()
