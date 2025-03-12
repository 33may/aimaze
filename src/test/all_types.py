# FunctionClass.py
from typing import List
from abc import ABC, abstractmethod
import json
import azure.functions as func
from shared.InputClass import StandardInput
from shared.OutputClass import StandardOutput
from shared.ParameterClass import Parameter
from shared.OutputParameterClass import OutputParameter

class BaseFunction(ABC):
    @abstractmethod
    def process(self, input_data: StandardInput) -> StandardOutput:
        """Process the input data and return standard output"""
        pass

    @abstractmethod
    def get_parameter_schema(self) -> List[Parameter]:
        """Return the parameter schema for this function"""
        pass

    @abstractmethod
    def get_output_schema(self) -> List[OutputParameter]:
        """Return the output parameter schema for this function"""
        pass

    def run(self, req: func.HttpRequest) -> func.HttpResponse:
        try:
            # Parse request body
            req_body = req.get_json()

            # Create StandardInput instance with schema
            input_data = StandardInput(req_body, self.get_parameter_schema())

            # Process data
            output = self.process(input_data)

            # Return response
            return func.HttpResponse(
                json.dumps(output.to_dict()),
                mimetype="application/json",
                status_code=200
            )
        except ValueError as e:
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=400
            )
        except Exception as e:
            return func.HttpResponse(
                json.dumps({"error": "Internal server error: " + str(e)}),
                mimetype="application/json",
                status_code=500
            )


# InputClass.py
 import ast
import re
from typing import Any
from shared.ParameterClass import Parameter, ParameterType
from shared.ValidationClass import ValidationResult, ValidationSeverity, CustomValidationType
from urllib.parse import urlparse, ParseResult
from shared.subfunctions.utilities import parse_to_array
from datetime import datetime
import json
import logging

def remove_non_ascii(text: str) -> str:
    """
    Remove all non-ASCII characters from the input text string.

    Args:
        text (str): Input text containing any Unicode characters

    Returns:
        str: Text with only ASCII characters (0-127) remaining
    """
    # Only keep characters with ASCII values 0-127
    return ''.join(char for char in text if ord(char) < 128)

class StandardInput:
    def __init__(self, raw_data: dict[str, Any], parameter_schema: list[Parameter]):
        self.raw_data = raw_data
        self.parameter_schema = parameter_schema
        self.validated_data: dict[str, Any] = {}
        self.validation_result = ValidationResult()

        # Log input data
        logging.info(f"Received input data: {json.dumps(raw_data, default=str)}")
        logging.info(f"Parameter schema: {[(param.name, param.param_type.value) for param in parameter_schema]}")

        self._validate()

    def _validate(self) -> None:
        """Main validation method"""
        logging.info("Starting input validation")

        for param in self.parameter_schema:
            value = self.raw_data.get(param.name)
            logging.debug(f"Validating parameter '{param.name}' with value: {value}")

            # Check for empty or missing values
            if value is None or (isinstance(value, str) and value.strip() == ""):
                if param.required:
                    error_msg = f"Required parameter '{param.name}' is missing"
                    logging.error(error_msg)
                    self.validation_result.add_error(error_msg, param.name)
                else:
                    # For non-required parameters, set to None and skip validation
                    self.validated_data[param.name] = None
                    logging.debug(f"Skipping validation for empty non-required parameter '{param.name}'")
                continue

            try:
                # Only proceed with validation for non-empty values
                if value is not None and (not isinstance(value, str) or value.strip() != ""):
                    value = self._validate_type(value, param)
                    self._validate_rules(value, param)
                    logging.debug(f"Parameter '{param.name}' passed validation")
                    self.validated_data[param.name] = value
                else:
                    # Handle empty strings for non-required parameters
                    if not param.required:
                        self.validated_data[param.name] = None
                        logging.debug(f"Setting empty non-required parameter '{param.name}' to None")
                    else:
                        self.validated_data[param.name] = value
            except Exception as e:
                logging.error(f"Validation failed for parameter '{param.name}': {str(e)}")
                raise

        # Log validation results
        if self.validation_result.has_errors:
            logging.error(f"Validation errors: {json.dumps(self.validation_result.get_messages())}")
            raise ValueError(json.dumps(self.validation_result.get_messages()))
        else:
            logging.info("Input validation completed successfully")
            if self.validation_result.has_warnings:
                logging.warning(f"Validation warnings: {json.dumps(self.validation_result.get_messages())}")

    def _convert_value(self, value: Any, param_type: ParameterType) -> Any:
        """Attempt to convert value to the required type"""
        try:
            if param_type == ParameterType.STRING:
                return str(value)

            elif param_type == ParameterType.INTEGER:
                if isinstance(value, str):
                    # Remove any commas or spaces from number strings
                    value = value.replace(',', '').strip()
                return int(float(value))  # Handle both "123" and "123.0"

            elif param_type == ParameterType.FLOAT:
                if isinstance(value, str):
                    # Remove any commas or spaces from number strings
                    value = value.replace(',', '').strip()
                return float(value)

            elif param_type == ParameterType.BOOLEAN:
                if isinstance(value, str):
                    value = value.lower().strip()
                    if value in ('true', '1', 'yes', 'on'):
                        return True
                    elif value in ('false', '0', 'no', 'off'):
                        return False
                    raise ValueError("Invalid boolean value")
                return bool(value)

            elif param_type == ParameterType.SELECT:
                return str(value)

            elif param_type == ParameterType.ARRAY:
                return parse_to_array(value)

            elif param_type == ParameterType.DYNAMIC:
                value = ast.literal_eval(value)
                if isinstance(value, dict):
                    return value
                elif isinstance(value, str):
                    try:
                        # First attempt: try standard JSON parsing
                        try:
                            parsed = json.loads(value)
                            if not isinstance(parsed, dict):
                                raise ValueError("DYNAMIC type must be a JSON object/dictionary")
                            return parsed
                        except json.JSONDecodeError:
                            # Second attempt: try to fix single quotes
                            value = value.replace("'", '"')
                            try:
                                parsed = json.loads(value)
                                if not isinstance(parsed, dict):
                                    raise ValueError("DYNAMIC type must be a JSON object/dictionary")
                                return parsed
                            except json.JSONDecodeError:
                                # Third attempt: try to handle unquoted property names
                                import re
                                # Find unquoted property names and quote them
                                value = re.sub(r'([{,])\s*([a-zA-Z0-9_]+)\s*:', r'"":', value)
                                parsed = json.loads(value)
                                if not isinstance(parsed, dict):
                                    raise ValueError("DYNAMIC type must be a JSON object/dictionary")
                                return parsed
                    except Exception as e:
                        raise ValueError(f"Invalid JSON object: {str(e)}")
                raise ValueError("Value must be a dictionary or valid JSON string")

            elif param_type == ParameterType.FILE:
                return str(value)

            elif param_type == ParameterType.URL:
                return str(value)

            elif param_type == ParameterType.DATE:
                if isinstance(value, (int, float)):
                    return datetime.fromtimestamp(value).isoformat()
                return str(value)

            elif param_type == ParameterType.EMAIL:
                return str(value)

            elif param_type == ParameterType.PHONE:
                if isinstance(value, (int, float)):
                    return str(int(value))
                return str(value)

            return value

        except Exception as e:
            logging.error(f"Type conversion failed: {str(e)}")
            raise ValueError(f"Cannot convert to {param_type.value}: {str(e)}")

    def _validate_type(self, value: Any, param: Parameter) -> Any:
        """Comprehensive type validation with conversion attempts"""
        try:
            # First try to convert the value if it's not already the correct type
            if param.param_type == ParameterType.STRING and not isinstance(value, str):
                value = self._convert_value(value, param.param_type)

            elif param.param_type == ParameterType.INTEGER and not isinstance(value, int):
                value = self._convert_value(value, param.param_type)

            elif param.param_type == ParameterType.FLOAT and not isinstance(value, (int, float)):
                value = self._convert_value(value, param.param_type)

            elif param.param_type == ParameterType.BOOLEAN and not isinstance(value, bool):
                value = self._convert_value(value, param.param_type)

            elif param.param_type == ParameterType.SELECT and not isinstance(value, str):
                value = self._convert_value(value, param.param_type)
                if value not in param.validation_rules.get("allowed_values", []):
                    raise ValueError(f"Value must be one of: {param.validation_rules['allowed_values']}")

            elif param.param_type == ParameterType.ARRAY and not isinstance(value, list):
                value = self._convert_value(value, param.param_type)

            elif param.param_type == ParameterType.DYNAMIC and not isinstance(value, dict):
                value = self._convert_value(value, param.param_type)

            elif param.param_type == ParameterType.FILE and not isinstance(value, str):
                value = self._convert_value(value, param.param_type)

            elif param.param_type == ParameterType.URL:
                value = self._convert_value(value, param.param_type)
                result: ParseResult = urlparse(value)
                if not all([result.scheme, result.netloc]):
                    raise ValueError("Invalid URL format")

            elif param.param_type == ParameterType.DATE:
                value = self._convert_value(value, param.param_type)
                # Attempt to parse the date string
                datetime.fromisoformat(value.replace('Z', '+00:00'))

            elif param.param_type == ParameterType.EMAIL:
                value = self._convert_value(value, param.param_type)
                if '@' not in value:
                    raise ValueError("Invalid email format")

            elif param.param_type == ParameterType.PHONE:
                value = self._convert_value(value, param.param_type)
                if not value.replace('+', '').isdigit():
                    raise ValueError("Invalid phone number format")
                if len(value) < 10:
                    raise ValueError("Phone number must have at least 10 digits")

            return value

        except (TypeError, ValueError) as e:
            self.validation_result.add_error(str(e), param.name)
            raise

    def _validate_rules(self, value: Any, param: Parameter) -> None:
        """Custom rules validation"""
        try:
            # Execute custom validator if provided
            if param.custom_validator:
                try:
                    result = param.custom_validator(value)
                    if result is not True:  # Custom validator should return True if valid
                        raise ValueError(result if isinstance(result, str) else "Custom validation failed")
                except Exception as e:
                    raise ValueError(str(e))

            # Check validation rules
            for rule_type, rule_value in param.validation_rules.items():
                if rule_type == CustomValidationType.ALLOWED_VALUES.value:
                    if value not in rule_value:
                        raise ValueError(f"Value must be one of: {rule_value}")

                elif rule_type == CustomValidationType.MIN_LENGTH.value:
                    if len(value) < rule_value:
                        raise ValueError(f"Minimum length: {rule_value}")

                elif rule_type == CustomValidationType.MAX_LENGTH.value:
                    if len(value) > rule_value:
                        raise ValueError(f"Maximum length: {rule_value}")

                elif rule_type == CustomValidationType.MIN_VALUE.value:
                    if value < rule_value:
                        raise ValueError(f"Minimum value: {rule_value}")

                elif rule_type == CustomValidationType.MAX_VALUE.value:
                    if value > rule_value:
                        raise ValueError(f"Maximum value: {rule_value}")

        except ValueError as e:
            if param.validation_rules.get("severity") == ValidationSeverity.WARNING:
                self.validation_result.add_warning(str(e), param.name)
            else:
                self.validation_result.add_error(str(e), param.name)


# OutputClass.py
 from typing import Any, Dict, List
import json
import logging
from .OutputParameterClass import OutputParameter, OutputParameterSchema, OutputParameterValidationError

class StandardOutput:
    def __init__(self, output_data: Dict[str, Any], output_schema: List[OutputParameter]):
        self.output_data = output_data
        self.schema = OutputParameterSchema(output_schema)
        logging.info("Creating output with schema validation")
        logging.debug(f"Raw output data: {json.dumps(output_data, default=str)}")

        # Filter the output data according to schema before validation
        self.output_data = self._filter_output_data(output_data)
        logging.debug(f"Filtered output data: {json.dumps(self.output_data, default=str)}")

        self._validate()

    def _filter_output_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter output data to only include fields defined in the schema"""
        filtered_data = {}

        # Get all non-nested parameters
        root_params = {param.key: param for param in self.schema.parameters if not param.parent}

        # Get nested parameters organized by parent
        nested_params = {}
        for param in self.schema.parameters:
            if param.parent:
                if param.parent not in nested_params:
                    nested_params[param.parent] = {}
                nested_params[param.parent][param.key] = param

        for param in self.schema.parameters:
            if param.parent:
                if param.parent not in nested_params:
                    nested_params[param.parent] = {}
                nested_params[param.parent][param.key] = param

        # Process root level parameters
        for key, param in root_params.items():
            if key in data:
                if isinstance(data[key], dict) and key in nested_params:
                    # Handle nested object
                    nested_data = {}
                    for nested_key, nested_param in nested_params[key].items():
                        if nested_key in data[key]:
                            nested_data[nested_key] = data[key][nested_key]
                    filtered_data[key] = nested_data if nested_data else None
                else:
                    # Handle non-nested field
                    filtered_data[key] = data[key]
            else:
                filtered_data[key] = None

        return filtered_data

    def _validate(self) -> None:
        """Validates output format against schema"""
        logging.info("Validating output format")

        try:
            # Validate against schema
            self.schema.validate_output(self.output_data)

            # Ensure entire output is JSON serializable
            json.dumps(self.output_data)
            logging.debug("Output is JSON serializable")

        except OutputParameterValidationError as e:
            logging.error(f"Output validation failed: {str(e)}")
            raise ValueError(str(e))
        except (TypeError, ValueError) as e:
            error_msg = "Output must be JSON serializable"
            logging.error(f"Output validation failed: {error_msg}")
            logging.error(f"Serialization error: {str(e)}")
            raise ValueError(error_msg)

        logging.info("Output validation completed successfully")

    def to_dict(self) -> Dict[str, Any]:
        """Returns the validated output data"""
        return self.output_data


# OutputParameterClass.py
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


# ParameterClass.py
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


# ValidationClass.py
 from typing import Dict, List
from enum import Enum

class CustomValidationType(Enum):
    ALLOWED_VALUES = "allowed_values"
    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"
    MIN_VALUE = "min_value"
    MAX_VALUE = "max_value"

class ValidationSeverity(Enum):
    WARNING = "warning"
    ERROR = "error"

class StarndardizedWarningMessages(Enum):
    STRING = "NO_INFORMATION"
    INTEGER = -1
    FLOAT = -1.0
    BOOLEAN = False
    ARRAY = []
    OBJECT = {}

class ValidationError:
    def __init__(self, message: str, parameter: str, severity: ValidationSeverity = ValidationSeverity.ERROR):
        self.message = message
        self.parameter = parameter
        self.severity = severity

    def __str__(self):
        return f"{self.severity.value.upper()}: {self.parameter} - {self.message}"

class ValidationResult:
    def __init__(self):
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []

    def add_error(self, message: str, parameter: str):
        self.errors.append(ValidationError(message, parameter, ValidationSeverity.ERROR))

    def add_warning(self, message: str, parameter: str):
        self.warnings.append(ValidationError(message, parameter, ValidationSeverity.WARNING))

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0

    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0

    def get_messages(self) -> Dict[str, List[str]]:
        return {
            "errors": [str(error) for error in self.errors],
            "warnings": [str(warning) for warning in self.warnings]
        }


# WooCommerceClass.py
 from typing import Dict, Any, Optional, List
import requests
from urllib.parse import urlencode, quote, urljoin
import time
import random
import string
import hmac
import hashlib
import base64
import logging
from dataclasses import dataclass
from enum import Enum

class WooCommerceAuthType(str, Enum):
    """Authentication types supported by WooCommerce"""
    BASIC = "basic"
    OAUTH = "oauth"

@dataclass
class WooCommerceConfig:
    """Configuration class for WooCommerce settings"""
    store_url: str
    consumer_key: str
    consumer_secret: str
    api_version: str = "wc/v3"
    is_https: bool = False
    auth_type: WooCommerceAuthType = WooCommerceAuthType.BASIC
    verify_ssl: bool = True
    timeout: int = 30
    query_string_auth: bool = False

class WooCommerceError(Exception):
    """Custom exception for WooCommerce-related errors"""
    pass

class WooCommerceClass:
    """Helper class to handle WooCommerce API operations"""

    def __init__(self, config: WooCommerceConfig):
        self.config = config
        self._validate_config()
        self.base_url = self._get_base_url()
        logging.info(f"WooCommerce client initialized for store: {self.config.store_url}")

    def _validate_config(self) -> None:
        if not all([self.config.store_url, self.config.consumer_key, self.config.consumer_secret]):
            raise WooCommerceError("Missing required configuration parameters")

        if self.config.store_url.startswith('https://'):
            self.config.is_https = True

        if not self.config.is_https:
            self.config.auth_type = WooCommerceAuthType.OAUTH
            self.config.query_string_auth = True

    def _get_base_url(self) -> str:
        return urljoin(
            self.config.store_url.rstrip('/') + '/',
            f"wp-json/{self.config.api_version}/"
        )

    def _get_oauth_params(self, method: str, url: str) -> Dict[str, str]:
        params = {
            'oauth_consumer_key': self.config.consumer_key,
            'oauth_nonce': ''.join(random.choices(string.ascii_letters + string.digits, k=32)),
            'oauth_signature_method': 'HMAC-SHA256',
            'oauth_timestamp': str(int(time.time()))
        }

        base_string = '&'.join([
            method,
            quote(url, safe=''),
            quote(urlencode(sorted(params.items())), safe='')
        ])

        key = f"{self.config.consumer_secret}&"
        signature = base64.b64encode(
            hmac.new(
                key.encode(),
                base_string.encode(),
                hashlib.sha256
            ).digest()
        ).decode()

        params['oauth_signature'] = signature
        return params

    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        url = urljoin(self.base_url, endpoint.lstrip('/'))
        headers = {'Content-Type': 'application/json'}
        request_params = params or {}

        try:
            if self.config.auth_type == WooCommerceAuthType.BASIC:
                auth = (self.config.consumer_key, self.config.consumer_secret)
                if self.config.query_string_auth:
                    request_params.update({
                        'consumer_key': self.config.consumer_key,
                        'consumer_secret': self.config.consumer_secret
                    })
                    auth = None
            else:
                auth = None
                request_params.update(self._get_oauth_params(method, url))

            response = requests.request(
                method=method,
                url=url,
                params=request_params,
                json=data,
                headers=headers,
                auth=auth,
                verify=self.config.verify_ssl,
                timeout=self.config.timeout
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logging.error(f"WooCommerce API request failed: {str(e)}")
            if response := getattr(e, 'response', None):
                try:
                    error_data = response.json()
                    error_message = error_data.get('message', str(e))
                except ValueError:
                    error_message = str(e)
            else:
                error_message = str(e)
            raise WooCommerceError(f"API request failed: {error_message}")

    # Product Methods
    def get_products(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get products with optional filtering"""
        return self.request('GET', 'products', params=params)

    def get_product(self, product_id: int) -> Dict[str, Any]:
        """Get a single product by ID"""
        return self.request('GET', f'products/{product_id}')

    def create_product(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new product"""
        return self.request('POST', 'products', data=data)

    def update_product(self, product_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a product"""
        return self.request('PUT', f'products/{product_id}', data=data)

    def delete_product(self, product_id: int, force: bool = False) -> Dict[str, Any]:
        """Delete a product"""
        return self.request('DELETE', f'products/{product_id}', params={'force': force})

    def get_product_categories(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get all product categories"""
        return self.request('GET', 'products/categories', params=params)

    # Order Methods
    def get_orders(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get orders with optional filtering"""
        return self.request('GET', 'orders', params=params)

    def get_order(self, order_id: int) -> Dict[str, Any]:
        """Get a single order by ID"""
        return self.request('GET', f'orders/{order_id}')

    def create_order(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new order"""
        return self.request('POST', 'orders', data=data)

    def update_order(self, order_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an order"""
        return self.request('PUT', f'orders/{order_id}', data=data)

    def delete_order(self, order_id: int, force: bool = False) -> Dict[str, Any]:
        """Delete an order"""
        return self.request('DELETE', f'orders/{order_id}', params={'force': force})

    # Customer Methods
    def get_customers(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get customers with optional filtering"""
        return self.request('GET', 'customers', params=params)

    def get_customer(self, customer_id: int) -> Dict[str, Any]:
        """Get a single customer by ID"""
        return self.request('GET', f'customers/{customer_id}')

    def create_customer(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new customer"""
        return self.request('POST', 'customers', data=data)

    def update_customer(self, customer_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a customer"""
        return self.request('PUT', f'customers/{customer_id}', data=data)

    def delete_customer(self, customer_id: int, force: bool = False) -> Dict[str, Any]:
        """Delete a customer"""
        return self.request('DELETE', f'customers/{customer_id}', params={'force': force})

    def get_customer_downloads(self, customer_id: int) -> List[Dict[str, Any]]:
        """Get customer downloads"""
        return self.request('GET', f'customers/{customer_id}/downloads')

    # Product Review Methods
    def get_product_reviews(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get product reviews with optional filtering"""
        return self.request('GET', 'products/reviews', params=params)

    def get_product_review(self, review_id: int) -> Dict[str, Any]:
        """Get a single product review by ID"""
        return self.request('GET', f'products/reviews/{review_id}')

    def create_product_review(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new product review"""
        return self.request('POST', 'products/reviews', data=data)

    def update_product_review(self, review_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a product review"""
        return self.request('PUT', f'products/reviews/{review_id}', data=data)

    def delete_product_review(self, review_id: int, force: bool = False) -> Dict[str, Any]:
        """Delete a product review"""
        return self.request('DELETE', f'products/reviews/{review_id}', params={'force': force})

    # Refund Methods
    def get_refunds(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get all refunds with optional filtering"""
        return self.request('GET', 'refunds', params=params)

    def get_order_refunds(self, order_id: int, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get refunds for a specific order"""
        return self.request('GET', f'orders/{order_id}/refunds', params=params)

    def get_order_refund(self, order_id: int, refund_id: int) -> Dict[str, Any]:
        """Get a specific refund from an order"""
        return self.request('GET', f'orders/{order_id}/refunds/{refund_id}')

    def create_order_refund(self, order_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a refund for an order"""
        return self.request('POST', f'orders/{order_id}/refunds', data=data)

    def delete_order_refund(self, order_id: int, refund_id: int, force: bool = False) -> Dict[str, Any]:
        """Delete a refund from an order"""
        return self.request('DELETE', f'orders/{order_id}/refunds/{refund_id}', params={'force': force})

    # Report Methods
    def get_reports(self) -> List[Dict[str, Any]]:
        """Get all available reports"""
        return self.request('GET', 'reports')

    def get_sales_report(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get sales report"""
        return self.request('GET', 'reports/sales', params=params)

    def get_top_sellers_report(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get top sellers report"""
        return self.request('GET', 'reports/top_sellers', params=params)

    def get_orders_totals(self) -> List[Dict[str, Any]]:
        """Get orders totals"""
        return self.request('GET', 'reports/orders/totals')

    def get_customers_totals(self) -> List[Dict[str, Any]]:
        """Get customers totals"""
        return self.request('GET', 'reports/customers/totals')

    # Shipping Class Methods
    def get_shipping_classes(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get all shipping classes"""
        return self.request('GET', 'products/shipping_classes', params=params)

    def get_shipping_class(self, shipping_class_id: int) -> Dict[str, Any]:
        """Get a single shipping class"""
        return self.request('GET', f'products/shipping_classes/{shipping_class_id}')

    def create_shipping_class(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new shipping class"""
        return self.request('POST', 'products/shipping_classes', data=data)

    def update_shipping_class(self, shipping_class_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a shipping class"""
        return self.request('PUT', f'products/shipping_classes/{shipping_class_id}', data=data)

    def delete_shipping_class(self, shipping_class_id: int, force: bool = False) -> Dict[str, Any]:
        """Delete a shipping class"""
        return self.request('DELETE', f'products/shipping_classes/{shipping_class_id}', params={'force': force})

    # Product Tag Methods
    def get_product_tags(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get all product tags"""
        return self.request('GET', 'products/tags', params=params)

    def get_product_tag(self, tag_id: int) -> Dict[str, Any]:
        """Get a single product tag"""
        return self.request('GET', f'products/tags/{tag_id}')

    def create_product_tag(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new product tag"""
        return self.request('POST', 'products/tags', data=data)

    def update_product_tag(self, tag_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a product tag"""
        return self.request('PUT', f'products/tags/{tag_id}', data=data)

    def delete_product_tag(self, tag_id: int, force: bool = False) -> Dict[str, Any]:
        """Delete a product tag"""
        return self.request('DELETE', f'products/tags/{tag_id}', params={'force': force})

    # Coupon Methods
    def get_coupons(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get all coupons"""
        return self.request('GET', 'coupons', params=params)

    def get_coupon(self, coupon_id: int) -> Dict[str, Any]:
        """Get a single coupon"""
        return self.request('GET', f'coupons/{coupon_id}')

    def create_coupon(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new coupon"""
        return self.request('POST', 'coupons', data=data)

    def update_coupon(self, coupon_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a coupon"""
        return self.request('PUT', f'coupons/{coupon_id}', data=data)

    def delete_coupon(self, coupon_id: int, force: bool = True) -> Dict[str, Any]:
        """Delete a coupon"""
        return self.request('DELETE', f'coupons/{coupon_id}', params={'force': force})

    # Batch Methods
    def batch_update_products(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Batch create/update/delete products"""
        return self.request('POST', 'products/batch', data=data)

    def batch_update_orders(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Batch create/update/delete orders"""
        return self.request('POST', 'orders/batch', data=data)

    def batch_update_customers(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Batch create/update/delete customers"""
        return self.request('POST', 'customers/batch', data=data)

    def batch_update_reviews(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Batch create/update/delete product reviews"""
        return self.request('POST', 'products/reviews/batch', data=data)

    def batch_update_refunds(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Batch create/update/delete refunds"""
        return self.request('POST', 'refunds/batch', data=data)

    def batch_update_shipping_classes(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Batch create/update/delete shipping classes"""
        return self.request('POST', 'products/shipping_classes/batch', data=data)

    def batch_update_product_tags(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Batch create/update/delete product tags"""
        return self.request('POST', 'products/tags/batch', data=data)

    def batch_update_coupons(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Batch create/update/delete coupons"""
        return self.request('POST', 'coupons/batch', data=data)


# create_coupon.py
 from typing import List
import logging
from datetime import datetime
from shared.FunctionClass import BaseFunction
from shared.ParameterClass import Parameter, ParameterType
from shared.OutputParameterClass import OutputParameter, OutputParameterType
from shared.InputClass import StandardInput
from shared.OutputClass import StandardOutput
from shared.ValidationClass import ValidationSeverity, CustomValidationType
from functions_classes.WooCommerceClass import WooCommerceClass, WooCommerceConfig, WooCommerceAuthType

class CreateWooCommerceCoupon(BaseFunction):
    def get_parameter_schema(self) -> List[Parameter]:
        return [
            Parameter(
                name="store_url",
                param_type=ParameterType.URL,
                required=True,
                validation_rules={
                    CustomValidationType.MIN_LENGTH.value: 1,
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="consumer_key",
                param_type=ParameterType.STRING,
                required=True,
                validation_rules={
                    CustomValidationType.MIN_LENGTH.value: 1,
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="consumer_secret",
                param_type=ParameterType.STRING,
                required=True,
                validation_rules={
                    CustomValidationType.MIN_LENGTH.value: 1,
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="code",
                param_type=ParameterType.STRING,
                required=True,
                validation_rules={
                    CustomValidationType.MIN_LENGTH.value: 1,
                    CustomValidationType.MAX_LENGTH.value: 50,
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="amount",
                param_type=ParameterType.STRING,
                required=True,
                validation_rules={
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="discount_type",
                param_type=ParameterType.SELECT,
                required=True,
                validation_rules={
                    CustomValidationType.ALLOWED_VALUES.value: [
                        "percent", "fixed_cart", "fixed_product"
                    ],
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="description",
                param_type=ParameterType.STRING,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="date_expires",
                param_type=ParameterType.STRING,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="individual_use",
                param_type=ParameterType.BOOLEAN,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="product_ids",
                param_type=ParameterType.ARRAY,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="excluded_product_ids",
                param_type=ParameterType.ARRAY,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="usage_limit",
                param_type=ParameterType.INTEGER,
                required=False,
                validation_rules={
                    CustomValidationType.MIN_VALUE.value: 0,
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="usage_limit_per_user",
                param_type=ParameterType.INTEGER,
                required=False,
                validation_rules={
                    CustomValidationType.MIN_VALUE.value: 0,
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="limit_usage_to_x_items",
                param_type=ParameterType.INTEGER,
                required=False,
                validation_rules={
                    CustomValidationType.MIN_VALUE.value: 0,
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="free_shipping",
                param_type=ParameterType.BOOLEAN,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="product_categories",
                param_type=ParameterType.ARRAY,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="excluded_product_categories",
                param_type=ParameterType.ARRAY,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="exclude_sale_items",
                param_type=ParameterType.BOOLEAN,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="minimum_amount",
                param_type=ParameterType.STRING,
                required=False,
                validation_rules={
                    CustomValidationType.MIN_VALUE.value: 0,
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="maximum_amount",
                param_type=ParameterType.STRING,
                required=False,
                validation_rules={
                    CustomValidationType.MIN_VALUE.value: 0,
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="email_restrictions",
                param_type=ParameterType.ARRAY,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.WARNING
                }
            )
        ]

    def get_output_schema(self) -> List[OutputParameter]:
        return [
            OutputParameter(
                key="id",
                name="Coupon ID",
                param_type=OutputParameterType.INTEGER,
                is_array=False,
                parent=None,
                default_value=None
            )
        ]

    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            # Get required parameters
            store_url = input_data.validated_data["store_url"]
            consumer_key = input_data.validated_data["consumer_key"]
            consumer_secret = input_data.validated_data["consumer_secret"]
            code = input_data.validated_data["code"]
            amount = input_data.validated_data["amount"]
            discount_type = input_data.validated_data["discount_type"]

            # Get optional parameters
            optional_parameters = {}
            for param in self.get_parameter_schema():
                if param.name in input_data.validated_data:
                    optional_parameters[param.name] = input_data.validated_data[param.name]


            # Initialize WooCommerce client
            logging.info(f"Initializing WooCommerce client for store: {store_url}")
            wc_config = WooCommerceConfig(
                store_url=store_url,
                consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                auth_type=WooCommerceAuthType.BASIC
            )
            wc = WooCommerceClass(wc_config)

            coupon_data = {
                "code": code,
                "amount": amount,
                "discount_type": discount_type
            }

            for key, value in optional_parameters.items():
                coupon_data[key] = value

            output = wc.create_coupon(coupon_data)

            output_data = {
                "id": output["id"]
            }

            return StandardOutput(output_data, self.get_output_schema())

        except Exception as e:
            error_msg = f"Error creating coupon: {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)


# delete_coupon.py
 from typing import List
import logging
from datetime import datetime
from shared.FunctionClass import BaseFunction
from shared.ParameterClass import Parameter, ParameterType
from shared.OutputParameterClass import OutputParameter, OutputParameterType
from shared.InputClass import StandardInput
from shared.OutputClass import StandardOutput
from shared.ValidationClass import ValidationSeverity, CustomValidationType
from functions_classes.WooCommerceClass import WooCommerceClass, WooCommerceConfig, WooCommerceAuthType

class DeleteWooCommerceCoupon(BaseFunction):
    def get_parameter_schema(self) -> List[Parameter]:
        return [
            Parameter(
                name="store_url",
                param_type=ParameterType.URL,
                required=True,
                validation_rules={
                    CustomValidationType.MIN_LENGTH.value: 1,
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="consumer_key",
                param_type=ParameterType.STRING,
                required=True,
                validation_rules={
                    CustomValidationType.MIN_LENGTH.value: 1,
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="consumer_secret",
                param_type=ParameterType.STRING,
                required=True,
                validation_rules={
                    CustomValidationType.MIN_LENGTH.value: 1,
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="id",
                param_type=ParameterType.INTEGER,
                required=True,
                validation_rules={
                    "severity": ValidationSeverity.ERROR
                }
            )
        ]

    def get_output_schema(self) -> List[OutputParameter]:
        return []

    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            # Get required parameters
            store_url = input_data.validated_data["store_url"]
            consumer_key = input_data.validated_data["consumer_key"]
            consumer_secret = input_data.validated_data["consumer_secret"]
            id = input_data.validated_data["id"]

            # Initialize WooCommerce client
            logging.info(f"Initializing WooCommerce client for store: {store_url}")
            wc_config = WooCommerceConfig(
                store_url=store_url,
                consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                auth_type=WooCommerceAuthType.BASIC
            )
            wc = WooCommerceClass(wc_config)

            wc.delete_coupon(coupon_id=id)

            output_data = {}

            return StandardOutput(output_data, self.get_output_schema())

        except Exception as e:
            error_msg = f"Error deleting coupon: {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)


# get_coupon.py
 from typing import List
import logging
from datetime import datetime
from shared.FunctionClass import BaseFunction
from shared.ParameterClass import Parameter, ParameterType
from shared.OutputParameterClass import OutputParameter, OutputParameterType
from shared.InputClass import StandardInput
from shared.OutputClass import StandardOutput
from shared.ValidationClass import ValidationSeverity, CustomValidationType
from functions_classes.WooCommerceClass import WooCommerceClass, WooCommerceConfig, WooCommerceAuthType

class GetWooCommerceCoupon(BaseFunction):
    def get_parameter_schema(self) -> List[Parameter]:
        return [
            Parameter(
                name="store_url",
                param_type=ParameterType.URL,
                required=True,
                validation_rules={
                    CustomValidationType.MIN_LENGTH.value: 1,
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="consumer_key",
                param_type=ParameterType.STRING,
                required=True,
                validation_rules={
                    CustomValidationType.MIN_LENGTH.value: 1,
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="consumer_secret",
                param_type=ParameterType.STRING,
                required=True,
                validation_rules={
                    CustomValidationType.MIN_LENGTH.value: 1,
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="id",
                param_type=ParameterType.INTEGER,
                required=True,
                validation_rules={
                    "severity": ValidationSeverity.ERROR
                }
            ),
        ]

    def get_output_schema(self) -> List[OutputParameter]:
        return [
            OutputParameter(
                key="coupon",
                name="Coupon",
                param_type=OutputParameterType.OBJECT,
                is_array=False,
                parent=None,
                default_value=None
            ),
            OutputParameter(
                key="id",
                name="ID",
                param_type=OutputParameterType.INTEGER,
                is_array=False,
                parent="coupon",
                default_value=None
            ),
            OutputParameter(
                key="code",
                name="Code",
                param_type=OutputParameterType.STRING,
                is_array=False,
                parent="coupon",
                default_value=None
            ),
            OutputParameter(
                key="amount",
                name="Amount",
                param_type=OutputParameterType.STRING,
                is_array=False,
                parent="coupon",
                default_value=None
            ),
            OutputParameter(
                key="date_created",
                name="Date Created",
                param_type=OutputParameterType.STRING,
                is_array=False,
                parent="coupon",
                default_value=None
            ),
            OutputParameter(
                key="date_modified",
                name="Date Modified",
                param_type=OutputParameterType.STRING,
                is_array=False,
                parent="coupon",
                default_value=None
            ),
            OutputParameter(
                key="discount_type",
                name="Discount Type",
                param_type=OutputParameterType.STRING,
                is_array=False,
                parent="coupon",
                default_value=None
            ),
            OutputParameter(
                key="description",
                name="Description",
                param_type=OutputParameterType.STRING,
                is_array=False,
                parent="coupon",
                default_value=None
            ),
            OutputParameter(
                key="date_expires",
                name="Date Expires",
                param_type=OutputParameterType.STRING,
                is_array=False,
                parent="coupon",
                default_value=None
            ),
            OutputParameter(
                key="usage_count",
                name="Usage Count",
                param_type=OutputParameterType.INTEGER,
                is_array=False,
                parent="coupon",
                default_value=None
            ),
            OutputParameter(
                key="individual_use",
                name="Individual Use",
                param_type=OutputParameterType.BOOLEAN,
                is_array=False,
                parent="coupon",
                default_value=None
            ),
            OutputParameter(
                key="product_ids",
                name="Product IDs",
                param_type=OutputParameterType.INTEGER,
                is_array=True,
                parent="coupon",
                default_value=None
            ),
            OutputParameter(
                key="excluded_product_ids",
                name="Excluded Product IDs",
                param_type=OutputParameterType.INTEGER,
                is_array=True,
                parent="coupon",
                default_value=None
            ),
            OutputParameter(
                key="usage_limit",
                name="Usage Limit",
                param_type=OutputParameterType.INTEGER,
                is_array=False,
                parent="coupon",
                default_value=None
            ),
            OutputParameter(
                key="usage_limit_per_user",
                name="Usage Limit Per User",
                param_type=OutputParameterType.INTEGER,
                is_array=False,
                parent="coupon",
                default_value=None
            ),
            OutputParameter(
                key="limit_usage_to_x_items",
                name="Limit Usage to X Items",
                param_type=OutputParameterType.INTEGER,
                is_array=False,
                parent="coupon",
                default_value=None
            ),
            OutputParameter(
                key="free_shipping",
                name="Free Shipping",
                param_type=OutputParameterType.BOOLEAN,
                is_array=False,
                parent="coupon",
                default_value=None
            ),
            OutputParameter(
                key="product_categories",
                name="Product Categories",
                param_type=OutputParameterType.INTEGER,
                is_array=True,
                parent="coupon",
                default_value=None
            ),
            OutputParameter(
                key="exclude_product_categories",
                name="Exclude Product Categories",
                param_type=OutputParameterType.INTEGER,
                is_array=True,
                parent="coupon",
                default_value=None
            ),
            OutputParameter(
                key="exclude_sale_items",
                name="Exclude Sale Items",
                param_type=OutputParameterType.BOOLEAN,
                is_array=False,
                parent="coupon",
                default_value=None
            ),
            OutputParameter(
                key="minimum_amount",
                name="Minimum Amount",
                param_type=OutputParameterType.STRING,
                is_array=False,
                parent="coupon",
                default_value=None
            ),
            OutputParameter(
                key="maximum_amount",
                name="Maximum Amount",
                param_type=OutputParameterType.STRING,
                is_array=False,
                parent="coupon",
                default_value=None
            ),
            OutputParameter(
                key="email_restrictions",
                name="Email Restrictions",
                param_type=OutputParameterType.STRING,
                is_array=True,
                parent="coupon",
                default_value=None
            ),
            OutputParameter(
                key="used_by",
                name="Used By",
                param_type=OutputParameterType.STRING,
                is_array=True,
                parent="coupon",
                default_value=None
            ),
        ]


    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            # Get validated parameters
            logging.info("Extracting validated parameters")
            store_url = input_data.validated_data["store_url"]
            consumer_key = input_data.validated_data["consumer_key"]
            consumer_secret = input_data.validated_data["consumer_secret"]
            coupon_id = input_data.validated_data["id"]

            # Initialize WooCommerce client
            logging.info(f"Initializing WooCommerce client for store: {store_url}")
            wc_config = WooCommerceConfig(
                store_url=store_url,
                consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                auth_type=WooCommerceAuthType.BASIC
            )
            wc = WooCommerceClass(wc_config)

            # Get coupon
            coupon = wc.get_coupon(coupon_id=coupon_id)

            # Extract coupon data
            output_data = {
                "coupon": {
                    "id": coupon.get("id"),
                    "code": coupon.get("code"),
                    "amount": coupon.get("amount"),
                    "date_created": coupon.get("date_created"),
                    "date_modified": coupon.get("date_modified"),
                    "discount_type": coupon.get("discount_type"),
                    "description": coupon.get("description"),
                    "date_expires": coupon.get("date_expires"),
                    "usage_count": coupon.get("usage_count"),
                    "individual_use": coupon.get("individual_use"),
                    "product_ids": coupon.get("product_ids"),
                    "excluded_product_ids": coupon.get("excluded_product_ids"),
                    "usage_limit": coupon.get("usage_limit"),
                    "usage_limit_per_user": coupon.get("usage_limit_per_user"),
                    "limit_usage_to_x_items": coupon.get("limit_usage_to_x_items"),
                    "free_shipping": coupon.get("free_shipping"),
                    "product_categories": coupon.get("product_categories"),
                    "exclude_product_categories": coupon.get("exclude_product_categories"),
                    "exclude_sale_items": coupon.get("exclude_sale_items"),
                    "minimum_amount": coupon.get("minimum_amount"),
                    "maximum_amount": coupon.get("maximum_amount"),
                    "email_restrictions": coupon.get("email_restrictions"),
                    "used_by": coupon.get("used_by")
                }
            }

            # Return the filtered coupons
            return StandardOutput(
                output_data,
                self.get_output_schema()
            )

        except Exception as e:
            error_msg = f"Error retrieving valid coupons: {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)


# get_coupons.py
 from typing import List
import logging
from datetime import datetime
from shared.FunctionClass import BaseFunction
from shared.ParameterClass import Parameter, ParameterType
from shared.OutputParameterClass import OutputParameter, OutputParameterType
from shared.InputClass import StandardInput
from shared.OutputClass import StandardOutput
from shared.ValidationClass import ValidationSeverity, CustomValidationType
from functions_classes.WooCommerceClass import WooCommerceClass, WooCommerceConfig, WooCommerceAuthType

class GetWooCommerceCoupons(BaseFunction):
    def get_parameter_schema(self) -> List[Parameter]:
        return [
            Parameter(
                name="store_url",
                param_type=ParameterType.URL,
                required=True,
                validation_rules={
                    CustomValidationType.MIN_LENGTH.value: 1,
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="consumer_key",
                param_type=ParameterType.STRING,
                required=True,
                validation_rules={
                    CustomValidationType.MIN_LENGTH.value: 1,
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="consumer_secret",
                param_type=ParameterType.STRING,
                required=True,
                validation_rules={
                    CustomValidationType.MIN_LENGTH.value: 1,
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="page",
                param_type=ParameterType.INTEGER,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="per_page",
                param_type=ParameterType.INTEGER,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="search",
                param_type=ParameterType.STRING,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="after",
                param_type=ParameterType.STRING,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="before",
                param_type=ParameterType.STRING,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="modified_after",
                param_type=ParameterType.STRING,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="modified_before",
                param_type=ParameterType.STRING,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="exclude",
                param_type=ParameterType.ARRAY,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="include",
                param_type=ParameterType.ARRAY,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="offset",
                param_type=ParameterType.INTEGER,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="order",
                param_type=ParameterType.SELECT,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.ERROR,
                    CustomValidationType.ALLOWED_VALUES.value: ["asc", "desc"]
                }
            ),
            Parameter(
                name="orderby",
                param_type=ParameterType.SELECT,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.ERROR,
                    CustomValidationType.ALLOWED_VALUES.value: [
                        "id", "date", "title", "slug", "modified", "include"
                    ]
                }
            )
        ]

    def get_output_schema(self) -> List[OutputParameter]:
        return [
            OutputParameter(
                key="coupons",
                name="Coupons",
                param_type=OutputParameterType.OBJECT,
                is_array=True,
                parent=None,
                default_value=None
            ),
            OutputParameter(
                key="id",
                name="ID",
                param_type=OutputParameterType.INTEGER,
                is_array=False,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="code",
                name="Code",
                param_type=OutputParameterType.STRING,
                is_array=False,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="amount",
                name="Amount",
                param_type=OutputParameterType.STRING,
                is_array=False,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="date_created",
                name="Date Created",
                param_type=OutputParameterType.STRING,
                is_array=False,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="date_modified",
                name="Date Modified",
                param_type=OutputParameterType.STRING,
                is_array=False,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="discount_type",
                name="Discount Type",
                param_type=OutputParameterType.STRING,
                is_array=False,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="description",
                name="Description",
                param_type=OutputParameterType.STRING,
                is_array=False,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="date_expires",
                name="Date Expires",
                param_type=OutputParameterType.STRING,
                is_array=False,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="usage_count",
                name="Usage Count",
                param_type=OutputParameterType.INTEGER,
                is_array=False,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="individual_use",
                name="Individual Use",
                param_type=OutputParameterType.BOOLEAN,
                is_array=False,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="product_ids",
                name="Product IDs",
                param_type=OutputParameterType.INTEGER,
                is_array=True,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="excluded_product_ids",
                name="Excluded Product IDs",
                param_type=OutputParameterType.INTEGER,
                is_array=True,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="usage_limit",
                name="Usage Limit",
                param_type=OutputParameterType.INTEGER,
                is_array=False,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="usage_limit_per_user",
                name="Usage Limit Per User",
                param_type=OutputParameterType.INTEGER,
                is_array=False,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="limit_usage_to_x_items",
                name="Limit Usage to X Items",
                param_type=OutputParameterType.INTEGER,
                is_array=False,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="free_shipping",
                name="Free Shipping",
                param_type=OutputParameterType.BOOLEAN,
                is_array=False,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="product_categories",
                name="Product Categories",
                param_type=OutputParameterType.INTEGER,
                is_array=True,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="exclude_product_categories",
                name="Exclude Product Categories",
                param_type=OutputParameterType.INTEGER,
                is_array=True,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="exclude_sale_items",
                name="Exclude Sale Items",
                param_type=OutputParameterType.BOOLEAN,
                is_array=False,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="minimum_amount",
                name="Minimum Amount",
                param_type=OutputParameterType.STRING,
                is_array=False,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="maximum_amount",
                name="Maximum Amount",
                param_type=OutputParameterType.STRING,
                is_array=False,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="email_restrictions",
                name="Email Restrictions",
                param_type=OutputParameterType.STRING,
                is_array=True,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="used_by",
                name="Used By",
                param_type=OutputParameterType.STRING,
                is_array=True,
                parent="coupons",
                default_value=None
            ),
        ]


    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            # Get validated parameters
            logging.info("Extracting validated parameters")
            store_url = input_data.validated_data["store_url"]
            consumer_key = input_data.validated_data["consumer_key"]
            consumer_secret = input_data.validated_data["consumer_secret"]

            # get optional parameters
            optional_parameters = {}
            for param in self.get_parameter_schema():
                if param.name in input_data.validated_data:
                    optional_parameters[param.name] = input_data.validated_data[param.name]

            # Initialize WooCommerce client
            logging.info(f"Initializing WooCommerce client for store: {store_url}")
            wc_config = WooCommerceConfig(
                store_url=store_url,
                consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                auth_type=WooCommerceAuthType.BASIC
            )
            wc = WooCommerceClass(wc_config)

            # Get coupon
            coupons = wc.get_coupons(params=optional_parameters)

            # Format coupons
            formatted_coupons = []

            for coupon in coupons:
                formatted_coupon = {
                    "id": coupon.get("id"),
                    "code": coupon.get("code"),
                    "amount": coupon.get("amount"),
                    "date_created": coupon.get("date_created"),
                    "date_modified": coupon.get("date_modified"),
                    "discount_type": coupon.get("discount_type"),
                    "description": coupon.get("description"),
                    "date_expires": coupon.get("date_expires"),
                    "usage_count": coupon.get("usage_count"),
                    "individual_use": coupon.get("individual_use"),
                    "product_ids": coupon.get("product_ids"),
                    "excluded_product_ids": coupon.get("excluded_product_ids"),
                    "usage_limit": coupon.get("usage_limit"),
                    "usage_limit_per_user": coupon.get("usage_limit_per_user"),
                    "limit_usage_to_x_items": coupon.get("limit_usage_to_x_items"),
                    "free_shipping": coupon.get("free_shipping"),
                    "product_categories": coupon.get("product_categories"),
                    "exclude_product_categories": coupon.get("exclude_product_categories"),
                    "exclude_sale_items": coupon.get("exclude_sale_items"),
                    "minimum_amount": coupon.get("minimum_amount"),
                    "maximum_amount": coupon.get("maximum_amount"),
                    "email_restrictions": coupon.get("email_restrictions"),
                    "used_by": coupon.get("used_by")
                }
                formatted_coupons.append(formatted_coupon)

            # Extract coupon data
            output_data = {
                "coupons": formatted_coupons
            }

            # Return the filtered coupons
            return StandardOutput(
                output_data,
                self.get_output_schema()
            )

        except Exception as e:
            error_msg = f"Error retrieving coupons: {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)


# update_coupon.py
 from typing import List
import logging
from shared.FunctionClass import BaseFunction
from shared.ParameterClass import Parameter, ParameterType
from shared.OutputParameterClass import OutputParameter, OutputParameterType
from shared.InputClass import StandardInput
from shared.OutputClass import StandardOutput
from shared.ValidationClass import ValidationSeverity, CustomValidationType
from functions_classes.WooCommerceClass import WooCommerceClass, WooCommerceConfig, WooCommerceAuthType

class UpdateWooCommerceCoupon(BaseFunction):
    def get_parameter_schema(self) -> List[Parameter]:
        return [
            Parameter(
                name="store_url",
                param_type=ParameterType.URL,
                required=True,
                validation_rules={
                    CustomValidationType.MIN_LENGTH.value: 1,
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="consumer_key",
                param_type=ParameterType.STRING,
                required=True,
                validation_rules={
                    CustomValidationType.MIN_LENGTH.value: 1,
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="consumer_secret",
                param_type=ParameterType.STRING,
                required=True,
                validation_rules={
                    CustomValidationType.MIN_LENGTH.value: 1,
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="id",
                param_type=ParameterType.INTEGER,
                required=True,
                validation_rules={
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="code",
                param_type=ParameterType.STRING,
                required=False,
                validation_rules={
                    CustomValidationType.MIN_LENGTH.value: 1,
                    CustomValidationType.MAX_LENGTH.value: 50,
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="amount",
                param_type=ParameterType.STRING,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="discount_type",
                param_type=ParameterType.SELECT,
                required=False,
                validation_rules={
                    CustomValidationType.ALLOWED_VALUES.value: [
                        "percent", "fixed_cart", "fixed_product"
                    ],
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="description",
                param_type=ParameterType.STRING,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="date_expires",
                param_type=ParameterType.STRING,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="individual_use",
                param_type=ParameterType.BOOLEAN,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="product_ids",
                param_type=ParameterType.ARRAY,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="excluded_product_ids",
                param_type=ParameterType.ARRAY,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="usage_limit",
                param_type=ParameterType.INTEGER,
                required=False,
                validation_rules={
                    CustomValidationType.MIN_VALUE.value: 0,
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="usage_limit_per_user",
                param_type=ParameterType.INTEGER,
                required=False,
                validation_rules={
                    CustomValidationType.MIN_VALUE.value: 0,
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="limit_usage_to_x_items",
                param_type=ParameterType.INTEGER,
                required=False,
                validation_rules={
                    CustomValidationType.MIN_VALUE.value: 0,
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="free_shipping",
                param_type=ParameterType.BOOLEAN,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="product_categories",
                param_type=ParameterType.ARRAY,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="excluded_product_categories",
                param_type=ParameterType.ARRAY,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="exclude_sale_items",
                param_type=ParameterType.BOOLEAN,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="minimum_amount",
                param_type=ParameterType.STRING,
                required=False,
                validation_rules={
                    CustomValidationType.MIN_VALUE.value: 0,
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="maximum_amount",
                param_type=ParameterType.STRING,
                required=False,
                validation_rules={
                    CustomValidationType.MIN_VALUE.value: 0,
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="email_restrictions",
                param_type=ParameterType.ARRAY,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.WARNING
                }
            )
        ]

    def get_output_schema(self) -> List[OutputParameter]:
        return []

    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            # Get required parameters
            logging.info("Extracting validated parameters")
            store_url = input_data.validated_data["store_url"]
            consumer_key = input_data.validated_data["consumer_key"]
            consumer_secret = input_data.validated_data["consumer_secret"]
            coupon_id = input_data.validated_data["id"]

            # Get optional parameters
            optional_parameters = {}
            for param in self.get_parameter_schema():
                if param.name in input_data.validated_data:
                    optional_parameters[param.name] = input_data.validated_data[param.name]

            # Initialize WooCommerce client
            logging.info(f"Initializing WooCommerce client for store: {store_url}")
            wc_config = WooCommerceConfig(
                store_url=store_url,
                consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                auth_type=WooCommerceAuthType.BASIC
            )
            wc = WooCommerceClass(wc_config)

            # Update coupon
            wc.update_coupon(coupon_id, optional_parameters)

            # Return output
            output_data = {}

            logging.info(f"Successfully updated coupon with ID: {coupon_id}")
            return StandardOutput(output_data, self.get_output_schema())

        except Exception as e:
            error_msg = f"Error updating coupon: {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)
