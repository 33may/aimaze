import ast
import re
from typing import Any
from ParameterClass import Parameter, ParameterType
from ValidationClass import ValidationResult, ValidationSeverity, CustomValidationType
from urllib.parse import urlparse, ParseResult
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
                                value = re.sub(r'([{,])\s*([a-zA-Z0-9_]+)\s*:', r'\1"\2":', value)
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
