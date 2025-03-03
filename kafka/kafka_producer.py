from confluent_kafka import Producer
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def produce_message(topic, message):
    # Get the Kafka bootstrap servers from environment variables
    bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    conf = {'bootstrap.servers': bootstrap_servers}
    producer = Producer(**conf)
    producer.produce(topic, key=str(message['key']), value=json.dumps(message), callback=delivery_report)
    producer.flush()