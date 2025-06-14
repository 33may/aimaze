import re
from gen.types import Parameter, ParameterType, OutputParameter, OutputParameterType

from jsonschema import validate
from schemas import SCHEMA_PARSE
from black import format_str, FileMode


IMPORTS = """
from FunctionClass import BaseFunction
from ParameterClass import Parameter, ParameterType
from OutputParameterClass import OutputParameter, OutputParameterType
from InputClass import StandardInput
from OutputClass import StandardOutput

# from {types_loc}.FunctionClass import BaseFunction
# from {types_loc}.ParameterClass import Parameter, ParameterType
# from {types_loc}.OutputParameterClass import OutputParameter, OutputParameterType
# from {types_loc}.InputClass import StandardInput
# from {types_loc}.OutputClass import StandardOutput

from dataclasses import dataclass
import logging
        

METHODS = {{"GET": get,
           "POST": post}}

@dataclass
class APIClientConfig:
    \"\"\"Configuration class for API settings\"\"\"
    base_url="{base_url}"
    name="{api_name}"

{variables}

    def get_oauth_params(self, method: str, url: str) -> dict[str, str]:
        return {{}}

    def validate(self):
        # Asserts here
        pass

    def authenticate(self):
        # For authentication done before calls, not during.
        pass

    def __init__(self): 
        self.validate()
        self.authenticate()

    def request(self, method: str, url: str, args_in_url: bool, data: dict) -> dict[str, any]:
        if args_in_url:
            url = url.format(**data)  # TODO: Take in-url args out of payload. Probably best with template string.

        response = METHODS[method](url, data=data)
        
        if response.status_code != 200:
            raise Exception(response.text)

        return json.loads(response.text)

"""

ENDPOINT_CODE = """

class {class_name}(BaseFunction):
    {endpoint_description}
    name = "{name}"
    url = "{url}"
    args_in_url = {args_in_url}
    method = "{method}"

    def __init__(self):
        self.api_config = APIClientConfig()
    
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
            out = self.api_config.request({class_name}.method, 
                                          {class_name}.url,
                                          {class_name}.args_in_url,
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
                                          comment=f"  # {p['description'].replace('\n', '')}" if 'description' in p else "")
               for p in params] if output else \
              [PARAM_FORMAT.format(name=p['name'],
                                   type=TYPES_IN[p['type']],
                                   required=p['required'],
                                   comment=f"  # {p['description'].replace('\n', '')}" if 'description' in p else "")
               for p in params]

     return ",\n\t\t\t".join(params)


def default_or_none(default: str, var_type: str) -> str:
    if default == "None": return default

    if not default: return "None"

    if var_type == "str" and not default.startswith('"'):
        return f'"{default}"'


def wrap_api(schema: dict, base_url: str, api_name: str) -> str:
    validate(instance=schema, schema=SCHEMA_PARSE)

    # //TODO fix Fields with a default value must come after any fields without a default.
    # //TODO fix when using filed of the class use self 

    config_vars = [f"    # {v['explanation']}\n    {v['var_name'].replace('-', '_')}: {v['type']} = {default_or_none(v['default_val'], v['type'])}" for v in schema["general_info"]]
    print(config_vars)

    code = IMPORTS.format(base_url=base_url, 
                          api_name=api_name, 
                          types_loc="shared",
                          variables="\n\n".join(config_vars))

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

    with open("test/code_raw.py", "w") as f:
        f.write(code)
    # print("\n".join([f"{i} {line}" for i, line in enumerate(code.split("\n"))]))
    return format_str(code, mode=FileMode())
