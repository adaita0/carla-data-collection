"""
@author: akarra1@uci.edu
@purpsoe: random pedestrian and car generator for carla simulation
"""


import carla, random, time

from examples.invertedai_traffic import spawn_pedestrians

class PedestrianManager:
    def __init__(self):
        pass

    @staticmethod
    def spawn_pedestrians(world, num_pedestrians=5):
        walker_list = list()
        walker_controllers = list()

        walker_bp = world.get_blueprint_library().filter('walker.pedestrian.*')
        for _ in range(num_pedestrians):
            spawn_point = random.choice(world.get_map().get_spawn_points())
            walker = world.spawn_actor(random.choice(walker_bp), spawn_point)
            walker_list.append(walker)

            walker_controller = world.get_world().spawn_actor(carla.commander, carla.Transform(), walker)
            walker_controllers.append(walker_controller)
            walker_controller.start()

        time.sleep(10)
        return walker_list, walker_controllers

    @staticmethod
    def log_pedestrians(walker: carla.Walker, vehicle: carla.Vehicle):
        if walker.get_location().distance(vehicle.get_location()) < 5.0:
            print(f"Pedestrian {walker.id} is near the vehicle.")

class CarManager:
    def __init__(self, num_cars:int=3):
        pass

    def spawn_cars(self, world, num_cars=3):
        cars_list = list()
        vehicle_bp = world.get_blueprint_library().filter('vehicle.*')

        for some in range(num_cars):
            spawn_point = random.choice(world.get_map().get_spawn_points())
            car = world.spawn_actor(random.choice(vehicle_bp), spawn_point)
            cars_list.append(car)

        return cars_list



if __name__ == "__main__":
    client = carla.Client('localhost', 2000)
    client.set_timeout(10)
    world = client.get_world()

    walkers, walker_controllers = spawn_pedestrians(world, num_pedestrians=5)
    cars = CarManager.spawn_cars(world)
    vehicle = world.get_actors().filter('vehicle')[0]
    print("starting simualation with manual control")

    """execute the code related to destroying all the cars and all the pedestrians
    log interactions. """