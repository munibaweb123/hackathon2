"""Streaming helpers for ChatKit using Server-Sent Events (SSE) in AI Chatbot feature."""

import asyncio
from typing import AsyncGenerator, Dict, Any
from fastapi import Response
from uuid import UUID


async def send_sse_event(event_type: str, data: Dict[str, Any]) -> str:
    """
    Format data as Server-Sent Event.

    Args:
        event_type: Type of the event
        data: Data to send

    Returns:
        Formatted SSE string
    """
    return f"data: {event_type}:{data}\n\n"


async def stream_response(response_generator: AsyncGenerator[str, None]) -> Response:
    """
    Stream response to client using Server-Sent Events.

    Args:
        response_generator: Async generator producing response chunks

    Returns:
        Streaming response
    """
    async def generate_stream():
        async for chunk in response_generator:
            yield f"data: {chunk}\n\n"

    return Response(
        content=generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )


async def create_sse_stream(data_generator: AsyncGenerator[Dict[str, Any], None]) -> Response:
    """
    Create an SSE stream from a data generator.

    Args:
        data_generator: Async generator producing data dictionaries

    Returns:
        Streaming response with SSE format
    """
    async def event_stream():
        async for data in data_generator:
            yield f"data: {data}\n\n"

    return Response(
        content=event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "X-Accel-Buffering": "no",
        }
    )


async def simulate_streaming_response(text: str, delay: float = 0.05) -> AsyncGenerator[str, None]:
    """
    Simulate streaming response by yielding text chunks with delay.

    Args:
        text: Text to stream
        delay: Delay between chunks in seconds

    Yields:
        Text chunks
    """
    words = text.split()
    for i, word in enumerate(words):
        await asyncio.sleep(delay)
        # Yield the word with proper SSE formatting
        yield f'data: {{"token": "{word}", "index": {i}, "done": {i == len(words) - 1}}}\n\n'


class StreamManager:
    """Class to manage streaming responses."""

    def __init__(self):
        self._queue = asyncio.Queue()

    async def add_message(self, message: Dict[str, Any]):
        """Add a message to the stream queue."""
        await self._queue.put(message)

    async def stream_messages(self) -> AsyncGenerator[str, None]:
        """Stream messages from the queue."""
        while True:
            try:
                # Wait for a message with timeout
                message = await asyncio.wait_for(self._queue.get(), timeout=30.0)
                yield f"data: {message}\n\n"
            except asyncio.TimeoutError:
                # Send a ping to keep the connection alive
                yield ": ping\n\n"
                continue
            except Exception:
                # If there's an error, break the loop
                break

    def close(self):
        """Close the stream manager."""
        # Put a sentinel value to signal end of stream
        self._queue.put_nowait(None)