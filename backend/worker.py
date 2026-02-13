"""Background worker entrypoint for scheduled alert evaluation."""

import time


def run() -> None:
    while True:
        print("worker heartbeat: checking price alerts")
        time.sleep(30)


if __name__ == "__main__":
    run()
