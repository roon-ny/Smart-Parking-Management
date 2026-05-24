# Workshop 4: Behavior-Oriented Simulation (SCPMS)

## Context
This is a Python program with a visual window that models each student as an **autonomous agent** to test how our parking system behaves when users get frustrated, stop using the app, and influence each other — emergent behaviors that a simple event simulation cannot capture.

## Integration with Previous Workshops
- **Workshop 1 (Data):** Peak hour rates (06:30–08:30 AM) from our field observation are used directly to control how fast agents arrive in the simulation.
- **Workshop 2 (Design):** The 20-minute TTL auto-release rule, duplicate reservation prevention, and the security violation alert flow are all implemented and tested under realistic load.
- **Workshop 3 (Management):** The adoption drift and social influence parameters map directly to the organizational risks identified in the risk register (low adoption RPN=15). An automatic `.log` file is saved on every run for reproducibility.

## What Makes This Different from Simulation 1
| Feature | Simulation 1 (Process-Oriented) | Simulation 2 (Behavior-Oriented) |
|---|---|---|
| Core unit | Scheduled events | Autonomous agents with memory |
| Models frustration | No | Yes — agents reject the app after repeated failures |
| Social influence | No | Yes — agents copy inactive neighbours |
| Bypass behavior | No | Yes — inactive agents park without reservation |
| Live chart | No | Yes — occupancy rate + adoption drift over time |

## Emergent Behaviors Observed
- **Adoption drift:** When the lot fills up during peak hours, repeated rejections push agents to stop using the app.
- **Social influence:** Inactive agents spread their behavior to neighbors, accelerating the drift.
- **Bypass congestion:** Agents who abandoned the app arrive without reservations, occupying slots outside the system and generating more violations.

## Instructions
1. Activate virtual environment: `venv\Scripts\activate`
2. Run simulation: `Behavior_Simulation.py`
3. Press **▶ Start Simulation** in the window.
4. Review results in the generated `output.log` file.


## Requirements
No external libraries needed — only Python standard library:
```
tkinter, random, math, logging, enum, datetime
```
