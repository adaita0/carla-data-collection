"""
author: @ananyakarra : akarra1@uci.edu
        @anjalidaita : aadaita@uci.edu
purpose: template sensor data collection script for Carla simulator
"""
import carla
import time
import numpy as np
import cv2
import math
import os
import json
from queue import Queue
from threading import Thread
from examples.manual_control_steeringwheel import DualControl
# Settings and configurations
sensor_data_folder = "./sensor_data"
if not os.path.exists(sensor_data_folder):
    os.makedirs(sensor_data_folder)
# Initialize the Carla client and world
client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()
spawn_points = world.get_map().get_spawn_points()
blueprint_library = world.get_blueprint_library()


# spawn_point = spawn_points[0] #seems to be providing errors at spawn point
# attempting to fix the spawning error:
spawned_actors = []
def cleanup_actors(actors):
    for actor in actors:
        if actor is not None:
            actor.destroy()
    print("Cleaned up all actors.")
vehicle_bp = blueprint_library.find('vehicle.tesla.model3')
vehicle = None
for spawn_point in spawn_points:
    try:
        vehicle = world.spawn_actor(vehicle_bp, spawn_point)
        spawned_actors.append(vehicle)
        print(f"Spawned vehicle at {spawn_point.location}")
        break
    except RuntimeError as e:
        print(f"Spawn failed at {spawn_point.location}: {e}")
        continue
if vehicle is None:
    print("ERROR: Failed to spawn vehicle at any available spawn point.")
    cleanup_actors(spawned_actors)
    exit(1)
# vehicle = world.spawn_actor(world.get_blueprint_library().find('vehicle.tesla.model3'), spawn_point)
def save_image(image, filename):
    image.save_to_disk(f"{sensor_data_folder}/{filename}.png")
def process_camera_data(image, queue):
   # print("Camera data received")

    # Convert the raw data from the image to a numpy array
    img_array = np.frombuffer(image.raw_data, dtype=np.uint8)
    # Reshape the array to the shape (height, width, 4) - 4 channels: BGRA
    img_array = np.reshape(img_array, (image.height, image.width, 4))
    # Convert BGRA to RGB by dropping alpha and reordering channels
    rgb_image = img_array[:, :, :3][:, :, ::-1]  # Take BGR and reverse to RGB
    # Optional: Save the image for reference
    filename = f"camera_{image.frame}"
    save_path = os.path.join(sensor_data_folder, f"{filename}.png")
    cv2.imwrite(save_path, rgb_image)
    # Package image metadata + image for JSON saving or debugging
    data = {
        'frame': image.frame,
        'timestamp': image.timestamp,
        'image_path': save_path
    }
    queue.put(data)
def process_imu_data(imu_data, queue):
    data = {
        'frame': imu_data.frame,
        'timestamp': imu_data.timestamp,
        'accelerometer': {
            'x': imu_data.accelerometer.x,
            'y': imu_data.accelerometer.y,
            'z': imu_data.accelerometer.z
        },
        'gyroscope': {
            'x': imu_data.gyroscope.x,
            'y': imu_data.gyroscope.y,
            'z': imu_data.gyroscope.z
        },
        'compass': imu_data.compass  # value between -1.0 and 1.0
    }
    queue.put(data)
def process_radar_data(radar_data, queue):
    detections = []
    for detection in radar_data:
        detections.append({
            'depth': detection.depth,   # Distance from radar to the object (in meters)
            'azimuth': math.degrees(detection.azimuth),  # Horizontal angle relative to the sensor (in radians)
            'altitude': math.degrees(detection.altitude),   # Vertical angle relative to the sensor (in radians)
            'velocity': detection.velocity  # Relative velocity (in m/s)
        })
    data = {
        'frame': radar_data.frame,
        'timestamp': radar_data.timestamp,
        'detections': detections
    }
    queue.put(data)
sensor_data_queue = Queue()
# Camera sensor (RGB)
try:
    camera_bp = blueprint_library.find('sensor.camera.rgb') # may or may not be the correct name of sensor in documentation
    camera_bp.set_attribute('image_size_x', '1280')
    camera_bp.set_attribute('image_size_y', '720')
    camera_bp.set_attribute('fov', '110')
    camera_location = carla.Transform(carla.Location(x=1.5, z=2.4))
    camera_sensor = world.spawn_actor(camera_bp, camera_location, attach_to=vehicle)
except RuntimeError as e:
    print(f"Camera sensor spawn failed: {e}")
    cleanup_actors(spawned_actors)
    exit(1)
# IMU sensor
try:
    imu_bp = blueprint_library.find('sensor.other.imu') # in format sensor.[class].[typeofsenseor]
    imu_location = carla.Transform(carla.Location(x=0, z=2.5))
    imu_sensor = world.spawn_actor(imu_bp, imu_location, attach_to=vehicle)
except RuntimeError as e:
    print(f"IMU sensor spawn failed: {e}")
    cleanup_actors(spawned_actors)
    exit(1)


    
# Radar sensor
try:
    radar_bp = blueprint_library.find('sensor.other.radar') # need to check sensor name in documentation
    radar_location = carla.Transform(carla.Location(x=0, z=2.5))
    radar_sensor = world.spawn_actor(radar_bp, radar_location, attach_to=vehicle)
except RuntimeError as e:
    print(f"Radar sensor spawn failed: {e}")
    cleanup_actors(spawned_actors)
    exit(1)
# sensor listeners

camera_sensor.listen(lambda image: process_camera_data(image, sensor_data_queue))

imu_sensor.listen(lambda imu_data: process_imu_data(imu_data, sensor_data_queue))

radar_sensor.listen(lambda radar_data: process_radar_data(radar_data, sensor_data_queue))


time.sleep(2)



sensor_data_folder = os.path.join(os.path.dirname(__file__), "sensor_data")
os.makedirs(sensor_data_folder, exist_ok=True)

sensor_data_path = os.path.join(sensor_data_folder, "sensor_data.json")
#HAD TO ADD THIS LINE TO CREATE THE JSON FILE


collection_duration = 60 # collection duration in seconds
start_time = time.time()
try:
    while time.time() - start_time < collection_duration:
        while not sensor_data_queue.empty():
            data = sensor_data_queue.get()
            # print("Collected Data:", data)
            with open(sensor_data_path, 'a') as f:
                json.dump(data, f)
                f.write("\n")
              # print("sensor data has been printed to JSON file")f
        # Tick the world to update the simulation
        world.tick() #world.tick() prints endlessly
        time.sleep(0.01)
finally:
    cleanup_actors(spawned_actors)
    print("Data collection completed and all actors cleaned up.")
    camera_sensor.stop()
    imu_sensor.stop()
    radar_sensor.stop()

  