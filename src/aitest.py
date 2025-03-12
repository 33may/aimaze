from typing import List, Dict, Any, Optional
import logging
import requests
from shared.FunctionClass import BaseFunction
from shared.ParameterClass import Parameter, ParameterType
from shared.OutputParameterClass import OutputParameter, OutputParameterType
from shared.InputClass import StandardInput
from shared.OutputClass import StandardOutput
from shared.ValidationClass import ValidationSeverity, CustomValidationType

class JSONPlaceholderAPI(BaseFunction):
    """Wrapper for JSONPlaceholder API calls"""

    def get_parameter_schema(self) -> List[Parameter]:
        """Define parameter schema for JSONPlaceholder API"""
        return [
            Parameter(
                name="method",
                param_type=ParameterType.SELECT,
                required=True,
                validation_rules={
                    CustomValidationType.ALLOWED_VALUES.value: [
                        "GET", "POST", "PUT", "PATCH", "DELETE"
                    ],
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="resource",
                param_type=ParameterType.SELECT,
                required=True,
                validation_rules={
                    CustomValidationType.ALLOWED_VALUES.value: [
                        "posts", "comments", "albums", "photos", "todos", "users"
                    ],
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="id",
                param_type=ParameterType.INTEGER,
                required=False,
                validation_rules={
                    CustomValidationType.MIN_VALUE.value: 1,
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="sub_resource",
                param_type=ParameterType.SELECT,
                required=False,
                validation_rules={
                    CustomValidationType.ALLOWED_VALUES.value: [
                        "comments", "photos", "albums", "todos", "posts"
                    ],
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="query_params",
                param_type=ParameterType.DYNAMIC,
                required=False
            ),
            Parameter(
                name="body",
                param_type=ParameterType.DYNAMIC,
                required=False
            )
        ]

    def get_output_schema(self) -> List[OutputParameter]:
        """Define output schema for JSONPlaceholder API"""
        return [
            OutputParameter(
                key="status_code",
                name="Status Code",
                param_type=OutputParameterType.INTEGER
            ),
            OutputParameter(
                key="data",
                name="Response Data",
                param_type=OutputParameterType.DYNAMIC
            )
        ]

    def process(self, input_data: StandardInput) -> StandardOutput:
        """Process the input data and make request to JSONPlaceholder API"""
        try:
            # Extract parameters
            method = input_data.validated_data["method"]
            resource = input_data.validated_data["resource"]
            resource_id = input_data.validated_data.get("id")
            sub_resource = input_data.validated_data.get("sub_resource")
            query_params = input_data.validated_data.get("query_params", {})
            body = input_data.validated_data.get("body", {})

            # Construct URL
            base_url = "https://jsonplaceholder.typicode.com"
            url_parts = [base_url, resource]

            if resource_id:
                url_parts.append(str(resource_id))

            if sub_resource:
                url_parts.append(sub_resource)

            url = "/".join(url_parts)

            # Set headers
            headers = {
                "Content-type": "application/json; charset=UTF-8"
            }

            # Make request
            logging.info(f"Making {method} request to {url}")

            if method == "GET":
                response = requests.get(url, params=query_params)
            elif method == "POST":
                response = requests.post(url, json=body, headers=headers)
            elif method == "PUT":
                response = requests.put(url, json=body, headers=headers)
            elif method == "PATCH":
                response = requests.patch(url, json=body, headers=headers)
            elif method == "DELETE":
                response = requests.delete(url)
            else:
                raise ValueError(f"Unsupported method: {method}")

            # Process response
            status_code = response.status_code

            # Parse response data if it's not a DELETE request
            if method != "DELETE":
                try:
                    data = response.json()
                except ValueError:
                    data = {"message": response.text}
            else:
                data = {"message": "Resource deleted successfully"}

            # Prepare output
            output_data = {
                "status_code": status_code,
                "data": data
            }

            return StandardOutput(output_data, self.get_output_schema())

        except Exception as e:
            error_msg = f"Error processing JSONPlaceholder API request: {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)


# Test function to verify the integrity of the script
def test_jsonplaceholder_api():
    """Minimal test for JSONPlaceholder API wrapper"""
    # Create instance of JSONPlaceholderAPI
    api = JSONPlaceholderAPI()

    # Create test input
    test_input = {
        "method": "GET",
        "resource": "posts",
        "id": 1
    }

    # Create StandardInput with the test data
    from shared.InputClass import StandardInput
    input_data = StandardInput(test_input, api.get_parameter_schema())

    # Process the request
    output = api.process(input_data)

    # Print the output
    print(f"Status Code: {output.output_data['status_code']}")
    print(f"Data: {output.output_data['data']}")

    return output.output_data['status_code'] == 200


if __name__ == "__main__":
    # Run the test
    success = test_jsonplaceholder_api()
    print(f"Test {'passed' if success else 'failed'}")
