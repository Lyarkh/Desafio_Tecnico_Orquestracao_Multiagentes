import os
import logging

from crewai import LLM
from models import AnalysisResponse, ConsolidatedResponse


GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
MODEL_NAME = os.environ.get("MODEL_NAME")

if not GOOGLE_API_KEY or not MODEL_NAME:
    logging.error("A GOOGLE_API_KEY and MODEL_NAME não estão configurada.")
    raise ValueError("GOOGLE_API_KEY and MODEL_NAME must be set in the environment variables.")

llm_for_review = LLM(
    model=f"gemini/{MODEL_NAME}",
    api_key=GOOGLE_API_KEY,
    temperature=0.3,
    response_format=AnalysisResponse,
)

llm_for_report = LLM(
    model=f"gemini/{MODEL_NAME}",
    api_key=GOOGLE_API_KEY,
    temperature=0.3,
    response_format=ConsolidatedResponse,
)
