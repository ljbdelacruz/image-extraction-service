import os
from confluent_kafka import Consumer, KafkaError
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from src.service.request_service import create_request

def consume_messages(topic):
    bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    conf = {
        'bootstrap.servers': bootstrap_servers,
        'group.id': "mygroup",
        'auto.offset.reset': 'earliest'
    }
    consumer = Consumer(**conf)
    consumer.subscribe([topic])

    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(msg.error())
                break

        message = json.loads(msg.value().decode('utf-8'))
        print(f"Received message: {message}")
        create_request(custom_id=message['key'], base_image=message['value'])

    consumer.close()