# LiveKit Agent Project

This project contains a LiveKit agent that provides assistant functionality with tool support.

## Fixed Issues

The main issue was in `api.py` where `ToolContext.__init__()` was missing the required `tools` argument. This has been fixed by:

1. Properly initializing the `AssistantFnc` class with a `tools` parameter
2. Defining the tools that the assistant can use
3. Implementing proper tool handling methods

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export LIVEKIT_API_KEY="your_api_key"
export LIVEKIT_API_SECRET="your_api_secret"
```

3. Run the agent in development mode:
```bash
python agent.py dev
```

## Project Structure

- `agent.py`: Main agent entrypoint and LiveKit integration
- `api.py`: Assistant function implementation with tool support
- `config.yaml`: Configuration file for the agent
- `requirements.txt`: Python dependencies

## Tools Available

The assistant currently supports:
- `search_web`: Search the web for current information
- `get_weather`: Get current weather information

## Error Resolution

The original error `TypeError: ToolContext.__init__() missing 1 required positional argument: 'tools'` has been resolved by properly passing the tools list to the parent class constructor.