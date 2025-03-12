from typing import Any, Optional
from enum import Enum
from typing import Callable

#Allowed parameter types based on software of Teamportal.ai (input types)
class ParameterType(Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    SELECT = "select"
    ARRAY = "array"
    DYNAMIC = "dynamic"
    FILE = "file"

    #TODO
    URL = "url"
    DATE = "date"
    EMAIL = "email"
    PHONE = "phone"

class Parameter:
    def __init__(
        self,
        name: str,
        param_type: ParameterType, # Type of the parameter
        required: bool = False, # Whether the parameter is required
        validation_rules: Optional[dict[Any, Any]] = None, # Validation rules for the parameter
        custom_validator: Optional[Callable[..., Any]] = None # Custom validator function
    ):
        self.name = name
        self.param_type = param_type
        self.required = required
        self.validation_rules = validation_rules or {}
        self.custom_validator = custom_validator