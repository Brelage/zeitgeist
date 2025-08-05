import os
from pathlib import Path
import subprocess

os.makedirs("workbench", exist_ok=True)
SCRIPTS_DIR = Path(__file__).parent / "gathering_scripts"

def main():
    procs = [
        subprocess.Popen(["python3", str(SCRIPTS_DIR / "gather_zeit.py")]),
        subprocess.Popen(["python3", str(SCRIPTS_DIR / "gather_tagesschau.py")])
    ]
    for p in procs:
        p.wait()

if __name__ == "__main__":
    main()
