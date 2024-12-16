import logging
import os

from vertexai.generative_models import (
    GenerationConfig,
    GenerationResponse,
    GenerativeModel,
)

from tools.spend import spend_tool

logger = logging.getLogger(__name__)


def extract_function_call(response: GenerationResponse) -> dict:
    """
    Extracts a single function call from the model's response.

    Args:
        response (GenerationResponse): The model's response.

    Returns:
        dict: A dictionary representing the function call and its arguments.
    """
    if response.candidates and response.candidates[0].function_calls:
        function_call = response.candidates[0].function_calls[0]
        function_call_dict = {function_call.name: dict(function_call.args)}
        return function_call_dict

    logger.info("No function call found in the model response.")
    return {}


def extract_text(response: GenerationResponse) -> str:
    """_summary_

    Args:
        response (GenerationResponse): _description_

    Returns:
        str: _description_
    """
    # Extract text from the model's response
    text = response.candidates[0].content.parts[0].text
    logger.info(f"Extracted text: {text}")

    return text


def get_model() -> GenerativeModel:
    """
    Returns a configured GenerativeModel object.

    Raises:
        ValueError: If the MODEL_LLM environment variable is not set.

    Returns:
        GenerativeModel: A configured generative model instance.
    """
    MODEL_LLM = os.getenv("MODEL_LLM")
    if not MODEL_LLM:
        raise ValueError("MODEL_LLM environment variable is not set.")

    logger.info(f"Initializing GenerativeModel with MODEL_LLM: {MODEL_LLM}")

    return GenerativeModel(
        MODEL_LLM,
        generation_config=GenerationConfig(temperature=0, candidate_count=1),
        tools=[spend_tool],
    )
