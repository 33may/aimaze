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

    def to_json(self) -> dict[str, Any]:
        return {"name": self.name,
                "type": self.param_type.name.lower(),
                "required": self.required}
from typing import Optional, List, Dict, Any
from enum import Enum
from dataclasses import dataclass
import json
import logging

class OutputParameterType(Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    OBJECT = "object"
    DYNAMIC = "dynamic"

    #TODO
    #URL = "url"
    #DATE = "date"
    #EMAIL = "email"
    #PHONE = "phone"

@dataclass
class OutputParameter:
    key: str  # Unique key for the parameter
    name: str  # Human-readable name of the parameter
    param_type: OutputParameterType  # Type of the parameter
    is_array: bool = False  # Whether the parameter is an array
    parent: Optional[str] = None  # Parent key for nested parameters
    default_value: Optional[Any] = None  # Default value if the output is None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OutputParameter':
        """Create OutputParameter from dictionary"""
        return cls(
            key=data['key'],
            name=data['name'],
            param_type=OutputParameterType(data['type']),
            is_array=data.get('is_array', False),
            parent=data.get('parent'),
            default_value=data.get('default_value')
        )

    def to_json(self) -> dict[str, Any]:
        return {"name": self.name,
                "type": self.param_type.name.lower(),
                "is_array": self.is_array,
                "default": self.default_value}

class OutputParameterValidationError(Exception):
    """Custom exception for output parameter validation errors"""
    pass

class OutputParameterValidator:
    @staticmethod
    def validate_value(value: Any, parameter: OutputParameter) -> Any:
        """Validate a value against an output parameter's specifications and return processed value"""
        logging.info(f"Validating output value for parameter: {parameter.key}")
        
        # Handle None value by returning default if available
        if value is None:
            return parameter.default_value

        # Check array constraint
        if parameter.is_array:
            if not isinstance(value, list):
                raise OutputParameterValidationError(
                    f"Parameter {parameter.key} expects an array but got {type(value)}"
                )
            # Validate each array element
            validated_array = []
            for i, element in enumerate(value):
                validated_element = OutputParameterValidator._validate_type(
                    element if element is not None else parameter.default_value,
                    parameter.param_type,
                    f"{parameter.key}[{i}]"
                )
                validated_array.append(validated_element)
            return validated_array
        else:
            if isinstance(value, list):
                raise OutputParameterValidationError(
                    f"Parameter {parameter.key} expects a single value but got an array"
                )
            logging.info(f"Output validation successful for parameter: {parameter.key}")
            return OutputParameterValidator._validate_type(value, parameter.param_type, parameter.key)
        

    @staticmethod
    def _validate_type(value: Any, param_type: OutputParameterType, key: str) -> Any:
        """Validate type of a single value and return processed value"""
        try:
            if value is None:
                return value

            if param_type == OutputParameterType.STRING:
                if not isinstance(value, str):
                    raise TypeError("Must be a string")
                    
            elif param_type == OutputParameterType.INTEGER:
                if not isinstance(value, int):
                    raise TypeError("Must be an integer")
                    
            elif param_type == OutputParameterType.FLOAT:
                if not isinstance(value, (int, float)):
                    raise TypeError("Must be a number")
                    
            elif param_type == OutputParameterType.BOOLEAN:
                if not isinstance(value, bool):
                    raise TypeError("Must be a boolean")
                    
            elif param_type == OutputParameterType.OBJECT:
                if not isinstance(value, dict):
                    raise TypeError("Must be an object")
            
            elif param_type == OutputParameterType.DYNAMIC:
                if not isinstance(value, dict):
                    raise TypeError("Must be an object")
            
            elif param_type == OutputParameterType.URL:
                if not isinstance(value, str) or not value.startswith("http"):
                    raise TypeError("Must be a URL")
                
            elif param_type == OutputParameterType.DATE:
                if not isinstance(value, str):
                    raise TypeError("Must be a string")
            
            elif param_type == OutputParameterType.EMAIL:
                if not isinstance(value, str) or "@" not in value:
                    raise TypeError("Must be an email address")
                
            elif param_type == OutputParameterType.PHONE:
                if not isinstance(value, str) or not value.isdigit():
                    raise TypeError("Must be a phone number")
                    
            return value
                    
        except TypeError as e:
            raise OutputParameterValidationError(f"Invalid type for {key}: {str(e)}")

class OutputParameterSchema:
    def __init__(self, parameters: List[OutputParameter]):
        self.parameters = parameters
        self._parameter_map = {param.key: param for param in parameters}
        self._validate_schema()
        
    def _validate_schema(self) -> None:
        """Validate the schema structure, especially parent references"""
        for param in self.parameters:
            if param.parent:
                if param.parent not in self._parameter_map:
                    raise OutputParameterValidationError(
                        f"Parameter {param.key} references non-existent parent {param.parent}"
                    )
                parent = self._parameter_map[param.parent]
                if parent.param_type not in [OutputParameterType.OBJECT, OutputParameterType.DYNAMIC]:
                    raise OutputParameterValidationError(
                        f"Parent parameter {param.parent} must be of type OBJECT or DYNAMIC"
                    )
    
    def validate_output(self, output_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate output data against the schema and return processed data"""
        processed_output = {}

        logging.info("Validating output data")
        
        # First pass: validate all non-nested parameters
        processed = set()
        for param in self.parameters:
            if not param.parent:
                value = output_data.get(param.key)
                validated_value = OutputParameterValidator.validate_value(value, param)
                processed_output[param.key] = validated_value
                processed.add(param.key)
        
        # Second pass: validate nested parameters
        for param in self.parameters:
            if param.parent and param.parent in processed:
                parent_data = output_data.get(param.parent, {})
                
                # Handle array of objects
                if isinstance(parent_data, list):
                    if not all(isinstance(item, dict) for item in parent_data):
                        raise OutputParameterValidationError(
                            f"All items in {param.parent} array must be objects"
                        )
                    
                    if param.parent not in processed_output:
                        processed_output[param.parent] = []
                    
                    # Process each object in the array
                    for item in parent_data:
                        processed_item = {}
                        for nested_param in [p for p in self.parameters if p.parent == param.parent]:
                            value = item.get(nested_param.key)
                            validated_value = OutputParameterValidator.validate_value(value, nested_param)
                            processed_item[nested_param.key] = validated_value
                        processed_output[param.parent].append(processed_item)
                    
                # Handle single object
                else:
                    if not isinstance(parent_data, dict) and not (param.is_array and isinstance(parent_data, list) and all(isinstance(item, dict) for item in parent_data)):
                        raise OutputParameterValidationError(
                            f"Parent parameter {param.parent} must be either an object or an array of objects"
                        )
                    
                    if param.parent not in processed_output:
                        processed_output[param.parent] = {}
                    
                    value = parent_data.get(param.key)
                    validated_value = OutputParameterValidator.validate_value(value, param)
                    processed_output[param.parent][param.key] = validated_value
                
                processed.add(param.key)
                
        logging.info("Output data validation successful")
        logging.debug(f"Processed output: {json.dumps(processed_output, default=str)}")

        return processed_output
