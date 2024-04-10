"""
OpenAI Functions Helper definitions and methods
"""
from typing import Dict


def get_account_balance(params: Dict[str, str]) -> str:
    """
    Gets the account balance based on the params received
    :param params: OpenAI Function parameters returned by the engine
    :return: The current specific account balance
    @TODO: This needs to be changed by a non hardcoded result.
    """
    if "client_id" in params:
        if "date" in params:
            return f"Estado de cuenta del cliente {params['client_id']} al {params['date']} es $1236.55"
        return "'date' is a required parameter."
    return "'client_id' is a required parameter."


OPENAI_FUNCTIONS = {
    "get_account_balance": {
        "function_call": get_account_balance,
        "data": {
            "name": "get_account_balance",
            "description": "Get the client account balance at a given date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "client_id": {
                        "type": "string",
                        "description": "The client's id.",
                    },
                    "date": {
                        "type": "string",
                        "description": "The balance's date in format YYYY-MM-DD.",
                    },
                },
                "required": ["client_id", "date"],
            },
        },
    },
}
