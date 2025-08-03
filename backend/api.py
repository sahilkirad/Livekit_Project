
import asyncio
import logging
from typing import Annotated

from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm,
)
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import openai, silero
from livekit.agents.llm import ToolContext


logger = logging.getLogger("voice-assistant")


class AssistantFnc(ToolContext):
    def __init__(self):
        # Initialize with an empty tools list - you can add specific tools here
        super().__init__(tools=[])

    @llm.ai_callable()
    async def get_weather(
        self,
        location: Annotated[str, llm.TypeInfo(description="The location to get weather for")]
    ):
        """Get the current weather for a location."""
        logger.info(f"Getting weather for {location}")
        # This is a placeholder - replace with actual weather API call
        return f"The weather in {location} is sunny and 72°F"

    @llm.ai_callable()
    async def set_volume(
        self,
        volume: Annotated[int, llm.TypeInfo(description="Volume level from 0 to 100")]
    ):
        """Set the volume level."""
        logger.info(f"Setting volume to {volume}")
        # This is a placeholder - replace with actual volume control
        return f"Volume set to {volume}%"


async def get_video_track(room):
    """Get the first video track from the room."""
    video_track = asyncio.create_future()

    for _, participant in room.remote_participants.items():
        for _, track_publication in participant.track_publications.items():
            if track_publication.track is not None and track_publication.kind == "video":
                video_track.set_result(track_publication.track)
                return video_track

    def on_track_subscribed(track, publication, participant):
        if publication.kind == "video":
            video_track.set_result(track)

    room.on("track_subscribed", on_track_subscribed)
    return await video_track

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
