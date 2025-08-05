import os
from pathlib import Path
import subprocess

os.makedirs("workbench", exist_ok=True)
SCRIPTS_DIR = Path(__file__).parent / "gathering_scripts"

def main():
    for file_name in os.listdir(SCRIPTS_DIR):
        if file_name.endswith(".py"):
            script_path = os.path.join(SCRIPTS_DIR, file_name)
            try:
                subprocess.run(["python", script_path], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error while running {script_path}: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
