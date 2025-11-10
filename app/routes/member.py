from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
from openai import OpenAI

from app.config import OPENAI_API_KEY
from app.services import member_service

router = APIRouter()
client = OpenAI(api_key=OPENAI_API_KEY)

# Define tools OpenAI can call
tools = [
    {
        "name": "get_eligibility",
        "description": "Get member eligibility for a given year",
        "parameters": {
            "type": "object",
            "properties": {
                "year": {
                    "type": "string",
                    "description": "Year for eligibility, e.g., 2024",
                },
                "name": {"type": "string", "description": "Member full name"},
            },
            "required": ["year", "name"],
        },
    },
    {
        "name": "get_claims",
        "description": "Get all claims for a member",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Member full name"}
            },
            "required": ["name"],
        },
    },
    {
        "name": "get_hccs",
        "description": "Get all HCC codes for a member",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Member full name"}
            },
            "required": ["name"],
        },
    },
    {
        "name": "get_members_by_eligibility_year",
        "description": "Get all members eligible for a given year",
        "parameters": {
            "type": "object",
            "properties": {
                "year": {
                    "type": "string",
                    "description": "Eligibility year, e.g., 2024",
                }
            },
            "required": ["year"],
        },
    },
    {
        "name": "get_all_members",
        "description": "Get all members (up to an optional limit)",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of members to return",
                }
            },
            "required": [],
        },
    },
]

# Map tool execution to Python functions
tool_functions = {
    "get_eligibility": lambda params: member_service.get_member_eligibility_by_name(
        params["name"], params["year"]
    ),
    "get_claims": lambda params: member_service.get_member_claims_by_name(
        params["name"]
    ),
    "get_hccs": lambda params: member_service.get_member_hccs_by_name(params["name"]),
    "get_members_by_eligibility_year": lambda params: member_service.get_members_by_eligibility_year(
        params["year"]
    ),
    "get_all_members": lambda params: member_service.get_all_members(
        limit=params.get("limit", 50)
    ),
}


@router.post("/query")
async def member_query(query: dict = Body(...)):
    user_question = query.get("question", "")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": user_question}],
        functions=tools,
        function_call="auto",
    )

    message = response.choices[0].message

    # Check if OpenAI wants to call a function
    if message.function_call:
        func_name = message.function_call.name
        import json

        params = json.loads(message.function_call.arguments)
        result = tool_functions[func_name](params)
        return JSONResponse({"answer": result})

    # Otherwise return plain text
    return JSONResponse({"answer": message.content})
