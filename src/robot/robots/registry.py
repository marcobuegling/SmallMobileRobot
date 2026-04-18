"""
All robots are registered here. 
This allows automatic mapping from config file input to the correct robot type.
"""

from basic_car import BasicCar


REGISTRY: dict[str, type] = {
    "basic_car_us_lt": BasicCar,
}