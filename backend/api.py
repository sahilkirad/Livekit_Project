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