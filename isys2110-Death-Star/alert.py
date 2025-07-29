import json
from datetime import datetime
from pathlib import Path

ALERT_FILE = Path("data/alerts.json")

class Alert:
    def __init__(self, alert_type, content, level, time=None, status="Unresolved"):
        self.alert_type = alert_type
        self.content = content
        self.level = level      # Critical, High, Medium, Low
        self.time = time or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status = status    # Resolved, Unresolved

    def to_dict(self):
        return {
            "alert_type": self.alert_type,
            "content": self.content,
            "level": self.level,
            "time": self.time,
            "status": self.status
        }

    @staticmethod
    def load_all():
        if not ALERT_FILE.exists():
            return []
        with open(ALERT_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return []
            return [Alert(**alert) for alert in json.loads(content)]

    @staticmethod
    def save_all(alerts):
        with open(ALERT_FILE, "w") as f:
            json.dump([alert.to_dict() for alert in alerts], f, indent=2)

    @staticmethod
    def log_resource_alert(resource_type, available, threshold):
        content = f"{resource_type} is below threshold! ({available} < {threshold})"
        level = "Critical" if available == 0 else "High"

        alerts = Alert.load_all()

        for a in alerts:
            if (
                    a.alert_type == "RESOURCE"
                    and a.status == "Unresolved"
                    and a.content == content
            ):
                return  # Skip same alert

        new_alert = Alert("RESOURCE", content, level)
        alerts.append(new_alert)
        Alert.save_all(alerts)

def reset_alerts():
    # Hard coded for testing
    if not ALERT_FILE.exists():
        sample_alerts = [
            {
                "alert_type": "RESOURCE",
                "content": "DROIDS is below threshold!(Created by default) (300 < 400)",
                "level": "High",
                "time": "2025-05-20 14:00:00",
                "status": "Unresolved"
            },
            {
                "alert_type": "MAINTENANCE",
                "content": "Hangar 3 requires urgent structural reinforcement.",
                "level": "Critical",
                "time": "2025-05-18 10:15:00",
                "status": "Unresolved"
            },
            {
                "alert_type": "SECURITY",
                "content": "Perimeter breach detected near Outpost Beta.",
                "level": "High",
                "time": "2025-05-19 03:45:00",
                "status": "Unresolved"
            },
            {
                "alert_type": "TECHNICAL",
                "content": "Shield generator unit #4 is overheating intermittently.",
                "level": "Medium",
                "time": "2025-05-17 18:30:00",
                "status": "Unresolved"
            },
            {
                "alert_type": "INFRASTRUCTURE",
                "content": "Hydro-core coolant reserves at 20%, resupply required.",
                "level": "Low",
                "time": "2025-05-16 08:20:00",
                "status": "Unresolved"
            }
        ]
        with open(ALERT_FILE, "w") as f:
            json.dump(sample_alerts, f, indent=2)