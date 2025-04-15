from kafka import KafkaConsumer
import json
import numpy as np
import uuid  # ✅ Added for random consumer group ID

def consume_messages():
    # ✅ Create consumer with random group id (fresh read every time)
    consumer = KafkaConsumer(
        'pfe',
        bootstrap_servers=['localhost:9092'],
        group_id=str(uuid.uuid4()),  # Random group ID ensures full topic read
        auto_offset_reset='earliest',
        enable_auto_commit=False,
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        consumer_timeout_ms=5000
    )

    print("⏳ Kafka consumer started, waiting for data...")
    data = []

    for message in consumer:
        batch_data = message.value.get("batch", [])
        print(f"✅ Consumed: {len(batch_data)} rows")
        data.extend(batch_data)

    print(f"📊 Total data collected from Kafka: {len(data)} rows")
    consumer.close()  # Important: close after consuming

    return np.array(data, dtype=np.float32)
