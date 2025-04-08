import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set")

HELICONE_API_KEY = os.getenv("HELICONE_API_KEY")

trackingConfig = {
    "base_url": "https://oai.helicone.ai/v1",
    "default_headers": {
        "Helicone-Auth": f"Bearer {HELICONE_API_KEY}"
    } 
} if HELICONE_API_KEY else {}

model = ChatOpenAI(
    model="gpt-4o-mini",
    openai_api_key=OPENAI_API_KEY,
    temperature=0,
    **trackingConfig
)
