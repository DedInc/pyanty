from .constants import JSONValue


def parse_json_response(response: object) -> JSONValue:
    try:
        return response.json()
    except ValueError as error:
        raise RuntimeError(response.text) from error
