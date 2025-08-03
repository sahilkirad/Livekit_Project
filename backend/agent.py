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