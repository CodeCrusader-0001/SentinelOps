import json
import time
from typing import Optional, Type, TypeVar
from pydantic import BaseModel
from backend.app.ai.base import BaseLLMProvider
from backend.app.core.config import settings
from backend.app.core.logging import logger

T = TypeVar("T", bound=BaseModel)

class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or settings.GEMINI_MODEL
        self.client = None
        
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
                logger.info(f"Initialized Gemini Client with model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize google-genai client: {e}")
                self.client = None

    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        if not self.client:
            raise RuntimeError("Gemini Client not initialized. Check GEMINI_API_KEY.")

        for attempt in range(1, settings.GEMINI_MAX_RETRIES + 1):
            try:
                config = {}
                if system_instruction:
                    config["system_instruction"] = system_instruction

                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config if config else None
                )
                return response.text or ""
            except Exception as e:
                logger.warning(f"Gemini API attempt {attempt} failed: {e}")
                if attempt == settings.GEMINI_MAX_RETRIES:
                    raise
                time.sleep(2 ** attempt)

    def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_instruction: Optional[str] = None
    ) -> T:
        if not self.client:
            raise RuntimeError("Gemini Client not configured. GEMINI_API_KEY is missing.")

        for attempt in range(1, settings.GEMINI_MAX_RETRIES + 1):
            try:
                config = {
                    "response_mime_type": "application/json",
                }
                if system_instruction:
                    config["system_instruction"] = system_instruction

                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config
                )
                raw_text = response.text or "{}"
                # Clean any markdown code blocks if returned
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                raw_text = raw_text.strip()

                parsed_json = json.loads(raw_text)
                return response_model.model_validate(parsed_json)
            except Exception as e:
                logger.warning(f"Gemini structured generation attempt {attempt} failed: {e}")
                if attempt == settings.GEMINI_MAX_RETRIES:
                    raise
                time.sleep(2 ** attempt)

