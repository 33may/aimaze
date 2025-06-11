from FunctionClass import BaseFunction
from ParameterClass import Parameter, ParameterType
from OutputParameterClass import OutputParameter, OutputParameterType
from InputClass import StandardInput
from OutputClass import StandardOutput
# from BaseClass import AuthType
from dataclasses import dataclass

@dataclass
class APIClientConfig:
    """Configuration class for API settings"""

    code: str = (None,)  # Personal API access code, used for authentication.
    public_code: str = (None,)  # Optional public code to fetch data via JavaScript.

    def get_oauth_params(self, method: str, url: str) -> dict[str, str]:
        return {}

    def validate(self):
        # Asserts here
        pass

    def __init__(self):  # Validation on init.
        self.validate()


api_wrapper = APIWrapper(
    APIClientConfig(), base_url="https://docs.webwinkelkeur.nl", name="WebWinkel"
)


class Retrieve_ratings_summary_as_JSON(BaseFunction):
    """API endpoint to retrieve an overall rating summary for a given webshop."""

    name = "Retrieve ratings summary as JSON"
    url = "https://dashboard.webwinkelkeur.nl/api/ratings/retrieve_summary/"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper

    def get_parameter_schema(self):
        return [
            Parameter(
                name="id", param_type=ParameterType.INTEGER, required=True
            ),  # The unique webshop ID.,
            Parameter(
                name="code", param_type=ParameterType.STRING, required=True
            ),  # Your personal API code.,
            Parameter(
                name="public_code", param_type=ParameterType.STRING, required=True
            ),  # Use instead of 'code' when fetching data with JavaScript.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(
                name="status", param_type=OutputParameterType.STRING, is_array=False
            ),  # Operation status: 'success' or 'error'.,
            OutputParameter(
                name="message", param_type=OutputParameterType.STRING, is_array=False
            ),  # Additional info about the operation.,
            OutputParameter(
                name="data", param_type=OutputParameterType.OBJECT, is_array=False
            ),  # Container for the rating summary details.,
            OutputParameter(
                name="amount", param_type=OutputParameterType.INTEGER, is_array=False
            ),  # Total number of ratings.,
            OutputParameter(
                name="rating_average",
                param_type=OutputParameterType.FLOAT,
                is_array=False,
            ),  # Average rating on a scale of 1-5.,
            OutputParameter(
                name="ratings_average",
                param_type=OutputParameterType.OBJECT,
                is_array=False,
            ),  # Average ratings per category.,
            OutputParameter(
                name="shippingtime",
                param_type=OutputParameterType.FLOAT,
                is_array=False,
            ),  # Average shipping time rating.,
            OutputParameter(
                name="customerservice",
                param_type=OutputParameterType.FLOAT,
                is_array=False,
            ),  # Average customer service rating.,
            OutputParameter(
                name="pricequality",
                param_type=OutputParameterType.FLOAT,
                is_array=False,
            ),  # Average price-quality rating.,
            OutputParameter(
                name="aftersale", param_type=OutputParameterType.FLOAT, is_array=False
            ),  # Average aftersale service rating.
        ]

    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(
                Retrieve_ratings_summary_as_JSON.method,
                Retrieve_ratings_summary_as_JSON.url,
                Retrieve_ratings_summary_as_JSON.args_in_url,
                input_data.validated_data,
            )
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = (
                f"Error running function 'Retrieve_ratings_summary_as_JSON': {str(e)}"
            )
            logging.error(error_msg)
            raise ValueError(error_msg)


class Retrieve_JSON_product_reviews(BaseFunction):
    """API endpoint to retrieve a list of product reviews in JSON format."""

    name = "Retrieve JSON product reviews"
    url = "https://dashboard.webwinkelkeur.nl/api/1.0/product_reviews.json"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper

    def get_parameter_schema(self):
        return [
            Parameter(
                name="id", param_type=ParameterType.INTEGER, required=True
            ),  # The unique webshop ID.,
            Parameter(
                name="code", param_type=ParameterType.STRING, required=True
            ),  # Your personal API code.,
            Parameter(
                name="public_code", param_type=ParameterType.STRING, required=True
            ),  # Use instead of 'code' when fetching data with JavaScript.,
            Parameter(
                name="product_id", param_type=ParameterType.STRING, required=False
            ),  # Filter reviews by specific product ID.,
            Parameter(
                name="offset", param_type=ParameterType.INTEGER, required=False
            ),  # Number of reviews to skip for pagination.,
            Parameter(
                name="limit", param_type=ParameterType.INTEGER, required=False
            ),  # Maximum number of reviews to retrieve.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(
                name="total", param_type=OutputParameterType.INTEGER, is_array=False
            ),  # Total number of reviews available.,
            OutputParameter(
                name="product_reviews",
                param_type=OutputParameterType.OBJECT,
                is_array=True,
            ),  # List of review objects returned.,
            OutputParameter(
                name="id", param_type=OutputParameterType.INTEGER, is_array=False
            ),  # Review ID.,
            OutputParameter(
                name="reviewer", param_type=OutputParameterType.OBJECT, is_array=False
            ),  # Reviewer details.,
            OutputParameter(
                name="name", param_type=OutputParameterType.STRING, is_array=False
            ),  # Name of the reviewer.,
            OutputParameter(
                name="email", param_type=OutputParameterType.STRING, is_array=False
            ),  # Reviewer email address.,
            OutputParameter(
                name="rating", param_type=OutputParameterType.INTEGER, is_array=False
            ),  # Rating scored, typically 1-5.,
            OutputParameter(
                name="review", param_type=OutputParameterType.STRING, is_array=False
            ),  # Review text.,
            OutputParameter(
                name="product_id", param_type=OutputParameterType.STRING, is_array=False
            ),  # Associated product ID.,
            OutputParameter(
                name="language", param_type=OutputParameterType.STRING, is_array=False
            ),  # Review language code.,
            OutputParameter(
                name="deleted", param_type=OutputParameterType.BOOLEAN, is_array=False
            ),  # Deletion status of the review.,
            OutputParameter(
                name="created", param_type=OutputParameterType.STRING, is_array=False
            ),  # Review creation timestamp.
        ]

    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(
                Retrieve_JSON_product_reviews.method,
                Retrieve_JSON_product_reviews.url,
                input_data.validated_data,
            )
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = (
                f"Error running function 'Retrieve_JSON_product_reviews': {str(e)}"
            )
            logging.error(error_msg)
            raise ValueError(error_msg)


class Retrieve_individual_webshop_details_as_JSON(BaseFunction):
    """API endpoint to retrieve detailed webshop information."""

    name = "Retrieve individual webshop details as JSON"
    url = "https://dashboard.webwinkelkeur.nl/api/1.0/webshop.json"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper

    def get_parameter_schema(self):
        return [
            Parameter(
                name="id", param_type=ParameterType.INTEGER, required=True
            ),  # The unique webshop ID.,
            Parameter(
                name="code", param_type=ParameterType.STRING, required=True
            ),  # Your personal API code.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(
                name="status", param_type=OutputParameterType.STRING, is_array=False
            ),  # Operation status.,
            OutputParameter(
                name="message", param_type=OutputParameterType.STRING, is_array=False
            ),  # Details about the retrieval.,
            OutputParameter(
                name="data", param_type=OutputParameterType.OBJECT, is_array=False
            ),  # Webshop data object.,
            OutputParameter(
                name="name", param_type=OutputParameterType.STRING, is_array=False
            ),  # Webshop name.,
            OutputParameter(
                name="address", param_type=OutputParameterType.OBJECT, is_array=False
            ),  # Webshop address details.,
            OutputParameter(
                name="street", param_type=OutputParameterType.STRING, is_array=False
            ),  # Street address.,
            OutputParameter(
                name="housenumber",
                param_type=OutputParameterType.STRING,
                is_array=False,
            ),  # Housenumber.,
            OutputParameter(
                name="postalcode", param_type=OutputParameterType.STRING, is_array=False
            ),  # Postal code.,
            OutputParameter(
                name="city", param_type=OutputParameterType.STRING, is_array=False
            ),  # City name.,
            OutputParameter(
                name="country", param_type=OutputParameterType.STRING, is_array=False
            ),  # Country name.,
            OutputParameter(
                name="logo", param_type=OutputParameterType.STRING, is_array=False
            ),  # URL link to the webshop logo.,
            OutputParameter(
                name="languages", param_type=OutputParameterType.OBJECT, is_array=True
            ),  # Supported languages over the webshop.,
            OutputParameter(
                name="name", param_type=OutputParameterType.STRING, is_array=False
            ),  # Language name.,
            OutputParameter(
                name="url", param_type=OutputParameterType.STRING, is_array=False
            ),  # Webpage URL for the language.,
            OutputParameter(
                name="iso", param_type=OutputParameterType.STRING, is_array=False
            ),  # ISO language code.,
            OutputParameter(
                name="all", param_type=OutputParameterType.BOOLEAN, is_array=False
            ),  # Indicates if all pages are in this language.,
            OutputParameter(
                name="main", param_type=OutputParameterType.BOOLEAN, is_array=False
            ),  # Indicates if this is the main language.
        ]

    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(
                Retrieve_individual_webshop_details_as_JSON.method,
                Retrieve_individual_webshop_details_as_JSON.url,
                input_data.validated_data,
            )
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Retrieve_individual_webshop_details_as_JSON': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)
