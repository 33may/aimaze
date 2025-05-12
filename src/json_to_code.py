from shared.ParameterClass import Parameter, ParameterType
from shared.OutputParameterClass import OutputParameter, OutputParameterType

from jsonschema import validate
from shared.schema import SCHEMA


IMPORTS = """
from shared.FunctionClass import BaseFunction
from shared.ParameterClass import Parameter, ParameterType
from shared.OutputParameterClass import OutputParameter, OutputParameterType
from shared.InputClass import StandardInput
from shared.OutputClass import StandardOutput
import requests

"""
ENDPOINT_CODE = """

class {class_name}(BaseFunction):
    {endpoint_description}
    name = "{name}"
    url = "{url}"
    args_in_url = {args_in_url}
    
    def get_parameter_schema(self):
        return [
            {input_parameters}
        ]

    def get_output_schema(self):
        return [
            {output_parameters}
        ]

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


OUTPUT_PARAM_FORMAT = "OutputParameter(name=\"{name}\", param_type={type}, is_array={is_array})  {comment}"
PARAM_FORMAT = "Parameter(name=\"{name}\", param_type={type}, required={required})  {comment}"
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


def wrap_api(schema: dict) -> str:
    validate(instance=schema, schema=SCHEMA)

    return IMPORTS + "".join([ENDPOINT_CODE.format(class_name=endpoint["name"].replace(" ", "_"),
                                                   name=endpoint["name"],
                                                   url=endpoint["url"],
                                                   args_in_url=endpoint["args_in_url"],
                                                   endpoint_description=f"\"\"\"\n\t{endpoint['description']}\n\t\"\"\"\n" if 'description' in endpoint else "",
                                                   input_parameters=_encode_parameters(endpoint["input_parameters"], output=False),
                                                   output_parameters=_encode_parameters(endpoint["output_parameters"], output=True),
                                                   )
                              for endpoint in schema["endpoints"]])