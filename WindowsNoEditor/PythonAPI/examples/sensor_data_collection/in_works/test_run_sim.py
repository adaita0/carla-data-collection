import carla
# this is also not working at the moment

# Connect to the CARLA simulator
client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()

# Get the ego vehicle
ego_vehicle = world.get_actor(1)  # Replace with actual vehicle ID

# Get surrounding vehicles
vehicles = world.get_actors().filter('vehicle.*')

# Extract positions and speeds
scene_data = []
for vehicle in vehicles:
    transform = vehicle.get_transform()
    velocity = vehicle.get_velocity()
    scene_data.append({
        "id": vehicle.id,
        "location": (transform.location.x, transform.location.y),
        "speed": (velocity.x, velocity.y),
    })