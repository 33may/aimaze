from shared.FunctionClass import BaseFunction
from shared.ParameterClass import Parameter, ParameterType
from shared.OutputParameterClass import OutputParameter, OutputParameterType
from shared.InputClass import StandardInput
from shared.OutputClass import StandardOutput
import requests

class JSONPlaceholderWrapper(BaseFunction):
    def get_parameter_schema(self):
        return [
            Parameter(name="post_id", param_type=ParameterType.INTEGER, required=True)
        ]

    def get_output_schema(self):
        return [
            OutputParameter(key="id", name="ID", param_type=OutputParameterType.INTEGER),
            OutputParameter(key="title", name="Title", param_type=OutputParameterType.STRING),
            OutputParameter(key="body", name="Body", param_type=OutputParameterType.STRING),
            OutputParameter(key="userId", name="User ID", param_type=OutputParameterType.INTEGER)
        ]

    def process(self, input_data: StandardInput) -> StandardOutput:
        post_id = input_data.validated_data["post_id"]
        response = requests.get(f"https://jsonplaceholder.typicode.com/posts/{post_id}")
        response.raise_for_status()
        post_data = response.json()
        return StandardOutput(post_data, self.get_output_schema())

# Testing the wrapper function
if __name__ == "__main__":
    wrapper = JSONPlaceholderWrapper()
    post_input = StandardInput({"post_id": 1}, wrapper.get_parameter_schema())
    output = wrapper.process(post_input)
    print(output.to_dict())
