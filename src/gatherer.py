import os
from pathlib import Path
import subprocess

SCRIPTS_DIR = Path(__file__).parent / "gathering_scripts"

def main():
    procs = [
        subprocess.Popen(["python3", str(SCRIPTS_DIR / "scrape_zeit.py")]),
        subprocess.Popen(["python3", str(SCRIPTS_DIR / "fetch_tagesschau.py")])
    ]
    for p in procs:
        p.wait()

if __name__ == "__main__":
    main()
