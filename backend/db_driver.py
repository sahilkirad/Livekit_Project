from dataclasses import dataclass
from typing import Optional

@dataclass
class Car:
    vin: str
    make: str
    model: str
    year: int

class DatabaseDriver:
    def __init__(self):
        # Simple in-memory database for demo purposes
        self.cars = {}
    
    def get_car_by_vin(self, vin: str) -> Optional[Car]:
        """Get car by VIN"""
        return self.cars.get(vin)
    
    def create_car(self, vin: str, make: str, model: str, year: int) -> Optional[Car]:
        """Create a new car entry"""
        car = Car(vin=vin, make=make, model=model, year=year)
        self.cars[vin] = car
        return car 