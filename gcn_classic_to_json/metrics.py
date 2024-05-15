#
# Copyright © 2023 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
"""Prometheus metrics."""
import prometheus_client

received = prometheus_client.Counter(
    "received",
    "Kafka messages received",
    labelnames=["topic", "partition"],
    namespace=__package__,
)

delivered = prometheus_client.Counter(
    "delivered",
    "Kafka messages delivered",
    labelnames=["topic", "partition", "successful"],
    namespace=__package__,
)
