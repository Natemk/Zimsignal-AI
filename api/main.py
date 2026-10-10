from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from langchain_core.messages import HumanMessage
from orchestration.supervisor import create_supervisor_graph

# 1. Initialize FastAPI app with descriptive metadata
app = FastAPI(
    title="ZimSignal AI Supervisor API",
    description="Production API wrapper for multi-agent RAG supervision, intent routing, and thread-persistent memory.",
    version="1.0.1"
)

# 2. Add CORS Middleware (Allows frontends like React Native/Web to communicate with this backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Compile the LangGraph supervisor graph globally upon startup
supervisor_app = create_supervisor_graph()

# 4. Define Request Body Schema using Pydantic
class ChatRequest(BaseModel):
    message: str = Field(..., description="The user query or prompt sent to the supervisor agent.")
    thread_id: Optional[str] = Field("default_thread", description="Unique session thread ID for multi-turn thread memory persistence.")

# 5. Define Response Schema
class ChatResponse(BaseModel):
    thread_id: str
    response: str

# 6. Root Endpoint (Fixes the 404 Not Found on '/')
@app.get("/", tags=["General"])
async def read_root():
    return {
        "service": "ZimSignal AI Supervisor API",
        "status": "online",
        "documentation": "/docs",
        "health_check": "/health"
    }

# 7. Health Check Endpoint
@app.get("/health", tags=["General"])
async def health_check():
    return {"status": "healthy", "database": "connected", "graph": "compiled"}

# 8. Main Chat Endpoint
@app.post("/chat", response_model=ChatResponse, tags=["Agent Interaction"])
async def chat_endpoint(payload: ChatRequest):
    """
    Receives user prompts, applies thread checkpointing configuration for memory, 
    and invokes the LangGraph supervisor multi-agent graph.
    """
    try:
        # Configure thread checkpointing config for LangGraph memory saver
        config = {"configurable": {"thread_id": payload.thread_id}}
        
        # Invoke the compiled supervisor graph
        result = supervisor_app.invoke(
            {"messages": [HumanMessage(content=payload.message)]}, 
            config=config
        )
        
        # Extract the final synthesized AI message response
        final_message = result["messages"][-1].content
        
        return ChatResponse(
            thread_id=payload.thread_id,
            response=final_message
        )
        
    except Exception as e:
        # Log error in production terminal and return clean HTTP 500
        print(f"[API ERROR] Failed to process chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal agent execution error: {str(e)}")