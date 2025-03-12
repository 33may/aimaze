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