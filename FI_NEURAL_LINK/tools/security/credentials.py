import os

def get_api_key(name: str) -> str:
    """
    Reads an API key from environment variables.
    Raises EnvironmentError if the key is not set.
    """
    key = os.environ.get(name)
    if key is None:
        raise EnvironmentError(f"API key '{name}' is not set. Please set the environment variable '{name}'.")
    return key
