
from shared.FunctionClass import BaseFunction
from shared.InputClass import StandardInput
from shared.OutputClass import StandardOutput
from shared.ParameterClass import Parameter, ParameterType
from shared.OutputParameterClass import OutputParameter, OutputParameterType
from typing import List, Dict, Any
import requests

class JSONPlaceholderWrapper(BaseFunction):

    def get_parameter_schema(self) -> List[Parameter]:
        return [
            Parameter(
                name="post_id",
                param_type=ParameterType.INTEGER,
                required=True
            )
        ]

    def get_output_schema(self) -> List[OutputParameter]:
        return [
            OutputParameter(
                key="post",
                name="Post",
                param_type=OutputParameterType.OBJECT,
                is_array=False
            ),
            OutputParameter(
                key="id",
                name="ID",
                param_type=OutputParameterType.INTEGER,
                is_array=False,
                parent="post"
            ),
            OutputParameter(
                key="title",
                name="Title",
                param_type=OutputParameterType.STRING,
                is_array=False,
                parent="post"
            ),
            OutputParameter(
                key="body",
                name="Body",
                param_type=OutputParameterType.STRING,
                is_array=False,
                parent="post"
            ),
            OutputParameter(
                key="userId",
                name="User ID",
                param_type=OutputParameterType.INTEGER,
                is_array=False,
                parent="post"
            )
        ]

    def process(self, input_data: StandardInput) -> StandardOutput:
        post_id = input_data.validated_data.get("post_id")
        response = requests.get(f'https://jsonplaceholder.typicode.com/posts/{post_id}')
        
        if response.status_code != 200:
            raise ValueError(f"Failed to fetch post with ID {post_id}")
        
        post_data = response.json()

        output_data = {
            "post": {
                "id": post_data.get("id"),
                "title": post_data.get("title"),
                "body": post_data.get("body"),
                "userId": post_data.get("userId")
            }
        }

        return StandardOutput(output_data, self.get_output_schema())

# Minimal test run
if __name__ == "__main__":
    import json
    from shared.InputClass import StandardInput
    from shared.OutputClass import StandardOutput
    from shared.ParameterClass import Parameter, ParameterType
    
    test_input_data = StandardInput(
        raw_data={"post_id": 1},
        parameter_schema=[
            Parameter(
                name="post_id",
                param_type=ParameterType.INTEGER,
                required=True
            )
        ]
    )

    json_placeholder_wrapper = JSONPlaceholderWrapper()
    test_output = json_placeholder_wrapper.process(test_input_data)

    # Print the output directly
    print(json.dumps(test_output.to_dict(), indent=2))
