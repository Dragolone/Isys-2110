import json
from pathlib import Path
from datetime import datetime, timedelta

from resource import Resource, log_resource_consumption
from alert import Alert


MISSION_FILE = Path("data/missions.json")


class Mission:
    def __init__(self, mission_id, name, description, planet_id, start_time, end_time, resources_used=None, status="draft"):
        self.mission_id = mission_id
        self.name = name
        self.description = description
        self.planet_id = planet_id
        self.start_time = start_time
        self.end_time = end_time
        self.resources_used = resources_used or {}  # dict {"ENERGY": 50, "DROIDS": 20}
        self.status = status

    def to_dict(self):
        return {
            "mission_id": self.mission_id,
            "name": self.name,
            "description": self.description,
            "planet_id": self.planet_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "resources_used": self.resources_used,
            "status": self.get_current_status()
        }

    def get_current_status(self):
        """
        Returns the current mission status.

        - draft: being created, not scheduled yet
        - planned: scheduled but not started
        - active: running now
        - completed: already ended
        - cancelled: manually cancelled, will not run
        """
        if self.status == "cancelled":
            return "cancelled"
        if self.status == "draft":
            return "draft"
        if self.status == "completed":
            return "completed"
        now = datetime.now()
        try:
            start = datetime.strptime(self.start_time, "%Y-%m-%d %H:%M")
            end = datetime.strptime(self.end_time, "%Y-%m-%d %H:%M")
        except ValueError:
            return self.status

        if start <= now <= end:
            return "active"
        elif now > end:
            return "completed"
        else:
            return "planned"

    @staticmethod
    def load_all():
        if not MISSION_FILE.exists():
            return []
        with open(MISSION_FILE, "r") as f:
            raw = json.load(f)
        return [Mission(**mission) for mission in raw]

    @staticmethod
    def save_all(missions):
        with open(MISSION_FILE, "w") as f:
            json.dump([mission.to_dict() for mission in missions], f, indent=2)

    @staticmethod
    def find_by_id(id):
        missions = Mission.load_all()
        for mission in missions:
            if mission.mission_id == id:
                return mission
        return None

    @staticmethod
    def delete_by_id(id):
        missions = Mission.load_all()
        deleted = None
        remaining = []
        for mission in missions:
            if mission.mission_id == id:
                deleted = mission
            else:
                remaining.append(mission)
        if deleted:
            Mission.save_all(remaining)
        return deleted

    @staticmethod
    def create_new(form):
        existing = Mission.load_all()
        existing_ids = [int(m.mission_id) for m in existing if m.mission_id.isdigit()]
        next_id = str(max(existing_ids, default=0) + 1)

        mission_id = next_id
        name = form.get("name", "Untitled Mission")
        description = form.get("description", "")
        planet_id = form.get("planet_id", "1")
        start_time = form.get("start_time", "").replace("T", " ")
        end_time = form.get("end_time", "").replace("T", " ")
        status = form.get("status", "draft")

        resources_used = {}

        return Mission(
            mission_id=mission_id,
            name=name,
            description=description,
            planet_id=planet_id,
            start_time=start_time,
            end_time=end_time,
            resources_used=resources_used,
            status=status
        )


def process_resource_for_mission(mission: "Mission"):
    """
    Apply or restore resources based on mission status.
    If resources are insufficient, rollback and alert.
    """
    resources = Resource.load_all()
    today = datetime.now().strftime("%Y-%m-%d")

    if mission.status == "active":
        for rtype, amount in mission.resources_used.items():
            r = next((res for res in resources if res.resource_type == rtype), None)
            if not r or r.available < amount:
                Alert.log_resource_alert(rtype, r.available if r else 0, amount)
                Alert("RESOURCE", f"{rtype} not enough for mission {mission.name}", "Critical").save()
                mission.status = "draft"
                return
            else:
                r.consume(amount)
                log_resource_consumption(rtype, amount, today)

    elif mission.status == "completed":
        for rtype, amount in mission.resources_used.items():
            r = next((res for res in resources if res.resource_type == rtype), None)
            if r:
                r.available += amount
                # log_resource_consumption(rtype, amount, today)

    Resource.save_all(resources)
    for r in resources:
        if r.is_low():
            Alert.log_resource_alert(r.resource_type, r.available, r.threshold)

def reset_missions():
    # Hard coded for testing
    if not MISSION_FILE.exists():
        now = datetime.now()
        demo_missions = []
        print(f"[INIT] MISSION_FILE not exists. Creating default data. Current TIME is {now}")

        for i in range(1, 6):  # 5 draft
            demo_missions.append(Mission(
                f"{i}", f"Draft Mission {i}", "Initial planning phase", "1",
                "", "", {"ENERGY": 0}, "draft"
            ))

        for i in range(6, 11):  # 5 planned (start in future)
            start = now + timedelta(days=i-5)
            end = start + timedelta(days=2)
            demo_missions.append(Mission(
                f"{i}", f"Planned Mission {i}", "Scheduled mission", "2",
                start.strftime("%Y-%m-%d %H:%M"),
                end.strftime("%Y-%m-%d %H:%M"),
                {"ENERGY": 200 + i*10}, "planned"
            ))

        for i in range(11, 12):  # 1 active (now in between)
            start = now - timedelta(hours=1)
            end = now + timedelta(minutes=2)
            demo_missions.append(Mission(
                f"{i}", f"Active Fast Mission {i}", "Running now, ending in 2 minutes", "3",
                start.strftime("%Y-%m-%d %H:%M"),
                end.strftime("%Y-%m-%d %H:%M"),
                {"DROIDS": 100}, "planned"
            ))

        for i in range(12, 14):  # 2 active (now in between)
            start = now - timedelta(hours=1)
            end = now + timedelta(hours=1)
            demo_missions.append(Mission(
                f"{i}", f"Active Mission {i}", "Running now", "3",
                start.strftime("%Y-%m-%d %H:%M"),
                end.strftime("%Y-%m-%d %H:%M"),
                {"DROIDS": 100}, "planned"
            ))

        for i in range(14, 18):  # 4 completed (already ended)
            start = now - timedelta(days=i-13)
            end = start + timedelta(hours=4)
            demo_missions.append(Mission(
                f"{i}", f"Completed Mission {i}", "Finished", "2",
                start.strftime("%Y-%m-%d %H:%M"),
                end.strftime("%Y-%m-%d %H:%M"),
                {"FACILITIES": 1}, "planned"
            ))

        for i in range(18, 21):  # 3 cancelled
            start = now + timedelta(days=1)
            end = start + timedelta(days=2)
            demo_missions.append(Mission(
                f"{i}", f"Cancelled Mission {i}", "Aborted", "3",
                start.strftime("%Y-%m-%d %H:%M"),
                end.strftime("%Y-%m-%d %H:%M"),
                {"ENERGY": 300}, "cancelled"
            ))

        Mission.save_all(demo_missions)