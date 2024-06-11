#
# Copyright © 2023 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
"""Convert GCN Classic notices to JSON."""
import json
import logging

import gcn_kafka

from . import metrics
from . import notices

log = logging.getLogger(__name__)


def kafka_delivered_cb(err, msg):
    successful = not err
    metrics.delivered.labels(msg.topic(), msg.partition(), successful).inc()


def run():
    binary_topic_prefix = "gcn.classic.binary."
    json_topic_prefix = "gcn.classic.json."

    log.info("Creating consumer")
    config = gcn_kafka.config_from_env()
    consumer = gcn_kafka.Consumer(config)

    log.info("Creating producer")
    config["client.id"] = __package__
    config["on_delivery"] = kafka_delivered_cb
    producer = gcn_kafka.Producer(config)

    log.info("Subscribing")
    consumer.subscribe([binary_topic_prefix + key for key in notices.keys])

    log.info("Entering consume loop")
    while True:
        for message in consumer.consume(timeout=1):
            topic = message.topic()
            if error := message.error():
                log.error("topic %s: got error %s", topic, error)
            else:
                log.info("topic %s: got message", topic)
                key = topic[len(binary_topic_prefix) :]
                result = notices.parse(key, message.value())
                json_data = json.dumps(result)
                producer.produce(json_topic_prefix + key, json_data)
