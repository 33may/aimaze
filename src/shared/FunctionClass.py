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
