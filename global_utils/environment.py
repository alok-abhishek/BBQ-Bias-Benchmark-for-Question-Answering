import os
from dotenv import load_dotenv

def load_environment(required_keys=None):
    """
    Load environment variables and validate required keys.

    Args:
        required_keys (list): List of required environment variable keys.

    Returns:
        dict: Dictionary of loaded environment variables.
    """
    load_dotenv()  # Load from .env file

    # Load variables
    env_vars = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "OPENAI_ORG_ID": os.getenv("OPENAI_ORG_ID")
    }

    # Add required keys validation
    if required_keys:
        missing_keys = [key for key in required_keys if key not in env_vars or not env_vars[key]]
        if missing_keys:
            raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_keys)}")

    return env_vars
