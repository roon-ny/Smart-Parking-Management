"""
Visual Simulation using Tkinter
"""
import json
import random
import heapq
import logging
import tkinter as tk

# Setup the log file to save all simulation results
logging.basicConfig(
    filename='output.log',
    level=logging.INFO,
    format='%(message)s',
    filemode='w'
)

# Load configuration from JSON
with open("config.json", "r") as f:
    CFG = json.load(f)

# Use a fixed seed so the simulation gives the same results every time
random.seed(42) 

# Interface colors
C = {
    "FREE":      "#27ae60",
    "RESERVED":  "#f39c12",
    "OCCUPIED":  "#e74c3c",
    "VIOLATION": "#9b59b6",
    "bg":        "#1a252f",
    "panel":     "#2c3e50",
    "text":      "#ecf0f1",
    "blue":      "#3498db",
    "green":     "#2ecc71",
    "dim":       "#7f8c8d",
    "divider":   "#3d5166",
}

# Grid settings (8 columns x 5 rows = 40 parking slots)
COLS  = 8
ROWS  = 5
SW    = 74   # Slot width
SH    = 44   # Slot height
PAD   = 8    # Padding

def to_time(minutes: float) -> str:
    """Convert simulation minutes to standard HH:MM format."""
    m = int(minutes)
    return f"{m // 60:02d}:{m % 60:02d}"


# ============================================================
# PARKING SYSTEM LOGIC
# ============================================================
class ParkingSystem:
    def __init__(self):
        # Create 40 slots labeled from S01 to S40, all FREE at the start
        self.slots = {f"S{i+1:02d}": "FREE" for i in range(CFG["total_slots"])}
        self.reservations = {} # Maps User ID -> Slot ID
        
        # Dictionary to keep track of numbers
        self.stats = {
            "arrivals": 0, "confirmed": 0, "rejected": 0,
            "checkins": 0, "ttl_releases": 0,
            "violations": 0, "checkouts": 0,
        }

    def find_free_slot(self):
        """Find the first available parking spot."""
        for sid, state in self.slots.items():
            if state == "FREE":
                return sid
        return None

    def reserve(self, uid: str):
        self.stats["arrivals"] += 1
        
        # If user already has a reservation, do nothing (Rule from Workshop 2)
        if uid in self.reservations:  
            return None
            
        slot = self.find_free_slot()
        if slot is None:
            self.stats["rejected"] += 1
            return None
            
        # Assign slot and update state
        self.slots[slot] = "RESERVED"
        self.reservations[uid] = slot
        self.stats["confirmed"] += 1
        return slot

    def checkin(self, uid: str):
        slot = self.reservations.get(uid)
        if slot and self.slots[slot] == "RESERVED":
            self.slots[slot] = "OCCUPIED"
            self.stats["checkins"] += 1
            return slot
        return None

    def ttl_expire(self, uid: str):
        slot = self.reservations.get(uid)
        # Only cancel if the user never showed up and slot is still RESERVED
        if slot and self.slots[slot] == "RESERVED":
            self.reservations.pop(uid)
            self.slots[slot] = "FREE"
            self.stats["ttl_releases"] += 1

    def violation(self, uid: str):
        slot = self.reservations.get(uid)
        if slot and self.slots[slot] == "OCCUPIED":
            self.slots[slot] = "VIOLATION"
            self.stats["violations"] += 1

    def checkout(self, uid: str):
        slot = self.reservations.pop(uid, None)
        if slot:
            self.slots[slot] = "FREE"
            self.stats["checkouts"] += 1


# ============================================================
# TRAFFIC GENERATION (ARRIVALS)
# ============================================================
def generate_arrivals(events_list):
    """Generate user arrivals for the day based on peak hours from Workshop 1."""
    t = float(CFG["start_time"])
    uid = 1

    while t < CFG["end_time"]:
        # Check current time to set the correct arrival rate
        if 390 <= t <= 510:
            rate = CFG["peak_rate"]        # Morning peak hours (06:30 - 08:30)
        elif (600 <= t <= 720) or (780 <= t <= 900):
            rate = CFG["normal_rate"] * 1.5 # Midday and afternoon rush
        else:
            rate = CFG["normal_rate"]      # Slow hours

        # Advanced time using exponential distribution
        t += random.expovariate(rate)
        if t >= CFG["end_time"]:
            break

        # Add arrival event to the heap list
        heapq.heappush(events_list, (t, "ARRIVE", f"U{uid:04d}"))
        uid += 1


# ============================================================
# GRAPHICAL INTERFACE (GUI)
# ============================================================
class SimApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.system = ParkingSystem()
        self.events = [] # This list will hold all events sorted by time
        self.clock = float(CFG["start_time"])
        self.log_history = []

        self.root.title("SCPMS — Parking Simulation")
        self.root.configure(bg=C["bg"])
        self.root.resizable(False, False)

        self._build_ui()
        generate_arrivals(self.events) # Pre-load the day's arrivals
        logging.info("--- STARTING SIMULATION LOG ---")

    def _build_ui(self):
        # Header labels
        tk.Label(self.root, text="Smart Campus Parking Management System", bg=C["bg"], fg=C["text"], font=("Helvetica", 13, "bold")).pack(pady=(12, 2))
        tk.Label(self.root, text=" Process-Oriented Simulation  |  Discrete-Event Simulation ", bg=C["bg"], fg=C["dim"], font=("Helvetica", 8)).pack(pady=(0, 8))

        main_frame = tk.Frame(self.root, bg=C["bg"])
        main_frame.pack(padx=16)

        # Left side: Parking Grid
        left_frame = tk.Frame(main_frame, bg=C["bg"])
        left_frame.pack(side=tk.LEFT)
        tk.Label(left_frame, text="Parking Slots — Basement 3", bg=C["bg"], fg=C["text"], font=("Helvetica", 10, "bold")).pack(pady=(0, 4))

        cw = COLS * (SW + 4) + PAD * 2
        ch = ROWS * (SH + 4) + PAD * 2
        self.canvas = tk.Canvas(left_frame, width=cw, height=ch, bg=C["panel"], highlightthickness=1, highlightbackground=C["divider"])
        self.canvas.pack()

        # Draw the 40 parking squares
        self.rects = {}
        for i in range(CFG["total_slots"]):
            row, col = divmod(i, COLS)
            x1 = PAD + col * (SW + 4)
            y1 = PAD + row * (SH + 4)
            sid = f"S{i+1:02d}"
            self.rects[sid] = self.canvas.create_rectangle(x1, y1, x1+SW, y1+SH, fill=C["FREE"], outline="#1a252f", width=2)
            self.canvas.create_text((x1 + x1+SW) // 2, (y1 + y1+SH) // 2, text=sid, fill="white", font=("Helvetica", 8, "bold"))

        # Right side: Control Panel and Counters
        panel = tk.Frame(main_frame, bg=C["panel"], padx=14, pady=14)
        panel.pack(side=tk.LEFT, padx=(12, 0), fill=tk.Y)

        tk.Label(panel, text="Simulation Time", bg=C["panel"], fg=C["dim"], font=("Helvetica", 9)).pack()
        self.time_var = tk.StringVar(value="06:00")
        tk.Label(panel, textvariable=self.time_var, bg=C["panel"], fg=C["blue"], font=("Helvetica", 24, "bold")).pack()
        
        # Draw line separator
        tk.Frame(panel, bg=C["divider"], height=1).pack(fill=tk.X, pady=7)

        # Setup stats counters
        self.labels_vars = {}
        rows = [
            ("arrivals",     "Total Arrivals", C["text"]),
            ("confirmed",    "Reservations OK", C["green"]),
            ("rejected",     "Rejected (Full)", "#e74c3c"),
            ("checkins",     "Checked In",     C["blue"]),
            ("ttl_releases", "Expired (TTL)",  "#f39c12"),
            ("violations",   "Violations",     "#9b59b6"),
            ("checkouts",    "Checked Out",    C["dim"]),
        ]
        for key, text, color in rows:
            f = tk.Frame(panel, bg=C["panel"])
            f.pack(fill=tk.X, pady=1)
            tk.Label(f, text=text, bg=C["panel"], fg="#95a5a6", font=("Helvetica", 9), width=16, anchor="w").pack(side=tk.LEFT)
            v = tk.StringVar(value="0")
            self.labels_vars[key] = v
            tk.Label(f, textvariable=v, bg=C["panel"], fg=color, font=("Courier", 9, "bold"), width=4).pack(side=tk.LEFT)

        tk.Frame(panel, bg=C["divider"], height=1).pack(fill=tk.X, pady=7)

        # Color Legends
        for state, label in [("FREE", "Free"), ("RESERVED", "Reserved"), ("OCCUPIED", "Occupied"), ("VIOLATION", "Violation")]:
            f = tk.Frame(panel, bg=C["panel"])
            f.pack(fill=tk.X, pady=1)
            tk.Label(f, bg=C[state], width=3).pack(side=tk.LEFT, padx=(0, 6))
            tk.Label(f, text=label, bg=C["panel"], fg=C["text"], font=("Helvetica", 9)).pack(side=tk.LEFT)

        tk.Frame(panel, bg=C["divider"], height=1).pack(fill=tk.X, pady=7)

        # Start button
        self.btn = tk.Button(panel, text="▶ Start Simulation", command=self._start, bg=C["blue"], fg="white", font=("Helvetica", 11, "bold"), relief="flat", cursor="hand2", padx=8, pady=7)
        self.btn.pack(fill=tk.X)

        # Bottom Frame: Event Log Console
        bottom_frame = tk.Frame(self.root, bg=C["bg"])
        bottom_frame.pack(padx=16, pady=(10, 12), fill=tk.X)
        tk.Label(bottom_frame, text="Live Event Log", bg=C["bg"], fg=C["text"], font=("Helvetica", 9, "bold")).pack(anchor="w")
        
        self.log_var = tk.StringVar(value="Press Start to begin the process...")
        tk.Label(bottom_frame, textvariable=self.log_var, bg=C["panel"], fg="#95a5a6", font=("Courier", 8), justify=tk.LEFT, anchor="w", padx=10, pady=7, wraplength=840).pack(fill=tk.X)

    def _start(self):
        self.btn.config(state=tk.DISABLED, text="Running...")
        self._loop()

    def _loop(self):
        """Main loop that runs events one by one."""
        if not self.events:
            self._finish()
            return

        t, etype, uid = heapq.heappop(self.events)
        if t > CFG["end_time"]:
            self._finish()
            return

        self.clock = t
        msg = self._handle_event(t, etype, uid)
        self._update_ui(msg)
        
        # Schedule next event based on config speed
        self.root.after(CFG["step_ms"], self._loop)

    def _handle_event(self, t: float, etype: str, uid: str) -> str:
        """Process the event and schedule future actions."""
        sys = self.system
        ttl = CFG["ttl_minutes"]

        if etype == "ARRIVE":
            slot = sys.reserve(uid)
            if slot:
                # Schedule check-in time (randomly before TTL expires)
                show_up = t + random.uniform(1, ttl - 1)
                heapq.heappush(self.events, (show_up, "CHECKIN", uid))
                # Schedule TTL expiration check
                heapq.heappush(self.events, (t + ttl, "TTL", uid))
                return f"[{to_time(t)}] User {uid} reserved slot {slot}"
            else:
                return f"[{to_time(t)}] User {uid} REJECTED — Parking lot full"

        elif etype == "CHECKIN":
            slot = sys.checkin(uid)
            if slot:
                # Calculate how long the user stays
                stay = max(10.0, random.expovariate(1.0 / CFG["avg_stay_min"]))
                
                # Check if user will overstay and cause a violation
                if random.random() < CFG["overstay_prob"]:
                    heapq.heappush(self.events, (t + stay, "VIOLATION", uid))
                    heapq.heappush(self.events, (t + stay + random.uniform(10, 40), "CHECKOUT", uid))
                else:
                    heapq.heappush(self.events, (t + stay, "CHECKOUT", uid))
                return f"[{to_time(t)}] User {uid} checked in at slot {slot}"
            else:
                return f"[{to_time(t)}] User {uid} check-in failed (Reservation expired)"

        elif etype == "TTL":
            sys.ttl_expire(uid)
            return f"[{to_time(t)}] Slot auto-released for user {uid} (TTL Expired)"

        elif etype == "VIOLATION":
            sys.violation(uid)
            return f"[{to_time(t)}] ALERT: User {uid} exceeded allowed time!"

        elif etype == "CHECKOUT":
            sys.checkout(uid)
            return f"[{to_time(t)}] User {uid} checked out safely"
            
        return ""

    def _update_ui(self, msg: str):
        """Refresh the interface counters and colors."""
        self.time_var.set(to_time(self.clock))
        
        # Refresh colors of squares
        for sid, state in self.system.slots.items():
            self.canvas.itemconfig(self.rects[sid], fill=C.get(state, C["FREE"]))
        
        # Refresh numerical counters
        for key, var in self.labels_vars.items():
            var.set(str(self.system.stats[key]))

        # Update text log at the bottom and write to log file
        if msg:
            logging.info(msg)
            self.log_history.append(msg)
            if len(self.log_history) > 4:
                self.log_history.pop(0)
            self.log_var.set("\n".join(self.log_history))

    def _finish(self):
        """Actions to take when simulation ends."""
        s = self.system.stats
        total = s["arrivals"]
        rate = (s["confirmed"] / total * 100) if total else 0
        final_msg = f"SIMULATION COMPLETE | Total Served: {s['confirmed']}/{total} ({rate:.1f}%) | Total Rejections: {s['rejected']}"
        
        logging.info(final_msg)
        self.btn.config(text="✓ Finished", bg="#27ae60", state=tk.NORMAL)
        self.log_var.set(final_msg)

if __name__ == "__main__":
    root = tk.Tk()
    SimApp(root)
    root.mainloop()