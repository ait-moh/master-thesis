from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
import pandas as pd
import json
import time
import uuid

# Load your historical CSV
csv_file = "df_scaled.csv"
df = pd.read_csv(csv_file)

# Kafka connection with retry logic
def connect_kafka():
    while True:
        try:
            producer = KafkaProducer(
                bootstrap_servers=['localhost:9092'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            print("✅ Kafka is ready!")
            return producer
        except NoBrokersAvailable:
            print("⏳ Kafka not ready yet. Retrying in 3 seconds...")
            time.sleep(3)

producer = connect_kafka()

#topic = 'pfe'  # Same topic as your consumer!
topic = 'pfe'

# Batch configuration
batch_size = 100  # number of rows in each batch
num_batches = 3   # total number of batches to send

# Iterate and send batches
for batch_num in range(num_batches):
    start_idx = batch_num * batch_size
    end_idx = start_idx + batch_size

    batch = df.iloc[start_idx:end_idx]

    # Prepare batch as a list of dicts
    batch_message = {"batch": batch.values.tolist()}

    # Send batch
    producer.send(topic, value=batch_message)
    print(f"✅ Sent batch {batch_num + 1}: rows {start_idx} to {end_idx}")

    # Optional delay to simulate real-time
    time.sleep(3)

producer.flush()
producer.close()
print("✅ Finished sending all batches.")
