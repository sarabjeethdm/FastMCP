from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "dev_v2")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

