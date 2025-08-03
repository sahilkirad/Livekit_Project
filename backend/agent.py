
import asyncio
import logging

from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import openai, silero

from api import AssistantFnc, get_video_track

logger = logging.getLogger("voice-assistant")


async def entrypoint(ctx: JobContext):
    initial_ctx = llm.ChatContext().append(
        role="system",
        text=(
            "You are a voice assistant created by LiveKit. Your interface with users will be voice. "
            "You should use short and concise responses, and avoiding usage of unpronounceable punctuation."
        ),
    )

    logger.info(f"connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Wait for the first participant to connect
    participant = await ctx.wait_for_participant()
    logger.info(f"starting voice assistant for participant {participant.identity}")

    # Initialize the assistant function context
    assistant_fnc = AssistantFnc()

    # Create the voice assistant
    assistant = VoiceAssistant(
        vad=silero.VAD.load(),
        stt=openai.STT(),
        llm=openai.LLM(),
        tts=openai.TTS(),
        chat_ctx=initial_ctx,
        fnc_ctx=assistant_fnc,
    )

    # Start the assistant
    assistant.start(ctx.room, participant)

    # Get video track if available
    try:
        video_track = await asyncio.wait_for(get_video_track(ctx.room), timeout=10.0)
        logger.info("Video track found")
    except asyncio.TimeoutError:
        logger.info("No video track found within timeout")

    await assistant.aclose()


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
        ),
    )

from __future__ import annotations
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm,
    Agent
)
from livekit.agents.llm import realtime
from dotenv import load_dotenv
from api import AssistantFnc
from prompts import WELCOME_MESSAGE, INSTRUCTIONS, LOOKUP_VIN_MESSAGE
import os

load_dotenv()

async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.SUBSCRIBE_ALL)
    await ctx.wait_for_participant()
    
    capabilities = realtime.RealtimeCapabilities(
        message_truncation=True,
        turn_detection=True,
        user_transcription=True,
        auto_tool_reply_generation=True,
        audio_output=True
    )
    model = realtime.RealtimeModel(capabilities=capabilities)
    assistant_fnc = AssistantFnc()
    assistant = Agent(model=model, fnc_ctx=assistant_fnc)
    assistant.start(ctx.room)
    
    session = model.sessions[0]
    session.conversation.item.create(  #adding a new chat message into a kind of context or current session
        llm.ChatMessage(
            role="assistant",
            content=WELCOME_MESSAGE
        )
    )
    session.response.create()
    
    @session.on("user_speech_committed")
    def on_user_speech_committed(msg: llm.ChatMessage):
        if isinstance(msg.content, list):
            msg.content = "\n".join("[image]" if isinstance(x, llm.ChatImage) else x for x in msg)
            
        if assistant_fnc.has_car():
            handle_query(msg)
        else:
            find_profile(msg)
        
    def find_profile(msg: llm.ChatMessage):
        session.conversation.item.create(
            llm.ChatMessage(
                role="system",
                content=LOOKUP_VIN_MESSAGE(msg)
            )
        )
        session.response.create()
        
    def handle_query(msg: llm.ChatMessage):
        session.conversation.item.create(
            llm.ChatMessage(
                role="user",
                content=msg.content
            )
        )
        session.response.create()
    
if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))

