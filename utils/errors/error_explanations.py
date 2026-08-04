ERROR_EXPLANATIONS = {
    "KeyError": (
        "The bot attempted to access a dictionary key that does not exist."
    ),

    "IndexError": (
        "The bot attempted to access an item outside the available range of a list or sequence."
    ),

    "AttributeError": (
        "The bot attempted to use an attribute or method that does not exist on an object."
    ),

    "TypeError": (
        "The bot attempted to perform an operation using an incompatible data type."
    ),

    "ValueError": (
        "The bot received a value of the correct type, but the value itself was invalid."
    ),

    "NameError": (
        "The bot attempted to use a variable, function, or name that has not been defined."
    ),

    "FileNotFoundError": (
        "The bot attempted to access a file or path that does not exist."
    ),

    "PermissionError": (
        "The bot attempted to access a file or resource without sufficient permissions."
    ),

    "JSONDecodeError": (
        "The bot attempted to read JSON data that is malformed or invalid."
    ),

    "AttributeError": (
        "The bot attempted to access an attribute or method that does not exist."
    ),

    "TimeoutError": (
        "An operation took too long to complete."
    ),

    "ConnectionError": (
        "The bot encountered a problem connecting to another service or resource."
    ),

    "HTTPException": (
        "Discord returned an error while processing the bot's request."
    ),

    "Forbidden": (
        "Discord refused the requested action because the bot does not have sufficient permissions."
    ),

    "NotFound": (
        "The requested Discord resource could not be found."
    ),
}


DEFAULT_EXPLANATION = (
    "The bot encountered an unexpected internal error. "
    "The stored error details may be required to determine the exact cause."
)


def explain_error(error_type: str) -> str:
    return ERROR_EXPLANATIONS.get(
        error_type,
        DEFAULT_EXPLANATION
    )