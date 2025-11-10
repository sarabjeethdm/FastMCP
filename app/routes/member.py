import json

from fastapi import APIRouter, Body, Header
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
    {
        "name": "get_members_by_delta_riskscore",
        "description": "Get all members filtered by deltaRiskScore comparison",
        "parameters": {
            "type": "object",
            "properties": {
                "operator": {
                    "type": "string",
                    "enum": ["lt", "lte", "eq", "gte", "gt"],
                    "description": "Comparison operator: lt, lte, eq, gte, gt",
                },
                "value": {
                    "type": "number",
                    "description": "Threshold deltaRiskScore value to compare against",
                },
            },
            "required": ["operator", "value"],
        },
    },
    # uncomment this if want combine backend functions
    # {
    #     "name": "get_members_by_riskscore_and_eligibility",
    #     "description": "Get members whose delta risk score meets a threshold and who are eligible for a given year",
    #     "parameters": {
    #         "type": "object",
    #         "properties": {
    #             "operator": {
    #                 "type": "string",
    #                 "enum": ["lt", "lte", "eq", "gte", "gt"],
    #                 "description": "Comparison operator for deltaRiskScore",
    #             },
    #             "value": {
    #                 "type": "number",
    #                 "description": "Threshold deltaRiskScore value",
    #             },
    #             "year": {
    #                 "type": "string",
    #                 "description": "Eligibility year (e.g., '2024')",
    #             },
    #         },
    #         "required": ["operator", "value", "year"],
    #     },
    # },
]

# Map tool execution to Python functions
tool_functions = {
    "get_eligibility": lambda params, headers={}: member_service.get_member_eligibility_by_name(
        params["name"],
        params["year"],
        health_plan_id=headers.get("healthPlanId"),
        year_of_service=headers.get("yearOfService"),
    ),
    "get_claims": lambda params, headers={}: member_service.get_member_claims_by_name(
        params["name"],
        health_plan_id=headers.get("healthPlanId"),
        year_of_service=headers.get("yearOfService"),
    ),
    "get_hccs": lambda params, headers={}: member_service.get_member_hccs_by_name(
        params["name"],
        health_plan_id=headers.get("healthPlanId"),
        year_of_service=headers.get("yearOfService"),
    ),
    "get_members_by_eligibility_year": lambda params, headers={}: member_service.get_members_by_eligibility_year(
        params["year"],
        health_plan_id=headers.get("healthPlanId"),
        year_of_service=headers.get("yearOfService"),
    ),
    "get_all_members": lambda params, headers={}: member_service.get_all_members(
        limit=params.get("limit", 50),
        health_plan_id=headers.get("healthPlanId"),
        year_of_service=headers.get("yearOfService"),
    ),
    "get_members_by_delta_riskscore": lambda params, headers={}: member_service.get_members_by_delta_riskscore(
        params["operator"],
        params["value"],
        health_plan_id=headers.get("healthPlanId"),
        year_of_service=headers.get("yearOfService"),
    ),
    "get_members_by_riskscore_and_eligibility": lambda params, headers={}: member_service.get_members_by_riskscore_and_eligibility(
        params["operator"],
        params["value"],
        params["year"],
        health_plan_id=headers.get("healthPlanId"),
        year_of_service=headers.get("yearOfService"),
    ),
}


# combine backend or single query tools
# @router.post("/query")
# async def member_query(
#     query: dict = Body(...),
#     health_plan_id: str | None = Header(None, alias="healthplanid"),
#     year_of_service: int | None = Header(None, alias="yearofservice"),
# ):
#     user_question = query.get("question", "")
#
#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[{"role": "user", "content": user_question}],
#         functions=tools,
#         function_call="auto",
#     )
#
#     message = response.choices[0].message
#
#     headers = {"healthPlanId": health_plan_id, "yearOfService": year_of_service}
#     print(f"headers : {headers}")
#     # Check if OpenAI wants to call a function
#     if message.function_call:
#         func_name = message.function_call.name
#         import json
#
#         params = json.loads(message.function_call.arguments)
#         result = tool_functions[func_name](params, headers=headers)
#         return JSONResponse({"answer": result})
#
#     # Otherwise return plain text
#     return JSONResponse({"answer": message.content})


# Using LLM to chain multiple tools
@router.post("/query")
async def member_query(
    query: dict = Body(...),
    health_plan_id: str | None = Header(None, alias="healthplanid"),
    year_of_service: int | None = Header(None, alias="yearofservice"),
):
    """
    Handles chained function calls by the LLM.
    """
    user_question = query.get("question", "")
    headers = {"healthPlanId": health_plan_id, "yearOfService": year_of_service}

    # initial message context
    messages = [
        {
            "role": "system",
            "content": (
                "You are a data assistant that can access member information "
                "using provided tools. If multiple filters are requested, call "
                "multiple functions step by step and combine their results logically "
                "before answering."
            ),
        },
        {"role": "user", "content": user_question},
    ]

    # loop to allow multiple tool calls
    for _ in range(6):  # cap iterations to avoid infinite loops
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            functions=tools,
            function_call="auto",
        )

        message = response.choices[0].message

        # model wants to call a function/tool
        if message.function_call:
            func_name = message.function_call.name
            params = json.loads(message.function_call.arguments)
            print(f"Tool call: {func_name} with {params}")

            # execute your backend tool
            if func_name in tool_functions:
                result = tool_functions[func_name](params, headers=headers)
                # feed result back into conversation
                messages.append(message)
                messages.append(
                    {
                        "role": "function",
                        "name": func_name,
                        "content": json.dumps(result),
                    }
                )
                continue  # go back to let GPT decide next tool
            else:
                return JSONResponse({"error": f"Unknown function {func_name}"}, status_code=400)

        # model finished reasoning
        if message.content:
            return JSONResponse({"answer": message.content})

    return JSONResponse({"answer": "Could not complete the multi-step query."})
