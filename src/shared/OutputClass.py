from typing import Any, Dict, List
import json
import logging
from OutputParameterClass import OutputParameter, OutputParameterSchema, OutputParameterValidationError

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
