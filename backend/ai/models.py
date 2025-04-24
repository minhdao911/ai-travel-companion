import os
from enum import Enum
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set")

HELICONE_API_KEY = os.getenv("HELICONE_API_KEY")


class AIModelProvider(Enum):
    OPENAI = "openai"
    GOOGLE = "google"


class AIModel:
    def __init__(self, provider: AIModelProvider, model_id: str):
        self.provider = provider
        self.model_id = model_id

    def _get_temperature(self):
        match self.provider:
            case AIModelProvider.OPENAI:
                if self.model_id.startswith("gpt-4.1"):
                    return 0
                else:
                    return 1
            case AIModelProvider.GOOGLE:
                return 0

    def get_llm(self, **kwargs):
        if self.provider == AIModelProvider.OPENAI:
            trackingConfig = (
                {
                    "base_url": "https://oai.helicone.ai/v1",
                    "default_headers": {"Helicone-Auth": f"Bearer {HELICONE_API_KEY}"},
                }
                if HELICONE_API_KEY
                else {}
            )
            return ChatOpenAI(
                model=self.model_id,
                openai_api_key=OPENAI_API_KEY,
                temperature=self._get_temperature(),
                **trackingConfig,
                **kwargs,
            )
        elif self.provider == AIModelProvider.GOOGLE:
            trackingConfig = (
                {
                    "client_options": {
                        "api_endpoint": "https://gateway.helicone.ai",
                    },
                    "additional_headers": {
                        "helicone-auth": f"Bearer {HELICONE_API_KEY}",
                        "helicone-target-url": "https://generativelanguage.googleapis.com",
                    },
                    "transport": "rest",
                }
                if HELICONE_API_KEY
                else {}
            )
            return ChatGoogleGenerativeAI(
                google_api_key=GOOGLE_API_KEY,
                model=self.model_id,
                temperature=self._get_temperature(),
                **trackingConfig,
                **kwargs,
            )
