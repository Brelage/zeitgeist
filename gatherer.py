import subprocess

def main():
    procs = [
        subprocess.Popen(["python3", "scrape_zeit.py"]),
        subprocess.Popen(["python3", "fetch_tagesschau.py"])
    ]
    for p in procs:
        p.wait()


if __name__ == "__main__":
    main()