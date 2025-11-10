from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mcp import FastApiMCP

from app.routes import member

# FastAPI app already has title & description
app = FastAPI(
    title="Member Chatbot API",
    description="Ask questions about member eligibility, claims, HCCs, etc.",
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# cors settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include member routes
app.include_router(member.router, prefix="/member")

# Initialize MCP (just pass the app)
FastApiMCP(app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
