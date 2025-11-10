from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from app.routes import member

# FastAPI app already has title & description
app = FastAPI(
    title="Member Chatbot API",
    description="Ask questions about member eligibility, claims, HCCs, etc."
)

# Include member routes
app.include_router(member.router, prefix="/member")

# Initialize MCP (just pass the app)
FastApiMCP(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

