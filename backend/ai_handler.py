import os
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables from .env file
load_dotenv()

# Initialize Anthropic client
anthropic_key = os.getenv("ANTHROPIC_API_KEY")
if anthropic_key:
    client = Anthropic(api_key=anthropic_key)
else:
    print("Warning: ANTHROPIC_API_KEY not found in .env file")
    client = None

# Default model
DEFAULT_MODEL = "claude-3-5-sonnet-20240620"


def ai_gen(messages, max_tokens=1000, **kwargs):
    try:
        if not client:
            raise ValueError("No Anthropic API key found. Please check your .env file for ANTHROPIC_API_KEY.")

        # Set up the parameters
        params = {
            "model": kwargs.get("model", DEFAULT_MODEL),
            "max_tokens": max_tokens,
            "messages": messages,
            **kwargs
        }

        # Make the API call
        response = client.messages.create(**params)
        return response.content[0].text  # Extract the text from the TextBlock

    except Exception as e:
        print(f"Error calling Anthropic API: {e}")
        return f"Sorry, I encountered an error: {str(e)}"


def test_ai_handler():
    print("Testing AI Handler:")

    test_messages = [
        {"role": "user", "content": "Hello world!"}
    ]
    response = ai_gen(test_messages)
    print(f"Claude response: {response}")


if __name__ == "__main__":
    test_ai_handler()
