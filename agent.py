import asyncio
import logging
from livekit.agents import JobContext
from api import AssistantFnc

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def entrypoint(job_ctx: JobContext):
    """Main entrypoint for the LiveKit agent"""
    try:
        # Initialize the assistant function
        assistant_fnc = AssistantFnc()
        
        # Get the room from the job context
        room = job_ctx.room
        
        # Set up event handlers for the room
        @room.on("participant_connected")
        async def on_participant_connected(participant):
            logger.info(f"Participant {participant.identity} connected")
            await room.local_participant.publish_data(
                "Welcome to the assistant! How can I help you today?",
                topic="chat"
            )
        
        @room.on("data_received")
        async def on_data_received(payload, participant, topic):
            if topic == "chat":
                message = payload.decode('utf-8')
                logger.info(f"Received message from {participant.identity}: {message}")
                
                # Process the message using the assistant
                response = await assistant_fnc.process_message(message)
                
                # Send the response back
                await room.local_participant.publish_data(
                    response.encode('utf-8'),
                    topic="chat"
                )
        
        # Keep the agent running
        await asyncio.Event().wait()
        
    except Exception as e:
        logger.error(f"Error in entrypoint: {e}")
        raise

if __name__ == "__main__":
    # This is for local development/testing
    asyncio.run(entrypoint(None))