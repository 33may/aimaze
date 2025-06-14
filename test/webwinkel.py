from FunctionClass import BaseFunction
from ParameterClass import Parameter, ParameterType
from OutputParameterClass import OutputParameter, OutputParameterType
from InputClass import StandardInput
from OutputClass import StandardOutput
from BaseClass import APIWrapper

# from shared.FunctionClass import BaseFunction
# from shared.ParameterClass import Parameter, ParameterType
# from shared.OutputParameterClass import OutputParameter, OutputParameterType
# from shared.InputClass import StandardInput
# from shared.OutputClass import StandardOutput
# from shared.BaseClass import APIWrapper, AuthType

from dataclasses import dataclass
import logging


@dataclass
class APIClientConfig:
    """Configuration class for API settings"""

    # Personal API key used for authenticating requests. To be securely stored and included in API requests for authorization.
    code: str = None

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


class Retrieve_ratings_summary(BaseFunction):
    """Retrieve a summary of all ratings for a specific webshop."""

    name = "Retrieve ratings summary"
    url = "/1.0/ratings_summary.json"
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
            ),  # Use instead of 'code' if fetching data with JavaScript.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(
                name="status", param_type=OutputParameterType.STRING, is_array=False
            ),  # Status of the response, e.g., 'success' or 'error'.,
            OutputParameter(
                name="message", param_type=OutputParameterType.STRING, is_array=False
            ),  # Additional message about the response.,
            OutputParameter(
                name="amount", param_type=OutputParameterType.INTEGER, is_array=False
            ),  # Number of ratings.,
            OutputParameter(
                name="rating_average",
                param_type=OutputParameterType.FLOAT,
                is_array=False,
            ),  # Average rating score on a scale of 1-5.,
            OutputParameter(
                name="ratings_average",
                param_type=OutputParameterType.OBJECT,
                is_array=False,
            ),  # Average scores per category, e.g., shippingtime, customerservice.
        ]

    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(
                Retrieve_ratings_summary.method,
                Retrieve_ratings_summary.url,
                Retrieve_ratings_summary.args_in_url,
                input_data.validated_data,
            )
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Retrieve_ratings_summary': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)


class Retrieve_webshop_details(BaseFunction):
    """Retrieve detailed information about a webshop using its ID."""

    name = "Retrieve webshop details"
    url = "/1.0/webshop.json"
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
            ),  # Response status, e.g., 'success' or 'error'.,
            OutputParameter(
                name="message", param_type=OutputParameterType.STRING, is_array=False
            ),  # Additional message.,
            OutputParameter(
                name="name", param_type=OutputParameterType.STRING, is_array=False
            ),  # Name of the webshop.,
            OutputParameter(
                name="address", param_type=OutputParameterType.OBJECT, is_array=False
            ),  # Address details of the webshop.,
            OutputParameter(
                name="logo", param_type=OutputParameterType.STRING, is_array=False
            ),  # URL to the webshop's logo image.,
            OutputParameter(
                name="languages", param_type=OutputParameterType.OBJECT, is_array=True
            ),  # Supported languages with details.
        ]

    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(
                Retrieve_webshop_details.method,
                Retrieve_webshop_details.url,
                Retrieve_webshop_details.args_in_url,
                input_data.validated_data,
            )
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Retrieve_webshop_details': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)


class Retrieve_JSON_product_reviews(BaseFunction):
    """Retrieve a list of product reviews in JSON format for a specific webshop."""

    name = "Retrieve JSON product reviews"
    url = "/1.0/product_reviews.json"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper

    def get_parameter_schema(self):
        return [
            Parameter(
                name="id", param_type=ParameterType.INTEGER, required=True
            ),  # The webshop ID.,
            Parameter(
                name="code", param_type=ParameterType.STRING, required=True
            ),  # Your personal API code.,
            Parameter(
                name="public_code", param_type=ParameterType.STRING, required=True
            ),  # Use instead of 'code' for JavaScript.,
            Parameter(
                name="product_id", param_type=ParameterType.STRING, required=False
            ),  # Filter reviews by specific product ID.,
            Parameter(
                name="offset", param_type=ParameterType.INTEGER, required=False
            ),  # Number of reviews to skip (for pagination).,
            Parameter(
                name="limit", param_type=ParameterType.INTEGER, required=False
            ),  # Maximum number of reviews to return.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(
                name="total", param_type=OutputParameterType.INTEGER, is_array=False
            ),  # Total number of reviews.,
            OutputParameter(
                name="product_reviews",
                param_type=OutputParameterType.OBJECT,
                is_array=True,
            ),  # Array of review objects.
        ]

    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(
                Retrieve_JSON_product_reviews.method,
                Retrieve_JSON_product_reviews.url,
                Retrieve_JSON_product_reviews.args_in_url,
                input_data.validated_data,
            )
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = (
                f"Error running function 'Retrieve_JSON_product_reviews': {str(e)}"
            )
            logging.error(error_msg)
            raise ValueError(error_msg)


class Add_a_product_review(BaseFunction):
    """Add a new product review to a webshop."""

    name = "Add a product review"
    url = "/1.0/product_reviews/add/"
    args_in_url = True
    method = "PUT"

    def __init__(self):
        self.api_wrapper = api_wrapper

    def get_parameter_schema(self):
        return [
            Parameter(
                name="id", param_type=ParameterType.INTEGER, required=True
            ),  # Webshop ID.,
            Parameter(
                name="code", param_type=ParameterType.STRING, required=True
            ),  # Your personal API code.,
            Parameter(
                name="public_code", param_type=ParameterType.STRING, required=True
            ),  # Use instead of 'code' for JavaScript.,
            Parameter(
                name="reviewer_name", param_type=ParameterType.STRING, required=True
            ),  # Name of the reviewer.,
            Parameter(
                name="rating", param_type=ParameterType.INTEGER, required=True
            ),  # Rating score, 1-5.,
            Parameter(
                name="review_text", param_type=ParameterType.STRING, required=False
            ),  # Optional review text.,
            Parameter(
                name="product_id", param_type=ParameterType.STRING, required=True
            ),  # ID of the product being reviewed.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(
                name="status", param_type=OutputParameterType.STRING, is_array=False
            ),  # Response status, e.g., 'success'.,
            OutputParameter(
                name="message", param_type=OutputParameterType.STRING, is_array=False
            ),  # Additional message.
        ]

    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(
                Add_a_product_review.method,
                Add_a_product_review.url,
                Add_a_product_review.args_in_url,
                input_data.validated_data,
            )
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Add_a_product_review': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)
