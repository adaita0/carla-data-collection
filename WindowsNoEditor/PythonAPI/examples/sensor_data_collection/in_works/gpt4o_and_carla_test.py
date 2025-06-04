import carla
import cv2
import numpy as np
# this is not running as expected atm

# Connect to CARLA
client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()


# Get vehicle
blueprint_library = world.get_blueprint_library()
vehicle_bp = blueprint_library.find('vehicle.tesla.model3')
spawn_point = world.get_map().get_spawn_points()[0]


spawn_points = world.get_map().get_spawn_points()
for spawn_point in spawn_points:
    vehicle = world.try_spawn_actor(vehicle_bp, spawn_point)
    if vehicle:
        print(f"vehicle spawned at{spawn_point.location}")
        break


# vehicle = world.spawn_actor(vehicle_bp, spawn_point)


# Attach Camera Sensor
camera_bp = blueprint_library.find('sensor.camera.rgb')
camera_bp.set_attribute('image_size_x', '640')
camera_bp.set_attribute('image_size_y', '480')
camera_bp.set_attribute('fov', '90')

camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)

def process_image(image):
    """ Convert CARLA image to OpenCV format """
    img = np.array(image.raw_data).reshape((image.height, image.width, 4))[:, :, :3]
    return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

# Register the camera callback
def save_image(image):
    img = process_image(image)
    cv2.imwrite("carla_frame.jpg", img)

camera.listen(lambda image: save_image(image))