import json
import os

from kafka import KafkaConsumer, KafkaProducer

kafka_bootstrap = os.getenv("KAFKA_BOOTSTRAP")


def get_kafka_producer():
    kafka_producer = KafkaProducer(
        bootstrap_servers=kafka_bootstrap,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        retries=5,
        acks="all",
    )
    return kafka_producer


def get_kafka_consumer():
    kafka_consumer = KafkaConsumer(
        "reservations",
        bootstrap_servers=kafka_bootstrap,
        auto_offset_reset="earliest",
        group_id="audit_service_group", 
        enable_auto_commit=True, 
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )
    return kafka_consumer
