# gcn-monitor

A Kafka client instrumented with Prometheus.

## Configuration

The following environment variables may be used to configure the service:

| Name                 | Value                                                                              |
| -------------------- | ---------------------------------------------------------------------------------- |
| `KAFKA_*`            | Kafka client configuration as understood by [Confluent Platform docker containers] |

[Confluent Platform docker containers]: https://docs.confluent.io/platform/current/installation/docker/config-reference.html
