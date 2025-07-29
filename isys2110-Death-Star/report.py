import json
from mission import Mission
from resource import Resource, RESOURCE_LOG_FILE

def load_mission_data():
    return Mission.load_all()

def load_current_resources():
    return Resource.load_all()

def load_resource_logs():
    if not RESOURCE_LOG_FILE.exists():
        return []
    with open(RESOURCE_LOG_FILE, 'r') as f:
        return json.load(f)