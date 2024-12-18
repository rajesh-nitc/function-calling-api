import logging

from vertexai.generative_models import GenerativeModel, Part

from services.function_registry import FUNCTION_REGISTRY
from utils.gcs_history import append_chat_to_gcs, load_same_day_history
from utils.vertex_ai_llm import extract_function_call, extract_text

logger = logging.getLogger(__name__)


def generate_model_response(prompt: str, model: GenerativeModel, user_id: str) -> str:
    """
    Generates a response from the model based on the given prompt, maintains conversation history by user_id,
    and returns the final model response. Chat history is stored in a GCP bucket by day.

    Args:
        prompt (str): The input prompt.
        model (GenerativeModel): The generative model to use.
        user_id (str): The unique identifier for the user.

    Returns:
        str: The final model response.
    """
    logger.info(f"***** Received new prompt from user {user_id}: {prompt} *****")

    # Retrieve or initialize the user's chat history for the same day
    history = load_same_day_history(user_id)

    # Start a new chat session with the model
    chat = model.start_chat()

    # Construct the full conversation context from the history
    conversation = "\n".join(history)
    if conversation:
        conversation += "\n"  # Add a newline if there's existing history

    # Add the current user prompt to the conversation
    conversation += f"user: {prompt}\nmodel:"

    logger.info(f"===== Conversation: {conversation} =====")

    # Send the conversation history and new prompt to the model
    response = chat.send_message(conversation)

    # Extract the function call or text from the model's response
    function_call = extract_function_call(response)

    if function_call:
        function_name, function_args = next(iter(function_call.items()))
        logger.info(f"function_name: {function_name}, function_args: {function_args}")

        # Fetch response using the appropriate function handler
        if function_name in FUNCTION_REGISTRY:
            api_response = FUNCTION_REGISTRY[function_name](function_args)
        else:
            raise ValueError(f"Unknown function called: {function_name}")

        # Send api response back to the model
        response = chat.send_message(
            Part.from_function_response(
                name=function_name,
                response={"content": api_response},
            )
        )

        # Extract the final text response from the model
        model_response = extract_text(response)

    else:
        # If there is no function call, extract the text from the initial response
        model_response = extract_text(response)

    # Store the updated history in GCP bucket
    append_chat_to_gcs(user_id, f"user: {prompt}")
    append_chat_to_gcs(user_id, f"model: {model_response}")

    return model_response