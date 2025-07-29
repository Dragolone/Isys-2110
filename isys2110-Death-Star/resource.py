import json
from datetime import datetime
from pathlib import Path

RESOURCE_FILE = Path("data/resources.json")
RESOURCE_LOG_FILE = Path("data/resource_log.json")

class Resource:
    def __init__(self, resource_type, available, threshold):
        self.resource_type = resource_type
        self.available = available
        self.threshold = threshold

    def is_low(self):
        return self.available < self.threshold

    def consume(self, amount):
        self.available -= amount
        if self.available < 0:
            self.available = 0

    def to_dict(self):
        return {
            "type": self.resource_type,
            "available": self.available,
            "threshold": self.threshold
        }

    @staticmethod
    def load_all():
        reset_resources()   # If no resources files, generate new default data
        with open(RESOURCE_FILE, "r") as f:
            raw = json.load(f)
        return [Resource(r["type"], r["available"], r["threshold"]) for r in raw]

    @staticmethod
    def save_all(resources):
        with open(RESOURCE_FILE, "w") as f:
            json.dump([resource.to_dict() for resource in resources], f, indent=2)


def log_resource_consumption(resource_type, amount, date_str=None):
    date_str = date_str or datetime.now().strftime("%Y-%m-%d")

    if not RESOURCE_LOG_FILE.exists():
        logs = []
    else:
        with open(RESOURCE_LOG_FILE, "r") as f:
            logs = json.load(f)

    updated = False
    for entry in logs:
        if entry["date"] == date_str:
            entry[resource_type] = entry.get(resource_type, 0) + amount
            updated = True
            break

    if not updated:
        logs.append({"date": date_str, resource_type: amount})

    with open(RESOURCE_LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

def reset_resources():
    # Hard coded for testing
    if not RESOURCE_FILE.exists():
        sample_resources = [
            {"type": "ENERGY", "available": 5500, "threshold": 2000},
            {"type": "DROIDS", "available": 500, "threshold": 400},
            {"type": "FACILITIES", "available": 1500, "threshold": 500}
        ]
        with open(RESOURCE_FILE, "w") as f:
            json.dump(sample_resources, f, indent=2)

    # Hard coded for testing
    if not RESOURCE_LOG_FILE.exists():
        sample_logs = [
            {"date": "2025-05-01", "ENERGY": 1200, "DROIDS": 400, "FACILITIES": 200},
            {"date": "2025-05-02", "ENERGY": 800, "DROIDS": 300, "FACILITIES": 150},
            {"date": "2025-05-21", "ENERGY": 0, "DROIDS": 200, "FACILITIES": 0}
        ]
        with open(RESOURCE_LOG_FILE, "w") as f:
            json.dump(sample_logs, f, indent=2)