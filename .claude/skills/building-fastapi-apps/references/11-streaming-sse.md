# Streaming & SSE in FastAPI

> **Official Docs**: [sse-starlette](https://github.com/sysid/sse-starlette)

## Installation

```bash
pip install sse-starlette
```

## What is SSE (Server-Sent Events)?

SSE is a standard for streaming data from server to client over HTTP:
- One-way communication (server to client)
- Auto-reconnection built into browsers
- Simpler than WebSockets for streaming use cases
- Perfect for: LLM responses, live updates, notifications

## Basic Async Generator

```python
import asyncio

async def number_generator():
    """Simple async generator."""
    for i in range(10):
        yield f"Number: {i}"
        await asyncio.sleep(1)
```

## Basic SSE Endpoint

```python
from fastapi import FastAPI
from sse_starlette.sse import EventSourceResponse

app = FastAPI()

async def event_stream():
    """Generate SSE events."""
    for i in range(10):
        yield {"data": f"Message {i}"}
        await asyncio.sleep(1)

@app.get("/stream")
async def stream():
    return EventSourceResponse(event_stream())
```

## SSE Event Format

```python
async def event_stream():
    # Simple data event
    yield {"data": "Hello"}

    # Event with type
    yield {
        "event": "message",
        "data": "Hello World"
    }

    # Event with ID (for reconnection)
    yield {
        "event": "update",
        "data": '{"count": 42}',
        "id": "msg-123"
    }

    # Retry interval (milliseconds)
    yield {
        "event": "config",
        "data": "Setting retry",
        "retry": 5000
    }
```

## LLM Response Streaming

```python
from fastapi import FastAPI
from sse_starlette.sse import EventSourceResponse
import openai

app = FastAPI()

async def stream_openai_response(prompt: str):
    """Stream OpenAI response token by token."""
    client = openai.AsyncOpenAI()

    stream = await client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )

    async for chunk in stream:
        if chunk.choices[0].delta.content:
            yield {
                "event": "token",
                "data": chunk.choices[0].delta.content
            }

    # Signal completion
    yield {"event": "done", "data": ""}

@app.get("/chat")
async def chat(prompt: str):
    return EventSourceResponse(stream_openai_response(prompt))
```

## Error Handling in Streams

```python
async def safe_stream():
    """Stream with error handling."""
    try:
        for i in range(100):
            if i == 50:
                raise ValueError("Simulated error")

            yield {"data": f"Item {i}"}
            await asyncio.sleep(0.1)

    except Exception as e:
        # Send error event before stopping
        yield {
            "event": "error",
            "data": str(e)
        }

    finally:
        # Always send completion signal
        yield {"event": "done", "data": ""}
```

## Client Disconnection Detection

```python
from fastapi import Request
from sse_starlette.sse import EventSourceResponse

@app.get("/stream")
async def stream(request: Request):
    async def generate():
        try:
            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    print("Client disconnected")
                    break

                yield {"data": "heartbeat"}
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            print("Stream cancelled")

    return EventSourceResponse(generate())
```

## Streaming with Database Queries

```python
from sqlmodel import Session, select

async def stream_tasks(session: Session):
    """Stream tasks from database."""
    # Initial batch
    tasks = session.exec(select(Task).limit(100)).all()
    for task in tasks:
        yield {
            "event": "task",
            "data": task.model_dump_json()
        }
        await asyncio.sleep(0.01)  # Small delay to prevent overwhelming

    yield {"event": "done", "data": ""}

@app.get("/tasks/stream")
async def stream_tasks_endpoint(session: Session = Depends(get_session)):
    return EventSourceResponse(stream_tasks(session))
```

## Progress Reporting

```python
async def process_with_progress(items: list):
    """Stream progress updates."""
    total = len(items)

    for i, item in enumerate(items):
        # Process item
        await process_item(item)

        # Report progress
        progress = ((i + 1) / total) * 100
        yield {
            "event": "progress",
            "data": f'{{"current": {i + 1}, "total": {total}, "percent": {progress:.1f}}}'
        }

    yield {
        "event": "complete",
        "data": '{"status": "success"}'
    }

@app.post("/process")
async def process_items(items: list[str]):
    return EventSourceResponse(process_with_progress(items))
```

## Multiple Event Types

```python
async def multi_event_stream(user_id: int):
    """Stream different event types."""
    # Initial state
    yield {
        "event": "init",
        "data": '{"status": "connected"}'
    }

    while True:
        # Check for notifications
        notifications = await get_notifications(user_id)
        for n in notifications:
            yield {
                "event": "notification",
                "data": n.model_dump_json()
            }

        # Check for messages
        messages = await get_messages(user_id)
        for m in messages:
            yield {
                "event": "message",
                "data": m.model_dump_json()
            }

        # Heartbeat
        yield {
            "event": "heartbeat",
            "data": '{"time": "' + datetime.utcnow().isoformat() + '"}'
        }

        await asyncio.sleep(5)
```

## StreamingResponse (Non-SSE)

For raw streaming without SSE format:

```python
from fastapi.responses import StreamingResponse

async def generate_csv():
    """Stream CSV data."""
    yield "id,name,value\n"
    for i in range(1000):
        yield f"{i},item_{i},{i * 10}\n"
        await asyncio.sleep(0.001)

@app.get("/export.csv")
async def export_csv():
    return StreamingResponse(
        generate_csv(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=export.csv"}
    )
```

## File Streaming

```python
from fastapi.responses import StreamingResponse
import aiofiles

async def stream_file(file_path: str):
    """Stream large file in chunks."""
    async with aiofiles.open(file_path, "rb") as f:
        while chunk := await f.read(8192):  # 8KB chunks
            yield chunk

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = f"/files/{filename}"
    return StreamingResponse(
        stream_file(file_path),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
```

## Client-Side JavaScript

```javascript
// Basic EventSource
const eventSource = new EventSource('/stream');

eventSource.onmessage = (event) => {
    console.log('Message:', event.data);
};

eventSource.onerror = (error) => {
    console.error('Error:', error);
    eventSource.close();
};

// With event types
eventSource.addEventListener('token', (event) => {
    document.getElementById('output').textContent += event.data;
});

eventSource.addEventListener('done', (event) => {
    console.log('Stream complete');
    eventSource.close();
});

eventSource.addEventListener('error', (event) => {
    console.error('Stream error:', event.data);
    eventSource.close();
});
```

## Testing Streaming Endpoints

```python
import pytest
from fastapi.testclient import TestClient

def test_sse_stream(client):
    """Test SSE endpoint."""
    with client.stream("GET", "/stream") as response:
        assert response.status_code == 200

        events = []
        for line in response.iter_lines():
            if line.startswith("data:"):
                events.append(line[5:].strip())

        assert len(events) > 0

def test_stream_content(client):
    """Test stream produces expected events."""
    response = client.get("/stream")
    content = response.text

    assert "event: message" in content
    assert "data:" in content
```

## Complete Chat Streaming Example

```python
from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
import openai

app = FastAPI()

class ChatMessage(BaseModel):
    role: str
    content: str

@app.post("/chat/stream")
async def chat_stream(
    messages: list[ChatMessage],
    request: Request
):
    async def generate():
        client = openai.AsyncOpenAI()

        try:
            stream = await client.chat.completions.create(
                model="gpt-4",
                messages=[m.model_dump() for m in messages],
                stream=True
            )

            async for chunk in stream:
                # Check for client disconnect
                if await request.is_disconnected():
                    break

                content = chunk.choices[0].delta.content
                if content:
                    yield {
                        "event": "token",
                        "data": content
                    }

            yield {"event": "done", "data": ""}

        except Exception as e:
            yield {
                "event": "error",
                "data": str(e)
            }

    return EventSourceResponse(generate())
```

## SSE vs WebSocket

| Feature | SSE | WebSocket |
|---------|-----|-----------|
| Direction | Server → Client | Bidirectional |
| Protocol | HTTP | WS |
| Reconnection | Auto (browser) | Manual |
| Binary data | No | Yes |
| Complexity | Simple | Complex |
| Use case | Streaming, updates | Real-time chat |

**Use SSE when:**
- Server pushes data to client
- LLM response streaming
- Live dashboards
- Notifications

**Use WebSocket when:**
- Bidirectional communication
- Low latency required
- Binary data transfer
- Gaming, collaborative editing
