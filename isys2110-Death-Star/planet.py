import json
from pathlib import Path

PLANET_FILE = Path("data/planets.json")

class Planet:
    def __init__(self, planet_id, name, x, y, rebel_score, threat, status):
        self.planet_id = planet_id
        self.name = name
        self.coord_x = x
        self.coord_y = y
        self.rebel_score = rebel_score  # int
        self.threat = threat  # LOW, MEDIUM, HIGH
        self.status = status  # ACTIVE, DORMANT, HIGH_RISK

    def to_dict(self):
        return {
            "planet_id": self.planet_id,
            "name": self.name,
            "x": self.coord_x,
            "y": self.coord_y,
            "rebel_score": self.rebel_score,
            "threat": self.threat,
            "status": self.status
        }

    @staticmethod
    def load_all():
        reset_planets()     # If no plants file, generate new default data
        with open(PLANET_FILE, "r") as f:
            raw = json.load(f)
        return [Planet(**p) for p in raw]

    @staticmethod
    def save_all(planets):
        with open(PLANET_FILE, "w") as f:
            json.dump([planet.to_dict() for planet in planets], f, indent=2)

    @staticmethod
    def find_by_id(id):
        planets = Planet.load_all()
        for planet in planets:
            if planet.planet_id == id:
                return planet
        return None

    @staticmethod
    def delete_by_id(id):
        planets = Planet.load_all()
        remaining = [planet for planet in planets if planet.planet_id != id]
        deleted = next((planet for planet in planets if planet.planet_id == id), None)
        if deleted:
            Planet.save_all(remaining)
        return deleted

    @staticmethod
    def update_planet(pid, form_data):
        planets = Planet.load_all()
        updated = False
        for p in planets:
            if p.planet_id == pid:
                p.name = form_data["name"]
                p.coord_x = int(form_data["x"])
                p.coord_y = int(form_data["y"])
                p.rebel_score = int(form_data["rebel_score"])
                p.threat = form_data["threat"]
                p.status = form_data["status"]
                updated = True
                break
        if updated:
            Planet.save_all(planets)
        return updated

    @staticmethod
    def create_new(form_data):
        required_fields = ["planet_id", "name", "x", "y", "rebel_score", "threat", "status"]
        missing = [field for field in required_fields if not form_data.get(field)]
        if missing:
            raise ValueError(f"Missing fields: {', '.join(missing)}")

        try:
            x = int(form_data["x"])
            y = int(form_data["y"])
            rebel_score = int(form_data["rebel_score"])
        except ValueError:
            raise ValueError("X, Y and Rebel Score must be integers.")

        new = Planet(
            planet_id=form_data["planet_id"],
            name=form_data["name"],
            x=x,
            y=y,
            rebel_score=rebel_score,
            threat=form_data["threat"],
            status=form_data["status"]
        )

        planets = Planet.load_all()
        planets.append(new)
        Planet.save_all(planets)
        return new

def reset_planets():
    # Hard coded for testing
    if not PLANET_FILE.exists():
        demo_planets = [
            Planet("0", "Imperial Base", 960, 540, 0, "BASE", "default"),
            Planet("1", "Big Earth", 1200, 200, 10, "HIGH", "HIGH_RISK"),
            Planet("2", "Big Mars", 1500, 750, 5, "MEDIUM", "ACTIVE"),
            Planet("3", "Small Moon", 400, 900, 3, "LOW", "DORMANT"),
            Planet("4", "Maga Sydney", 200, 600, 1, "LOW", "DORMANT")
        ]
        Planet.save_all(demo_planets)
