"""
SCPMS — Behavior-Oriented Simulation (Workshop 4)
Universidad Distrital Francisco José de Caldas — Semester 2026-I
────────────────────────────────────────────────────────────────
Paradigm : Agent-Based Model (ABM)
Each user is an autonomous agent with a behavioral state and
memory. Emergent phenomena modelled:
  • Adoption drift  — frustrated agents stop using the app
  • Social influence — agents copy neighbour behaviour
  • Bypass congestion — inactive agents park without reservation
"""

import tkinter as tk
import random, math, logging
from enum import Enum, auto

log_file = f"output.log"
logging.basicConfig(level=logging.INFO, format="%(message)s",
                    handlers=[logging.FileHandler(log_file), logging.StreamHandler()])
with open("config.json") as f:
    CFG = json.load(f)

C = {
    "bg": "#1a252f", "panel": "#2c3e50", "text": "#ecf0f1", "dim": "#95a5a6",
    "blue": "#3498db", "green": "#27ae60", "divider": "#3d5166",
    "FREE": "#27ae60", "RESERVED": "#2980b9", "OCCUPIED": "#8e44ad",
    "VIOLATION": "#c0392b", "INACTIVE": "#566573",
}

COLS, ROWS, SW, SH, PAD = 8, 5, 74, 44, 8

def to_time(m): return f"{int(m)//60:02d}:{int(m)%60:02d}"


# ── Agent ────────────────────────────────────────────────────────
class State(Enum):
    ARRIVING = auto(); RESERVED = auto(); CHECKED_IN = auto()
    OVERSTAYING = auto(); GONE = auto(); INACTIVE = auto()

class Agent:
    _n = 0
    def __init__(self, t):
        Agent._n += 1
        self.uid      = f"U{Agent._n:04d}"
        self.state    = State.ARRIVING
        self.slot     = None
        self.uses_app = True
        self.memory   = []   # "OK" / "REJ"

    def reject(self):
        self.memory = self.memory[-4:] + ["REJ"]
        if self.memory.count("REJ") >= CFG["frustration_threshold"]:
            if random.random() < 0.15:
                self.uses_app = False
                self.state = State.INACTIVE

    def social(self, neighbour_active):
        if not neighbour_active and random.random() < CFG["social_influence_r"]:
            self.uses_app = False
            self.state = State.INACTIVE


# ── Environment ──────────────────────────────────────────────────
class Env:
    def __init__(self):
        self.slots = {f"S{i+1:02d}": "FREE" for i in range(CFG["total_slots"])}
        self.owners = {}   # slot -> uid
        self.stats  = {k: 0 for k in
            ["arrivals","app","bypasses","confirmed","rejected",
             "checkins","ttl_releases","violations","resolved","checkouts","inactive"]}
        self.hist_t, self.hist_occ, self.hist_ina = [], [], []

    def _free(self):
        return next((s for s,v in self.slots.items() if v=="FREE"), None)

    def reserve(self, ag):
        self.stats["arrivals"] += 1; self.stats["app"] += 1
        if ag.slot: return False
        s = self._free()
        if not s:
            self.stats["rejected"] += 1; ag.reject(); return False
        self.slots[s] = "RESERVED"; self.owners[s] = ag.uid
        ag.slot = s; ag.state = State.RESERVED
        self.stats["confirmed"] += 1; ag.memory.append("OK"); return True

    def bypass(self, ag):
        self.stats["arrivals"] += 1; self.stats["bypasses"] += 1
        s = self._free()
        if s:
            self.slots[s] = "OCCUPIED"; self.owners[s] = ag.uid
            ag.slot = s; ag.state = State.CHECKED_IN; return True
        ag.state = State.GONE; return False

    def checkin(self, ag):
        if ag.slot and self.slots.get(ag.slot) == "RESERVED":
            self.slots[ag.slot] = "OCCUPIED"; self.stats["checkins"] += 1
            ag.state = State.CHECKED_IN; return True
        return False

    def ttl(self, ag):
        if ag.slot and self.slots.get(ag.slot) == "RESERVED":
            self.slots[ag.slot] = "FREE"; self.owners.pop(ag.slot, None)
            ag.slot = None; ag.state = State.GONE; self.stats["ttl_releases"] += 1

    def violation(self, ag):
        if ag.slot and self.slots.get(ag.slot) == "OCCUPIED":
            self.slots[ag.slot] = "VIOLATION"; ag.state = State.OVERSTAYING
            self.stats["violations"] += 1

    def resolve(self, ag):
        if ag.slot and self.slots.get(ag.slot) == "VIOLATION":
            self.slots[ag.slot] = "FREE"; self.owners.pop(ag.slot, None)
            ag.slot = None; ag.state = State.GONE
            self.stats["resolved"] += 1; self.stats["checkouts"] += 1

    def checkout(self, ag):
        if ag.slot:
            self.slots[ag.slot] = "FREE"; self.owners.pop(ag.slot, None)
            ag.slot = None; ag.state = State.GONE; self.stats["checkouts"] += 1

    def occ_rate(self):
        return sum(1 for v in self.slots.values() if v in ("OCCUPIED","VIOLATION")) / CFG["total_slots"]

    def snapshot(self, t, n_inactive):
        self.hist_t.append(t); self.hist_occ.append(self.occ_rate())
        self.hist_ina.append(n_inactive)


# ── Simulation ───────────────────────────────────────────────────
class Sim:
    def __init__(self):
        Agent._n = 0
        self.env = Env(); self.agents = []
        self.clock = float(CFG["start_time"]); self.sched = []
        self._snap_t = self.clock

    def _rate(self):
        t = self.clock
        if 390 <= t <= 510:   return CFG["peak_rate"]
        if (600<=t<=720) or (780<=t<=900): return CFG["normal_rate"]*1.5
        return CFG["normal_rate"]

    def _push(self, delay, action, ag):
        self.sched.append((self.clock + delay, action, ag))

    def tick(self):
        if self.clock >= CFG["end_time"]: return []
        msgs = []

        # Spawn arrivals (Poisson)
        r = self._rate()
        w = [math.exp(-r), r*math.exp(-r), (r**2/2)*math.exp(-r)]
        for _ in range(random.choices([0,1,2], weights=w)[0]):
            self.agents.append(Agent(self.clock))

        # Process arriving agents
        for ag in self.agents:
            if ag.state != State.ARRIVING: continue
            if ag.uses_app:
                if self.env.reserve(ag):
                    self._push(random.uniform(1, CFG["ttl_minutes"]-1), "CHECKIN", ag)
                    self._push(CFG["ttl_minutes"], "TTL", ag)
                    msgs.append(f"[{to_time(self.clock)}] {ag.uid} reserved {ag.slot}")
                else:
                    if ag.state != State.INACTIVE:
                        ag.state = State.GONE
                        msgs.append(f"[{to_time(self.clock)}] {ag.uid} REJECTED — full")
                    else:
                        self.env.stats["inactive"] += 1
                        msgs.append(f"[{to_time(self.clock)}] {ag.uid} INACTIVE — skipped app")
            else:
                ok = self.env.bypass(ag)
                if ok:
                    stay = max(10.0, random.expovariate(1/CFG["avg_stay_min"]))
                    if random.random() < CFG["overstay_prob"]:
                        self._push(stay, "VIOLATION", ag)
                        self._push(stay + random.uniform(3,8), "RESOLVE", ag)
                    else:
                        self._push(stay, "CHECKOUT", ag)
                    msgs.append(f"[{to_time(self.clock)}] {ag.uid} BYPASS — no reservation")
                else:
                    msgs.append(f"[{to_time(self.clock)}] {ag.uid} BYPASS REJECTED — no slot")

        # Process scheduled events
        pending = []
        for ft, act, ag in self.sched:
            if ft > self.clock: pending.append((ft, act, ag)); continue
            if act == "CHECKIN":
                if self.env.checkin(ag):
                    stay = max(10.0, random.expovariate(1/CFG["avg_stay_min"]))
                    if random.random() < CFG["overstay_prob"]:
                        self._push(stay, "VIOLATION", ag)
                        self._push(stay + random.uniform(3,8), "RESOLVE", ag)
                    else:
                        self._push(stay, "CHECKOUT", ag)
                    msgs.append(f"[{to_time(self.clock)}] {ag.uid} checked in → {ag.slot}")
                else:
                    msgs.append(f"[{to_time(self.clock)}] {ag.uid} check-in failed (TTL)")
            elif act == "TTL":
                self.env.ttl(ag)
                msgs.append(f"[{to_time(self.clock)}] {ag.uid} slot released (TTL)")
            elif act == "VIOLATION":
                self.env.violation(ag)
                msgs.append(f"[{to_time(self.clock)}] ⚠ {ag.uid} VIOLATION")
            elif act == "RESOLVE":
                self.env.resolve(ag)
                msgs.append(f"[{to_time(self.clock)}] Security resolved {ag.uid}")
            elif act == "CHECKOUT":
                self.env.checkout(ag)
                msgs.append(f"[{to_time(self.clock)}] {ag.uid} checked out")
        self.sched = pending

        # Social influence every 5 ticks
        if int(self.clock) % 5 == 0:
            active = [a for a in self.agents if a.state not in (State.GONE, State.INACTIVE)]
            for i, ag in enumerate(active):
                if ag.uses_app:
                    nb = active[(i-1) % len(active)] if len(active) > 1 else ag
                    ag.social(nb.uses_app)
                    if not ag.uses_app: self.env.stats["inactive"] += 1

        # Snapshot every 30 min
        if self.clock - self._snap_t >= 30:
            self.env.snapshot(self.clock, sum(1 for a in self.agents if not a.uses_app))
            self._snap_t = self.clock

        self.clock += 1.0
        return msgs

    @property
    def done(self): return self.clock >= CFG["end_time"]


# ── Mini chart ───────────────────────────────────────────────────
class Chart:
    def __init__(self, parent):
        self.w, self.h = 860, 80
        self.cv = tk.Canvas(parent, width=self.w, height=self.h,
                            bg=C["panel"], highlightthickness=1,
                            highlightbackground=C["divider"])
        self.cv.pack(pady=(4,0))
        p = 28
        self.cv.create_line(p,4,p,self.h-12,fill=C["divider"])
        self.cv.create_line(p,self.h-12,self.w-4,self.h-12,fill=C["divider"])

    def update(self, ts, occ, ina):
        self.cv.delete("d")
        if len(ts) < 2: return
        p = 28; pw = self.w-p-4; ph = self.h-16
        span = CFG["end_time"] - CFG["start_time"]
        mx = max(max(ina, default=1), 1)
        px = lambda t: p + int((t-CFG["start_time"])/span*pw)
        py = lambda v: 4 + int((1-v)*ph)
        pyi = lambda v: 4 + int((1-v/mx)*ph)
        for i in range(1, len(ts)):
            self.cv.create_line(px(ts[i-1]),py(occ[i-1]),px(ts[i]),py(occ[i]),fill=C["blue"],width=2,tags="d")
            self.cv.create_line(px(ts[i-1]),pyi(ina[i-1]),px(ts[i]),pyi(ina[i]),fill="#e67e22",width=2,tags="d")
        self.cv.create_text(p+4,8,text="─ Occupancy  ─ Inactive agents",
                            fill=C["dim"],font=("Helvetica",6),anchor="w",tags="d")


# ── GUI ──────────────────────────────────────────────────────────
class App:
    def __init__(self, root):
        self.root = root; self.sim = Sim(); self.log_h = []
        root.title("SCPMS — Behavior-Oriented Simulation (ABM)")
        root.configure(bg=C["bg"]); root.resizable(False, False)
        self._build()
        logging.info("─── SCPMS ABM SIMULATION LOG ───")

    def _build(self):
        tk.Label(self.root, text="Smart Campus Parking Management System",
                 bg=C["bg"], fg=C["text"], font=("Helvetica",13,"bold")).pack(pady=(12,2))
        tk.Label(self.root, text=" Behavior-Oriented Simulation  |  Agent-Based Model (ABM) ",
                 bg=C["bg"], fg=C["dim"], font=("Helvetica",8)).pack(pady=(0,8))

        mf = tk.Frame(self.root, bg=C["bg"]); mf.pack(padx=16)

        # Grid
        lf = tk.Frame(mf, bg=C["bg"]); lf.pack(side=tk.LEFT)
        tk.Label(lf, text="Parking Slots — Basement 3", bg=C["bg"], fg=C["text"],
                 font=("Helvetica",10,"bold")).pack(pady=(0,4))
        cw = COLS*(SW+4)+PAD*2; ch = ROWS*(SH+4)+PAD*2
        self.cv = tk.Canvas(lf, width=cw, height=ch, bg=C["panel"],
                            highlightthickness=1, highlightbackground=C["divider"])
        self.cv.pack()
        self.rects = {}
        for i in range(CFG["total_slots"]):
            r, c = divmod(i, COLS)
            x1 = PAD+c*(SW+4); y1 = PAD+r*(SH+4)
            sid = f"S{i+1:02d}"
            self.rects[sid] = self.cv.create_rectangle(x1,y1,x1+SW,y1+SH,fill=C["FREE"],outline="#1a252f",width=2)
            self.cv.create_text((x1+x1+SW)//2,(y1+y1+SH)//2,text=sid,fill="white",font=("Helvetica",8,"bold"))

        # Panel
        p = tk.Frame(mf, bg=C["panel"], padx=14, pady=14); p.pack(side=tk.LEFT, padx=(12,0), fill=tk.Y)
        tk.Label(p, text="Simulation Time", bg=C["panel"], fg=C["dim"], font=("Helvetica",9)).pack()
        self.tvar = tk.StringVar(value="06:00")
        tk.Label(p, textvariable=self.tvar, bg=C["panel"], fg=C["blue"], font=("Helvetica",24,"bold")).pack()
        tk.Frame(p, bg=C["divider"], height=1).pack(fill=tk.X, pady=7)

        self.svars = {}
        for key, label, color in [
            ("arrivals","Total Arrivals",C["text"]), ("app","Via App",C["blue"]),
            ("bypasses","Bypasses (no app)","#e67e22"), ("confirmed","Reservations OK",C["green"]),
            ("rejected","Rejected (Full)","#e74c3c"), ("checkins","Checked In",C["blue"]),
            ("ttl_releases","Expired (TTL)","#f39c12"), ("violations","Violations","#9b59b6"),
            ("resolved","Violations Resolved",C["green"]), ("checkouts","Checked Out",C["dim"]),
            ("inactive","Inactive Agents ⚠","#e67e22"),
        ]:
            f = tk.Frame(p, bg=C["panel"]); f.pack(fill=tk.X, pady=1)
            tk.Label(f,text=label,bg=C["panel"],fg="#95a5a6",font=("Helvetica",9),width=18,anchor="w").pack(side=tk.LEFT)
            v = tk.StringVar(value="0"); self.svars[key] = v
            tk.Label(f,textvariable=v,bg=C["panel"],fg=color,font=("Courier",9,"bold"),width=4).pack(side=tk.LEFT)

        tk.Frame(p, bg=C["divider"], height=1).pack(fill=tk.X, pady=7)
        for state, label in [("FREE","Free"),("RESERVED","Reserved"),
                              ("OCCUPIED","Occupied"),("VIOLATION","Violation"),("INACTIVE","Bypass (no app)")]:
            f = tk.Frame(p, bg=C["panel"]); f.pack(fill=tk.X, pady=1)
            tk.Label(f,bg=C[state],width=3).pack(side=tk.LEFT,padx=(0,6))
            tk.Label(f,text=label,bg=C["panel"],fg=C["text"],font=("Helvetica",9)).pack(side=tk.LEFT)

        tk.Frame(p, bg=C["divider"], height=1).pack(fill=tk.X, pady=7)
        self.btn = tk.Button(p, text="▶ Start Simulation", command=self._start,
                             bg=C["blue"], fg="white", font=("Helvetica",11,"bold"),
                             relief="flat", cursor="hand2", padx=8, pady=7)
        self.btn.pack(fill=tk.X)

        # Chart + log
        bf = tk.Frame(self.root, bg=C["bg"]); bf.pack(padx=16, pady=(8,4), fill=tk.X)
        tk.Label(bf, text="Live Analytics — Occupancy Rate & Adoption Drift",
                 bg=C["bg"], fg=C["text"], font=("Helvetica",9,"bold")).pack(anchor="w")
        self.chart = Chart(bf)

        lf2 = tk.Frame(self.root, bg=C["bg"]); lf2.pack(padx=16, pady=(4,12), fill=tk.X)
        tk.Label(lf2, text="Live Agent Event Log", bg=C["bg"], fg=C["text"],
                 font=("Helvetica",9,"bold")).pack(anchor="w")
        self.lvar = tk.StringVar(value="Press ▶ Start to begin...")
        tk.Label(lf2, textvariable=self.lvar, bg=C["panel"], fg="#95a5a6",
                 font=("Courier",8), justify=tk.LEFT, anchor="w",
                 padx=10, pady=7, wraplength=860).pack(fill=tk.X)

    def _start(self):
        self.btn.config(state=tk.DISABLED, text="Running..."); self._loop()

    def _loop(self):
        if self.sim.done: self._finish(); return
        msgs = self.sim.tick(); self._update(msgs)
        self.root.after(CFG["step_ms"], self._loop)

    def _update(self, msgs):
        self.tvar.set(to_time(self.sim.clock))
        for sid, st in self.sim.env.slots.items():
            self.cv.itemconfig(self.rects[sid], fill=C.get(st, C["FREE"]))
        for k, v in self.svars.items():
            v.set(str(self.sim.env.stats.get(k, 0)))
        e = self.sim.env
        if e.hist_t: self.chart.update(e.hist_t, e.hist_occ, e.hist_ina)
        for m in msgs:
            if m: logging.info(m); self.log_h.append(m)
        self.log_h = self.log_h[-5:]
        if self.log_h: self.lvar.set("\n".join(self.log_h))

    def _finish(self):
        s = self.sim.env.stats
        t = s["arrivals"]
        pct = s["confirmed"]/t*100 if t else 0
        bp  = s["bypasses"]/t*100  if t else 0
        msg = (f"SIMULATION COMPLETE | Arrivals: {t} | Served via App: {s['confirmed']} ({pct:.1f}%) | "
               f"Bypasses: {s['bypasses']} ({bp:.1f}%) | Inactive Agents: {s['inactive']} | "
               f"Violations: {s['violations']}")
        logging.info(msg); logging.info(f"Log: {log_file}")
        self.lvar.set(msg); self.btn.config(text="✓ Finished", bg="#27ae60", state=tk.NORMAL)


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
