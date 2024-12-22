import random
import requests

NUM_LABELS = 3


def generate_set(size):
    dataset = {
        "features": [],
        "labels": []
    }
    for i in range(size):
        t = i % NUM_LABELS
        row = {
            "median_longitude": random.random() * float(t + 1) * 0.3 / float(NUM_LABELS),
            "median_latitude": random.random() * float(t + 1) * 0.9 / float(NUM_LABELS),
            "mean_diff_time": random.random() * float(t + 1) * 0.5 / float(NUM_LABELS),
            "mean_diff_amount": random.random() * float(t + 1) / float(NUM_LABELS),
            "median_targetIP": random.random() * float(t + 1) * random.random() / float(NUM_LABELS),
            "median_destIP": random.random() * float(t + 1) * 0.8 / float(NUM_LABELS)
        }
        dataset["features"].append(row)
        dataset["labels"].append(t)

    return dataset


if __name__ == "__main__":
    learning_sets = {
        "training_set":     generate_set(600),
        "validation_set":   generate_set(150),
        "test_set":         generate_set(250)
    }

    url = "http://192.168.97.185:5001"
    requests.post(url, json=learning_sets)
