import re
from gen.types import Parameter, ParameterType, OutputParameter, OutputParameterType

from jsonschema import validate
from schemas import SCHEMA
from black import format_str, FileMode


IMPORTS = """
from {types_loc}.FunctionClass import BaseFunction
from {types_loc}.ParameterClass import Parameter, ParameterType
from {types_loc}.OutputParameterClass import OutputParameter, OutputParameterType
from {types_loc}.InputClass import StandardInput
from {types_loc}.OutputClass import StandardOutput
from {types_loc}.BaseClass import APIWrapper, AuthType
from dataclasses import dataclass
        

@dataclass
class APIClientConfig:
    \"\"\"Configuration class for API settings\"\"\"
    consumer_key: str
    consumer_secret: str
    api_version: str = "wc/v3"

    auth_type: AuthType
    verify_ssl: bool = True
    timeout: int = 30
    query_string_auth: bool

    def get_oauth_params(self, method: str, url: str) -> Dict[str, str]:
        return {{"key": consumer_key, "secret": consumer_secret}}

    def __init__(self):  # Validation on init.
        assert(all(x is not None for x in [self.consumer_key, self.consumer_secret]), "Missing required API key, check APIClientConfig.")


api_wrapper = APIWrapper(APIClientConfig(), base_url="{base_url}", name="{api_name}")
    
"""

ENDPOINT_CODE = """

class {class_name}(BaseFunction):
    {endpoint_description}
    name = "{name}"
    url = "{url}"
    args_in_url = {args_in_url}
    method = {method}

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            {input_parameters}
        ]

    def get_output_schema(self):
        return [
            {output_parameters}
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request({class_name}.method, 
                                           {class_name}.url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function '{class_name}': {{str(e)}}"
            logging.error(error_msg)
            raise ValueError(error_msg)

"""

TYPES_IN = {"string": ParameterType.STRING,
            "integer": ParameterType.INTEGER,
            "boolean": ParameterType.BOOLEAN,
            "float": ParameterType.FLOAT,
            "object": OutputParameterType.OBJECT}

TYPES_OUT = {"string": OutputParameterType.STRING,
             "integer": OutputParameterType.INTEGER,
             "boolean": OutputParameterType.BOOLEAN,
             "float": OutputParameterType.FLOAT,
             "object": OutputParameterType.OBJECT}


OUTPUT_PARAM_FORMAT = "OutputParameter(name=\"{name}\", param_type={type}, is_array={is_array}),{comment}"
PARAM_FORMAT = "Parameter(name=\"{name}\", param_type={type}, required={required}),{comment}"
def _encode_parameters(params: list, output: bool) -> list[Parameter] | list[OutputParameter]:
    # "OutputParameter(name=\"{p['name']}\", param_type={TYPES_IN[p['type']]}, is_array={p['is_array']})"
     params = [OUTPUT_PARAM_FORMAT.format(name=p['name'],
                                          type=TYPES_OUT[p['type']],
                                          is_array=p['is_array'],
                                          comment=f"  # {p['description']}" if 'description' in p else "")
               for p in params] if output else \
              [PARAM_FORMAT.format(name=p['name'],
                                   type=TYPES_IN[p['type']],
                                   required=p['required'],
                                   comment=f"  # {p['description']}" if 'description' in p else "")
               for p in params]

     return ",\n\t\t\t".join(params)


def wrap_api(schema: dict, base_url: str, api_name: str) -> str:
    validate(instance=schema, schema=SCHEMA)

    code = IMPORTS.format(base_url=base_url, api_name=api_name, types_loc="shared")

    code += "".join([ENDPOINT_CODE.format(class_name=re.sub("\W", "", endpoint["name"].replace(" ", "_")),
                                          name=endpoint["name"],
                                          url=endpoint["url"],
                                          args_in_url=endpoint["args_in_url"],
                                          method=endpoint["method"],
                                          endpoint_description=f"\"\"\"{endpoint['description']}\"\"\"" if 'description' in endpoint else "",
                                          input_parameters=_encode_parameters(endpoint["input_parameters"], output=False),
                                          output_parameters=_encode_parameters(endpoint["output_parameters"], output=True),
                                          )
                     for endpoint in schema["endpoints"]])

    # print("\n".join([f"{i} {line}" for i, line in enumerate(code.split("\n"))]))
    return format_str(code, mode=FileMode())
