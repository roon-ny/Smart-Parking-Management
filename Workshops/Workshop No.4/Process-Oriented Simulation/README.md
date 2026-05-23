[README.md](https://github.com/user-attachments/files/28179963/README.md)
# Workshop 4: Simulation & Validation (SCPMS)

## Context
This is a Python program with a visual window to test if our parking system design from Workshop 2 works well under real-life campus traffic.

## Integration with Previous Workshops
- **Workshop 1 (Data):** We used the actual busy hours data (6:30 AM to 8:30 AM) to set up how fast students arrive in the system.
- **Workshop 2 (Design):** We tested the 20-minute reservation rule (TTL) to see if spots open up automatically when someone doesn't show up.
- **Workshop 3 (Management):** We added an automatic log file to save everything that happens, making sure our tests are reliable.

## Instructions
1. Activate virtual environment: `venv\Scripts\activate`
2. Run simulation: `python scmp_simulation.py`
3. Verify results in `simulation_output.log`.
