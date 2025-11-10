from openai import OpenAI
from app.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def interpret_query(question: str, member: dict):
    """
    Optional: Use OpenAI GPT to parse natural language queries
    and return structured JSON response.
    """
    prompt = f"""
    You are an assistant for a member database.
    Member data: {member}
    Question: {question}
    Return the answer in concise JSON format.
    """
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

