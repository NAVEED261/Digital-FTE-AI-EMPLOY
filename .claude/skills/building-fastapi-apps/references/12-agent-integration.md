# Agent Integration in FastAPI

> **Official Docs**: [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)

## Installation

```bash
pip install openai-agents
```

## Basic Agent Setup

```python
from agents import Agent, Runner

# Create an agent
agent = Agent(
    name="assistant",
    instructions="You are a helpful assistant that answers questions.",
    model="gpt-4"
)

# Run agent (non-streaming)
async def chat(message: str) -> str:
    result = await Runner.run(agent, message)
    return result.final_output
```

## Function Tool Decorator

Convert functions to agent tools:

```python
from agents import function_tool

@function_tool
def get_weather(city: str) -> str:
    """Get the current weather for a city.

    Args:
        city: The name of the city to get weather for.
    """
    # Simulate API call
    return f"Weather in {city}: Sunny, 72°F"

@function_tool
def search_products(query: str, max_results: int = 5) -> list[dict]:
    """Search for products in the catalog.

    Args:
        query: Search query string.
        max_results: Maximum number of results to return.
    """
    # Simulate database query
    return [
        {"id": 1, "name": f"Product matching '{query}'", "price": 29.99}
    ]
```

## Agent with Tools

```python
from agents import Agent, Runner, function_tool

@function_tool
def get_task_count(status: str) -> int:
    """Get the count of tasks with a given status."""
    # Integrate with your database
    return db.query(Task).filter(Task.status == status).count()

@function_tool
def create_task(title: str, priority: str = "medium") -> dict:
    """Create a new task."""
    task = Task(title=title, priority=priority)
    db.add(task)
    db.commit()
    return {"id": task.id, "title": task.title}

# Create agent with tools
task_agent = Agent(
    name="task-assistant",
    instructions="""You help users manage their tasks.
    Use the available tools to query and create tasks.
    Always confirm actions with the user.""",
    tools=[get_task_count, create_task]
)
```

## FastAPI Integration (Non-Streaming)

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents import Agent, Runner, function_tool

app = FastAPI()

# Define tools
@function_tool
def calculate(expression: str) -> float:
    """Evaluate a mathematical expression."""
    try:
        return eval(expression)  # Use a safe evaluator in production!
    except Exception as e:
        return f"Error: {e}"

# Create agent
calculator_agent = Agent(
    name="calculator",
    instructions="You are a helpful math assistant. Use the calculate tool for math.",
    tools=[calculate]
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        result = await Runner.run(calculator_agent, request.message)
        return ChatResponse(response=result.final_output)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Streaming with Runner.run_streamed

```python
from fastapi import FastAPI
from sse_starlette.sse import EventSourceResponse
from agents import Agent, Runner, function_tool

app = FastAPI()

@function_tool
def search_knowledge_base(query: str) -> str:
    """Search the knowledge base for information."""
    return f"Found relevant information about: {query}"

agent = Agent(
    name="knowledge-assistant",
    instructions="Help users find information. Search the knowledge base when needed.",
    tools=[search_knowledge_base]
)

@app.get("/chat/stream")
async def chat_stream(message: str):
    async def generate():
        try:
            async with Runner.run_streamed(agent, message) as stream:
                async for event in stream:
                    # Handle different event types
                    if hasattr(event, "text"):
                        yield {
                            "event": "token",
                            "data": event.text
                        }
                    elif hasattr(event, "tool_call"):
                        yield {
                            "event": "tool_call",
                            "data": event.tool_call.name
                        }

            yield {"event": "done", "data": ""}

        except Exception as e:
            yield {
                "event": "error",
                "data": str(e)
            }

    return EventSourceResponse(generate())
```

## API-to-Tool Conversion Pattern

Convert existing FastAPI endpoints to agent tools:

```python
from agents import function_tool
from sqlmodel import Session

# Original endpoint logic
def get_tasks_from_db(session: Session, status: str | None = None) -> list[dict]:
    query = select(Task)
    if status:
        query = query.where(Task.status == status)
    tasks = session.exec(query).all()
    return [t.model_dump() for t in tasks]

# Wrap as tool (with session from app.state or context)
@function_tool
def list_tasks(status: str | None = None) -> list[dict]:
    """List all tasks, optionally filtered by status.

    Args:
        status: Filter by task status (todo, in_progress, done).
    """
    with Session(engine) as session:
        return get_tasks_from_db(session, status)

@function_tool
def get_task(task_id: int) -> dict:
    """Get a specific task by ID.

    Args:
        task_id: The ID of the task to retrieve.
    """
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task:
            return {"error": f"Task {task_id} not found"}
        return task.model_dump()

@function_tool
def update_task_status(task_id: int, status: str) -> dict:
    """Update a task's status.

    Args:
        task_id: The ID of the task to update.
        status: New status (todo, in_progress, done).
    """
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task:
            return {"error": f"Task {task_id} not found"}
        task.status = status
        session.commit()
        return {"success": True, "task": task.model_dump()}
```

## Multi-Agent Patterns

```python
from agents import Agent, Runner, function_tool

# Specialist agents
researcher = Agent(
    name="researcher",
    instructions="Research topics and provide detailed information.",
    tools=[search_web, search_docs]
)

writer = Agent(
    name="writer",
    instructions="Write clear, well-structured content.",
    tools=[]
)

# Coordinator agent that delegates
@function_tool
async def delegate_to_researcher(question: str) -> str:
    """Delegate a research question to the researcher agent."""
    result = await Runner.run(researcher, question)
    return result.final_output

@function_tool
async def delegate_to_writer(content: str, style: str) -> str:
    """Delegate writing to the writer agent."""
    prompt = f"Write the following in {style} style:\n\n{content}"
    result = await Runner.run(writer, prompt)
    return result.final_output

coordinator = Agent(
    name="coordinator",
    instructions="""You coordinate tasks between specialists.
    Use the researcher for finding information.
    Use the writer for creating content.""",
    tools=[delegate_to_researcher, delegate_to_writer]
)
```

## Structured Output from Agents

```python
from pydantic import BaseModel
from agents import Agent, Runner

class TaskAnalysis(BaseModel):
    summary: str
    priority_recommendation: str
    estimated_hours: float
    next_steps: list[str]

analysis_agent = Agent(
    name="task-analyzer",
    instructions="""Analyze tasks and provide structured recommendations.
    Always return valid JSON matching the TaskAnalysis schema.""",
    model="gpt-4"
)

async def analyze_task(description: str) -> TaskAnalysis:
    prompt = f"""Analyze this task and return JSON:
    Task: {description}

    Return format:
    {{"summary": "...", "priority_recommendation": "...", "estimated_hours": N, "next_steps": ["..."]}}
    """

    result = await Runner.run(analysis_agent, prompt)

    # Parse the output
    import json
    data = json.loads(result.final_output)
    return TaskAnalysis(**data)
```

## Error Handling in Agent Endpoints

```python
from fastapi import HTTPException
from agents import Agent, Runner, AgentError

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        result = await Runner.run(agent, request.message)
        return {"response": result.final_output}

    except AgentError as e:
        # Agent-specific errors
        raise HTTPException(
            status_code=500,
            detail=f"Agent error: {e}"
        )

    except TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Agent response timed out"
        )

    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error in chat: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )
```

## Complete Agent Chat Endpoint

```python
from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from agents import Agent, Runner, function_tool
from sqlmodel import Session

app = FastAPI()

# Database tools
@function_tool
def search_tasks(query: str) -> list[dict]:
    """Search tasks by title or description."""
    with Session(engine) as session:
        tasks = session.exec(
            select(Task).where(Task.title.contains(query))
        ).all()
        return [t.model_dump() for t in tasks]

@function_tool
def get_task_stats() -> dict:
    """Get task statistics."""
    with Session(engine) as session:
        total = session.exec(select(func.count(Task.id))).one()
        done = session.exec(
            select(func.count(Task.id)).where(Task.status == "done")
        ).one()
        return {
            "total": total,
            "completed": done,
            "completion_rate": f"{(done/total*100):.1f}%" if total > 0 else "0%"
        }

# Create agent
task_assistant = Agent(
    name="task-assistant",
    instructions="""You are a helpful task management assistant.
    Help users:
    - Search and find tasks
    - Get statistics about their tasks
    - Provide productivity tips

    Be concise and helpful.""",
    tools=[search_tasks, get_task_stats],
    model="gpt-4"
)

class ChatMessage(BaseModel):
    role: str
    content: str

@app.post("/agent/chat")
async def agent_chat(messages: list[ChatMessage]):
    """Non-streaming agent chat."""
    # Convert to single prompt (or use conversation history)
    user_message = messages[-1].content

    result = await Runner.run(task_assistant, user_message)

    return {
        "role": "assistant",
        "content": result.final_output
    }

@app.post("/agent/chat/stream")
async def agent_chat_stream(
    messages: list[ChatMessage],
    request: Request
):
    """Streaming agent chat."""
    user_message = messages[-1].content

    async def generate():
        try:
            async with Runner.run_streamed(task_assistant, user_message) as stream:
                async for event in stream:
                    if await request.is_disconnected():
                        break

                    if hasattr(event, "text") and event.text:
                        yield {
                            "event": "token",
                            "data": event.text
                        }
                    elif hasattr(event, "tool_call"):
                        yield {
                            "event": "tool_use",
                            "data": f"Using tool: {event.tool_call.name}"
                        }

            yield {"event": "done", "data": ""}

        except Exception as e:
            yield {
                "event": "error",
                "data": str(e)
            }

    return EventSourceResponse(generate())
```

## Tool Best Practices

1. **Clear docstrings**: Agents use docstrings to understand tools
2. **Type hints**: Help agents understand expected inputs
3. **Return useful data**: Include enough context for the agent
4. **Handle errors gracefully**: Return error messages, don't raise
5. **Keep tools focused**: One task per tool
6. **Use descriptive names**: `get_user_orders` not `fetch_data`
