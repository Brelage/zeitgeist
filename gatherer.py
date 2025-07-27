import subprocess
import fetch_tagesschau
import scrape_zeit


def main():
    subprocess.run(scrape_zeit)
    subprocess.run(fetch_tagesschau)


if __name__ == "__main__":
    main()