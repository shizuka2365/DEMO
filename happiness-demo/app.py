from flask import Flask, render_template, jsonify
import random
from datetime import datetime
import os

app = Flask(__name__)

class SimulationState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.current_day = 1
        self.max_days = 60
        self.active_users = 0
        self.points_issued_today = 0
        self.avg_trust = 45.0
        self.total_points_issued = 0
        self.risk_events = 0
        self.phase = "启动期"
        self.users = self._create_users()

    def _create_users(self):
        types = ["early_adopter"] * 2 + ["follower"] * 2 + ["skeptic"] * 1
        users = []
        for i in range(5):
            utype = random.choice(types)
            trust = {"early_adopter": 65, "follower": 45, "skeptic": 25}[utype]
            points = {"early_adopter": 3000, "follower": 800, "skeptic": 100}[utype]
            team = {"early_adopter": random.randint(8,20), "follower": random.randint(1,5), "skeptic": 0}[utype]
            users.append({
                "name": f"用户{i+1}",
                "type": utype,
                "trust": trust,
                "points": points,
                "team": team,
                "tier": "银牌" if points > 2000 else "铜牌"
            })
        return users

    def get_phase(self, day):
        if day <= 14: return "启动期"
        elif day <= 30: return "增长期"
        elif day <= 45: return "转化期"
        elif day <= 60: return "收割期"
        else: return "延伸期"

    def advance_day(self):
        if self.current_day >= self.max_days:
            return False
        self.current_day += 1
        self.phase = self.get_phase(self.current_day)
        base_active = 3 + (self.current_day / 60) * 2
        self.active_users = min(5, max(1, int(base_active + random.uniform(-1, 2))))
        points_today = random.randint(180, 450)
        if self.phase in ["转化期", "收割期"]:
            points_today = int(points_today * 1.4)
        self.points_issued_today = points_today
        self.total_points_issued += points_today
        trust_change = random.uniform(-4, 7)
        if self.phase == "启动期": trust_change += 4
        elif self.phase == "收割期": trust_change -= 3
        self.avg_trust = max(20, min(98, self.avg_trust + trust_change / 6))
        if random.random() < 0.18 and self.phase in ["转化期", "收割期"]:
            self.risk_events += 1
        for user in self.users:
            user["points"] += random.randint(60, 350)
            user["trust"] = max(10, min(98, user["trust"] + random.uniform(-6, 10)))
            if user["type"] == "early_adopter":
                user["team"] += random.randint(0, 3)
            if user["points"] > 15000:
                user["tier"] = "金牌"
            elif user["points"] > 5000:
                user["tier"] = "银牌"
        return True

state = SimulationState()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    return jsonify({
        "day": state.current_day,
        "phase": state.phase,
        "active_users": state.active_users,
        "points_today": state.points_issued_today,
        "total_points": state.total_points_issued,
        "avg_trust": round(state.avg_trust, 1),
        "risk_events": state.risk_events,
        "users": state.users[:3],
        "is_end": state.current_day >= state.max_days,
        "current_date": datetime.now().strftime("%Y年%m月%d日")
    })

@app.route('/api/advance')
def advance():
    success = state.advance_day()
    return jsonify({"success": success})

@app.route('/api/reset')
def reset():
    state.reset()
    return jsonify({"success": True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))

    app.run(host='0.0.0.0', port=port)
