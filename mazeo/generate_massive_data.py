
import json
import csv
import random
import uuid
from datetime import datetime, timedelta

def generate_database(num_entries=100000):
    first_names = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda", "William", "Elizabeth", 
                   "Ahmed", "Fatima", "Mazen", "Sarah", "Omar", "Layla", "Youssef", "Nour", "Ali", "Hana"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Saber", "Mansour", "Hassan", "Zaid", "Kassab",
                  "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson"]
    cities = ["Cairo", "New York", "London", "Tokyo", "Paris", "Dubai", "Riyadh", "Berlin", "Madrid", "Rome"]
    countries = ["Egypt", "USA", "UK", "Japan", "France", "UAE", "Saudi Arabia", "Germany", "Spain", "Italy"]
    interests = ["Coding", "Music", "Travel", "History", "Physics", "Math", "AI", "Gaming", "Reading", "Sports"]
    activities = [
        "Logged in from a new device",
        "Completed a math challenge",
        "Browsed historical archives",
        "Updated profile preferences",
        "Sent a message to a mentor",
        "Accessed the geography module",
        "Generated an AI image",
        "Ran a deep learning simulation"
    ]

    data = []
    ids = [str(uuid.uuid4())[:8] for _ in range(num_entries)]
    
    print(f"Generating {num_entries} entries...")

    for i in range(num_entries):
        first = random.choice(first_names)
        last = random.choice(last_names)
        name = f"{first} {last}"
        age = random.randint(18, 85)
        
        # Inject realistic anomalies
        is_anomaly = random.random() < 0.05
        if is_anomaly:
            anomaly_type = random.choice(["Extreme Age", "Mismatched Location", "High Frequency Activity"])
            if anomaly_type == "Extreme Age":
                age = random.choice([3, 115, 150])
            activity = f"ANOMALY DETECTED: {anomaly_type}"
        else:
            anomaly_type = None
            activity = random.choice(activities)

        entry = {
            "ID": ids[i],
            "Name": name,
            "Age": age,
            "Location": f"{random.choice(cities)}, {random.choice(countries)}",
            "Email": f"{first.lower()}.{last.lower()}.{ids[i]}@mazeo-training.ai",
            "Preferences": random.sample(interests, k=random.randint(2, 5)),
            "Timestamp": (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat(),
            "Activity": activity,
            "Status": random.random() > 0.1,
            "Relationships": random.sample(ids, k=random.randint(0, 3)),
            "Anomalies": anomaly_type
        }
        data.append(entry)
        
        if i % 20000 == 0 and i > 0:
            print(f"Progress: {i}/{num_entries}...")

    # Export to JSON
    print("Saving to training_data.json...")
    with open("training_data.json", "w") as f:
        json.dump(data, f, indent=2)

    # Export to CSV
    print("Saving to training_data.csv...")
    keys = data[0].keys()
    with open("training_data.csv", "w", newline='', encoding='utf-8') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

    print("Success! Database generated and exported.")

if __name__ == "__main__":
    generate_database(100000)
