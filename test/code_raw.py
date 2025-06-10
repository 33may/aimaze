
from shared.FunctionClass import BaseFunction
from shared.ParameterClass import Parameter, ParameterType
from shared.OutputParameterClass import OutputParameter, OutputParameterType
from shared.InputClass import StandardInput
from shared.OutputClass import StandardOutput
from shared.BaseClass import APIWrapper, AuthType
from dataclasses import dataclass
        

@dataclass
class APIClientConfig:
    """Configuration class for API settings"""
    id: int = None,  # Webshop ID required for authentication, typically a unique identifier for the service instance or entity.
    code: str = None,  # API key associated with the user account used for authentication, necessary for secure API access.

    def get_oauth_params(self, method: str, url: str) -> Dict[str, str]:
        return {}

    def validate(self):
        # Asserts here
        pass

    def __init__(self):  # Validation on init.
        self.validate()

api_wrapper = APIWrapper(APIClientConfig(), base_url="https://docs.webwinkelkeur.nl", name="WebWinkel")
    


class Retrieve_Ratings_Summary(BaseFunction):
    """Retrieve a summary of ratings for a specific webshop."""
    name = "Retrieve Ratings Summary"
    url = "https://dashboard.webwinkelkeur.nl/api/ratings/retrieve_summary/"
    args_in_url = False
    method = GET

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="id", param_type=ParameterType.INTEGER, required=True),  # The unique webshop ID. Must be provided as a query parameter.,
			Parameter(name="code", param_type=ParameterType.STRING, required=True),  # Your personal API code. Must be provided as a query parameter.,
			Parameter(name="public_code", param_type=ParameterType.STRING, required=True),  # Use instead of 'code' when fetching data with JavaScript. Must be provided as a query parameter.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="amount", param_type=OutputParameterType.INTEGER, is_array=False),  # Total number of ratings.,
			OutputParameter(name="rating_average", param_type=OutputParameterType.FLOAT, is_array=False),  # Average rating score on a scale of 1 to 5.,
			OutputParameter(name="ratings_average", param_type=OutputParameterType.OBJECT, is_array=False),  # Object containing average scores for specific categories.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Retrieve_Ratings_Summary.method, 
                                           Retrieve_Ratings_Summary.url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Retrieve_Ratings_Summary': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Retrieve_Product_Reviews_in_JSON(BaseFunction):
    """Retrieve a list of product reviews in JSON format."""
    name = "Retrieve Product Reviews in JSON"
    url = "https://dashboard.webwinkelkeur.nl/api/product_reviews/retrieve-json/"
    args_in_url = False
    method = GET

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="id", param_type=ParameterType.INTEGER, required=True),  # The webshop's unique ID.,
			Parameter(name="code", param_type=ParameterType.STRING, required=True),  # Your API code.,
			Parameter(name="public_code", param_type=ParameterType.STRING, required=True),  # Use instead of 'code' when fetching data with JavaScript.,
			Parameter(name="product_id", param_type=ParameterType.STRING, required=False),  # Filter reviews by specific product ID.,
			Parameter(name="offset", param_type=ParameterType.INTEGER, required=False),  # Number of reviews to skip (for pagination).,
			Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # Maximum number of reviews to retrieve.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="total", param_type=OutputParameterType.INTEGER, is_array=False),  # Total number of reviews.,
			OutputParameter(name="product_reviews", param_type=OutputParameterType.OBJECT, is_array=True),  # List of review objects.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Retrieve_Product_Reviews_in_JSON.method, 
                                           Retrieve_Product_Reviews_in_JSON.url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Retrieve_Product_Reviews_in_JSON': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Add_Invitation(BaseFunction):
    """Create or schedule an invitation for a customer."""
    name = "Add Invitation"
    url = "https://dashboard.webwinkelkeur.nl/api/invitations/add/"
    args_in_url = False
    method = GET

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="id", param_type=ParameterType.INTEGER, required=True),  # Webshop's unique ID.,
			Parameter(name="code", param_type=ParameterType.STRING, required=True),  # Your API code.,
			Parameter(name="email", param_type=ParameterType.STRING, required=True),  # Full email address of the customer.,
			Parameter(name="order", param_type=ParameterType.STRING, required=False),  # Order number.,
			Parameter(name="language", param_type=ParameterType.STRING, required=False),  # Language code in ISO-639-1 format.,
			Parameter(name="delay", param_type=ParameterType.INTEGER, required=False),  # Delay in days before sending invitation.,
			Parameter(name="customer_name", param_type=ParameterType.STRING, required=False),  # Name of the customer.,
			Parameter(name="phone_numbers", param_type=ParameterType.STRING, required=False),  # Comma-separated list of phone numbers.,
			Parameter(name="order_total", param_type=ParameterType.FLOAT, required=False),  # Total order amount.,
			Parameter(name="order_data", param_type=OutputParameterType.OBJECT, required=False),  # Additional order data, e.g., product details.,
			Parameter(name="client", param_type=ParameterType.STRING, required=False),  # Name of the originating software/system.,
			Parameter(name="platform_version", param_type=ParameterType.STRING, required=False),  # Version of the originating software/system.,
			Parameter(name="plugin_version", param_type=ParameterType.STRING, required=False),  # Version of the plugin used.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="status", param_type=OutputParameterType.STRING, is_array=False),  # Status of the invitation creation process.,
			OutputParameter(name="message", param_type=OutputParameterType.STRING, is_array=False),  # Additional info message.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Add_Invitation.method, 
                                           Add_Invitation.url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Add_Invitation': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)

