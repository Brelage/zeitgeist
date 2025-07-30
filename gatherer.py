import subprocess

def main():
    subprocess.run(["python3", "scrape_zeit.py"])
    subprocess.run(["python3", "fetch_tagesschau.py"])


if __name__ == "__main__":
    main()