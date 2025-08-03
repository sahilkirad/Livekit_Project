from livekit.agents import llm
from livekit.agents.llm import tool_context
import enum
from typing import Annotated
import logging
from db_driver import DatabaseDriver

logger = logging.getLogger("user-data")
logger.setLevel(logging.INFO)

DB = DatabaseDriver()

class CarDetails(enum.Enum):
    VIN = "vin"
    Make = "make"
    Model = "model"
    Year = "year"
    

class AssistantFnc(tool_context.ToolContext):
    def __init__(self):
        super().__init__()
        
        self._car_details = {
            CarDetails.VIN: "",
            CarDetails.Make: "",
            CarDetails.Model: "",
            CarDetails.Year: ""
        }
    
    def get_car_str(self):
        car_str = ""
        for key, value in self._car_details.items():
            car_str += f"{key}: {value}\n"
            
        return car_str
    
    @tool_context.function_tool(description="lookup a car by its vin")
    def lookup_car(self, vin: str):
        logger.info("lookup car - vin: %s", vin)
        
        result = DB.get_car_by_vin(vin)
        if result is None:
            return "Car not found"
        
        self._car_details = {
            CarDetails.VIN: result.vin,
            CarDetails.Make: result.make,
            CarDetails.Model: result.model,
            CarDetails.Year: result.year
        }
        
        return f"The car details are: {self.get_car_str()}"
    
    @tool_context.function_tool(description="get the details of the current car")
    def get_car_details(self):
        logger.info("get car  details")
        return f"The car details are: {self.get_car_str()}"
    
    @tool_context.function_tool(description="create a new car")
    def create_car(
        self, 
        vin: str,
        make: str,
        model: str,
        year: int
    ):
        logger.info("create car - vin: %s, make: %s, model: %s, year: %s", vin, make, model, year)
        result = DB.create_car(vin, make, model, year)
        if result is None:
            return "Failed to create car"
        
        self._car_details = {
            CarDetails.VIN: result.vin,
            CarDetails.Make: result.make,
            CarDetails.Model: result.model,
            CarDetails.Year: result.year
        }
        
        return "car created!"
    
    def has_car(self):
        return self._car_details[CarDetails.VIN] != ""