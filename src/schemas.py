INPUT_PARAMETER = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string"
        },
        "required": {
            "type": "boolean"
        },
        "type": {
            "type": "string",
            "enum": [
                "integer",
                "boolean",
                "string",
                "float",
                "object"
            ]
        },
        "description": {
            "type": "string",
            "description": "Any additional info needed about this parameter that isn't already captured by the schema. Use only if necessary."
        }
    },
    "required": ["name", "required", "type", "description"],
    "additionalProperties": False
}

OUTPUT_PARAMETER = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string"
        },
        "is_array": {
            "type": "boolean"
        },
        "type": {
            "type": "string",
            "enum": [
                "integer",
                "boolean",
                "string",
                "float",
                "object"
            ]
        },
        "description": {
            "type": "string",
            "description": "Any additional info needed about this parameter that isn't already captured by the schema. Use only if necessary."
        }
    },
    "required": ["name", "is_array", "type", "description"],
    "additionalProperties": False
}

SCHEMA = {
    "type": "object",
    "properties": {
        "endpoints": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the endpoint",
                        # "pattern": "\w( \w)+",
                        "pattern": "[^\"]+",  # Name gets put in a string in code later, this way we don't escape it prematurely.
                    },
                    "url": {
                        "type": "string",
                        "description": "Absolute URL of the endpoint"
                    },
                    "args_in_url": {
                        "type": "boolean",
                        "description": "Whether any payload information should be in the endpoint URL itself (e.g. '/posts/{userID}/{postID}' instead of '/posts' with userID and postID given in the params)."
                    },
                    "method": {
                        "type": "string",
                        "enum": ["GET", "DELETE", "INSERT", "UPDATE", "PUT"],
                    },

                    "input_parameters": {
                        "type": "array",
                        "items": INPUT_PARAMETER,
                        "additionalProperties": False
                    },
                    "output_parameters": {
                        "type": "array",
                        "items": OUTPUT_PARAMETER,
                        "additionalProperties": False
                    },
                    "description": {
                        "type": "string",
                        "description": "Any additional info needed about this endpoint that isn't already captured by the schema. Use only if necessary."
                    }
                },
                "required": ["name", "method", "url", "args_in_url", "input_parameters", "output_parameters", "description"],
                "additionalProperties": False
            },
        },
    },
    "required": ["endpoints"],
    "additionalProperties": False
}

OPENAI_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "endpoints",
        "strict": True,
        "schema": SCHEMA
    },
}
