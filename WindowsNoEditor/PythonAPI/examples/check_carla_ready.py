import time
from carla import Client

def check_carla_ready():
    print("Waiting for 20 seconds before starting readiness checks...")
    time.sleep(20)  # Add 20-second delay

    client = Client("localhost", 2000)
    client.set_timeout(10.0)  # Increase timeout for slow systems
    max_retries = 20  # Limit retries to 20 attempts (~40 seconds)

    for attempt in range(max_retries):
        try:
            world = client.get_world()
            print(f"CARLA is ready! Connected on attempt {attempt + 1}.")
            return True
        except Exception as e:
            print(f"Attempt {attempt + 1}: CARLA not ready yet ({str(e)}). Retrying in 2 seconds...")
            time.sleep(2)

    print("CARLA did not respond in time. Exiting.")
    return False

if __name__ == "__main__":
    if not check_carla_ready():
        exit(1)  # Exit with an error if CARLA is not ready
