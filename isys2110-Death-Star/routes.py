import json
from datetime import datetime
from flask import render_template, session, redirect, url_for, request, flash, jsonify, Response
from planet import Planet, reset_planets
from mission import Mission, process_resource_for_mission, reset_missions
from alert import Alert, reset_alerts
from report import load_mission_data, load_current_resources, load_resource_logs
from resource import reset_resources, Resource


def register_routes(app):

    @app.route("/")
    def index():
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        # Get resource data
        resources = Resource.load_all()
        resources_dict = [r.to_dict() for r in resources]

        # Get mission data
        missions = Mission.load_all()
        missions_dict = [m.to_dict() for m in missions]
        mission_data = {
            'active': len([m for m in missions if m.status == 'active']),
            'planned': len([m for m in missions if m.status == 'planned']),
            'completed': len([m for m in missions if m.status == 'completed']),
            'cancelled': len([m for m in missions if m.status == 'cancelled'])
        }

        # Get alert data (last 7 days)
        alerts = Alert.load_all()
        alert_data = [0] * 7  # Initialize with zeros for the last 7 days
        today = datetime.now()
        for alert in alerts:
            alert_date = datetime.fromisoformat(alert.time)
            days_ago = (today - alert_date).days
            if 0 <= days_ago < 7:
                alert_data[days_ago] += 1

        return render_template(
            "dashboard.html",
            mission_data=mission_data,
            alert_data=alert_data,
            missions=missions_dict,
            resources=resources_dict,
            is_admin=session.get("logged_in", False)
        )

    # Settings Page
    @app.route("/settings")
    def settings():
        return render_template("settings.html", resources=Resource.load_all())

    @app.route("/update_resources", methods=["POST"])
    def update_resources():
        resources = Resource.load_all()

        for r in resources:
            try:
                available = int(request.form.get(f"available_{r.resource_type}", r.available))
                threshold = int(request.form.get(f"threshold_{r.resource_type}", r.threshold))
                r.available = max(0, available)
                r.threshold = max(0, threshold)
            except ValueError:
                flash(f"Invalid value for {r.resource_type}. Must be a positive integer.", "danger")
                return redirect(url_for("settings"))

        Resource.save_all(resources)

        # Trigger alerts
        for r in resources:
            if r.is_low():
                Alert.log_resource_alert(r.resource_type, r.available, r.threshold)

        flash("Resources updated successfully and alerts checked.", "success")
        return redirect(url_for("settings"))


    @app.route("/reset", methods=["POST"])
    def reset_system():
        import os
        from alert import ALERT_FILE
        from resource import RESOURCE_FILE, RESOURCE_LOG_FILE
        from planet import PLANET_FILE
        from mission import MISSION_FILE

        # Delete all data files
        for f in [ALERT_FILE, RESOURCE_FILE, RESOURCE_LOG_FILE, PLANET_FILE, MISSION_FILE]:
            if f.exists():
                os.remove(f)

        # Start the hardcoded initialisation in the respective module
        reset_alerts()
        reset_resources()
        reset_planets()
        reset_missions()

        flash("System reset complete.", "success")
        return redirect(url_for("index"))


    # Resources Page
    @app.route("/resources")
    def view_resources():
        with open("data/resources.json", "r") as f:
            current_resources = json.load(f)

        with open("data/resource_log.json", "r") as f:
            usage_log = json.load(f)

        return render_template(
            "resources.html",
            resources=current_resources,
            usage_log=usage_log,
            is_admin=session.get("logged_in", False)
        )

    # Planets Page
    @app.route("/planets")
    def view_planets():
        planets = Planet.load_all()
        return render_template("planets.html", planets=planets)

    @app.route("/planet/delete/<pid>")
    def delete_planet(pid):
        planet = Planet.delete_by_id(pid)
        if planet:
            flash(f"Planet {planet.planet_id} [{planet.name}] deleted.", "success")
        else:
            flash("Planet not found.", "danger")
        return redirect(url_for("view_planets"))

    @app.route("/planet/edit/<pid>", methods=["GET", "POST"])
    def edit_planet(pid):
        planet = Planet.find_by_id(pid)
        if not planet:
            flash("Error: Planet not found", "danger")
            return redirect(url_for("view_planets"))

        if request.method == "POST":
            Planet.update_planet(pid, request.form)
            flash("Planet updated", "success")
            return redirect(url_for("view_planets"))

        return render_template("edit_planet.html", planet=planet)

    @app.route("/planet/new", methods=["GET", "POST"])
    def new_planet():
        if request.method == "POST":
            try:
                x = int(request.form['x'])
                y = int(request.form['y'])
                score = int(request.form['rebel_score'])

                if x < 0 or x > 1920 or y < 0 or y > 1080:
                    flash('Coordinates must be within map boundaries (0-1920, 0-1080).', 'danger')
                    return render_template("new_planet.html")
                if not 0 <= score <= 10:
                    flash('Rebel score must be within 0 and 10.', 'danger')
                    return render_template("new_planet.html")

                new = Planet.create_new(request.form)
                flash(f"New planet {new.planet_id} ({new.name}) added!", "success")
                return redirect(url_for("view_planets"))

            except ValueError:
                flash('Coordinates and rebel score must be integers.', 'danger')
                return render_template("new_planet.html")

        return render_template("new_planet.html")

    # Star Map Page
    @app.route("/map")
    def view_map():
        return render_template("map.html")

    @app.route("/api/planets")
    def api_planets():
        planets = Planet.load_all()
        return jsonify([p.to_dict() for p in planets])


    # Mission Page
    @app.route("/missions")
    def view_missions():
        all_missions = Mission.load_all()

        updated = False
        for i, m in enumerate(all_missions):
            current_status = m.get_current_status()
            if m.status != current_status:
                m.status = current_status
                process_resource_for_mission(m)
                updated = True
        if updated:
            Mission.save_all(all_missions)

        non_cancelled = [m for m in all_missions if m.status != 'cancelled']
        total = len(non_cancelled)
        done = len([m for m in all_missions if m.status == 'completed'])
        in_progress = len([m for m in all_missions if m.status in ('active', 'planned')])
        unassigned = len([m for m in all_missions if m.status == 'draft'])

        priority_order = {'active': 0, 'planned': 1}
        active_planned = sorted(
            [m for m in all_missions if m.status in ('active', 'planned')],
            key=lambda m: priority_order.get(m.status, 99)
        )

        drafts = [m for m in all_missions if m.status == 'draft']
        completed = [m for m in all_missions if m.status == 'completed']

        return render_template(
            'missions.html',
            total=total,
            done=done,
            in_progress=in_progress,
            unassigned=unassigned,
            active_planned=active_planned,
            drafts=drafts,
            completed=completed
        )

    @app.route("/mission/edit/<mid>", methods=["GET", "POST"])
    def edit_mission(mid):
        mission = Mission.find_by_id(mid)
        if not mission:
            flash("Mission not found.", "danger")
            return redirect(url_for("view_missions"))

        if request.method == "POST":
            mission.name = request.form["name"]
            mission.description = request.form["description"]
            mission.start_time = request.form["start_time"].replace("T", " ")
            mission.end_time = request.form["end_time"].replace("T", " ")
            mission.resources_used = {
                "ENERGY": int(request.form.get("energy", 0)),
                "DROIDS": int(request.form.get("droids", 0)),
                "FACILITIES": int(request.form.get("facilities", 0))
            }
            mission.status = request.form.get("status", "planned")

            all_missions = Mission.load_all()
            for i in range(len(all_missions)):
                if all_missions[i].mission_id == mid:
                    all_missions[i] = mission
                    break

            Mission.save_all(all_missions)
            flash("Mission updated.", "success")
            process_resource_for_mission(mission)
            return redirect(url_for("view_missions"))
        else:
            return render_template("edit_mission.html", mission=mission)

    @app.route("/mission/new", methods=["GET", "POST"])
    def add_mission():
        if request.method == "POST":
            resources_used = {
                "ENERGY": int(request.form.get("energy", 0)),
                "DROIDS": int(request.form.get("droids", 0)),
                "FACILITIES": int(request.form.get("facilities", 0))
            }

            new_mission = Mission.create_new(request.form)
            new_mission.resources_used = resources_used

            all_missions = Mission.load_all()
            all_missions.append(new_mission)
            Mission.save_all(all_missions)
            process_resource_for_mission(new_mission)
            flash("New mission added!", "success")
            return redirect(url_for("view_missions"))
        else:
            return render_template("new_planet.html")

    @app.route("/mission/delete/<mid>")
    def delete_mission(mid):
        mission = Mission.delete_by_id(mid)
        if mission:
            flash(f"Deleted mission {mid}.", "success")
        else:
            flash("Only draft missions can be deleted.", "warning")
        return redirect(url_for("view_missions"))

    @app.route("/api/missions")
    def api_missions():
        missions = Mission.load_all()
        return jsonify([m.to_dict() for m in missions])


    # Alerts Page
    @app.route("/alerts")
    def view_alerts():
        alerts = Alert.load_all()
        return render_template("alerts.html", alerts=alerts)

    @app.route("/alerts/resolve/<time>")
    def resolve_alert(time):
        alerts = Alert.load_all()
        for a in alerts:
            if a.time == time:
                a.status = "Resolved"
        Alert.save_all(alerts)
        flash("Alert marked as resolved.", "info")
        return redirect(url_for("view_alerts"))

    @app.route("/alerts/delete/<time>")
    def delete_alert(time):
        alerts = Alert.load_all()
        alerts = [a for a in alerts if a.time != time]
        Alert.save_all(alerts)
        flash("Alert deleted.", "info")
        return redirect(url_for("view_alerts"))

    @app.route("/alerts/create", methods=["POST"])
    def create_alert():
        alert_type = request.form["type"]
        content = request.form["content"]
        level = request.form["level"]
        time = request.form.get("time", None)
        if not time:
            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        new_alert = Alert(alert_type, content, level, time)
        alerts = Alert.load_all()
        alerts.append(new_alert)
        Alert.save_all(alerts)
        flash("Manual alert created.", "success")
        return redirect(url_for("view_alerts"))

    @app.route("/alerts/resolve_all", methods=["POST"])
    def resolve_all_alerts():
        alerts = Alert.load_all()
        for a in alerts:
            a.status = "Resolved"
        Alert.save_all(alerts)
        flash("All alerts marked as resolved.", "info")
        return redirect(url_for("view_alerts"))


    # Report Page
    @app.route("/reports")
    def view_reports():
        missions = load_mission_data()
        resources = load_current_resources()
        resource_logs = load_resource_logs()
        return render_template("reports.html", missions=missions, resources=resources, resource_logs=resource_logs)

    @app.route("/export_report_csv", methods=["POST"])
    def export_report_csv():
        import csv
        from io import StringIO

        include_resource = bool(request.form.get("export_resource"))
        include_mission = bool(request.form.get("export_mission"))

        output = StringIO()
        writer = csv.writer(output)

        if include_mission:
            writer.writerow(["Mission Report"])
            writer.writerow(["ID", "Name", "Description", "Status", "Start Time", "End Time"])
            for m in load_mission_data():
                writer.writerow([m.mission_id, m.name, m.description, m.status, m.start_time, m.end_time])
            writer.writerow([])

        if include_resource:
            writer.writerow(["Current Resource Overview"])
            writer.writerow(["Type", "Available", "Threshold"])
            for r in load_current_resources():
                writer.writerow([r.resource_type, r.available, r.threshold])
            writer.writerow([])

            writer.writerow(["Resource Usage Log"])
            writer.writerow(["Date", "ENERGY", "DROIDS", "FACILITIES"])
            for log in load_resource_logs():
                writer.writerow([
                    log["date"],
                    log.get("ENERGY", 0),
                    log.get("DROIDS", 0),
                    log.get("FACILITIES", 0)
                ])

        csv_data = output.getvalue()
        output.close()

        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=system_report.csv"}
        )

    @app.route("/login", methods=["GET", "POST"])
    def login():
        users = {
            "admin@example.com": "123456",
            "test@example.com": "654321"
        }
        error = None
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")
            if email in users and users[email] == password:
                session["logged_in"] = True
                session["user_email"] = email
                return redirect(url_for("index"))
            else:
                error = "Invalid email or password."
        return render_template("login.html", error=error)

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.route("/register", methods=["GET", "POST"])
    def register():
        users = {
            "admin@example.com": "123456",
            "test@example.com": "654321"
        }
        error = None
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")
            confirm_password = request.form.get("confirm_password")
            if email in users:
                error = "Email already registered."
            elif password != confirm_password:
                error = "Passwords do not match."
            else:
                # 实际项目应写入数据库，这里仅演示
                users[email] = password
                return redirect(url_for("login"))
        return render_template("register.html", error=error)
