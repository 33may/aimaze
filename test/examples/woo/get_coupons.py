from typing import List
import logging
from datetime import datetime
from FunctionClass import BaseFunction
from ParameterClass import Parameter, ParameterType
from OutputParameterClass import OutputParameter, OutputParameterType
from InputClass import StandardInput
from OutputClass import StandardOutput
from ValidationClass import ValidationSeverity, CustomValidationType
# from functions_classes.WooCommerceClass import WooCommerceClass, WooCommerceConfig, WooCommerceAuthType

class GetWooCommerceCoupons(BaseFunction):
    def get_parameter_schema(self) -> List[Parameter]:
        return [
            Parameter(
                name="store_url",
                param_type=ParameterType.URL,
                required=True,
                validation_rules={
                    CustomValidationType.MIN_LENGTH.value: 1,
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="consumer_key",
                param_type=ParameterType.STRING,
                required=True,
                validation_rules={
                    CustomValidationType.MIN_LENGTH.value: 1,
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="consumer_secret",
                param_type=ParameterType.STRING,
                required=True,
                validation_rules={
                    CustomValidationType.MIN_LENGTH.value: 1,
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="page",
                param_type=ParameterType.INTEGER,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="per_page",
                param_type=ParameterType.INTEGER,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="search",
                param_type=ParameterType.STRING,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="after",
                param_type=ParameterType.STRING,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="before",
                param_type=ParameterType.STRING,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="modified_after",
                param_type=ParameterType.STRING,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="modified_before",
                param_type=ParameterType.STRING,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="exclude",
                param_type=ParameterType.ARRAY,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="include",
                param_type=ParameterType.ARRAY,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="offset",
                param_type=ParameterType.INTEGER,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="order",
                param_type=ParameterType.SELECT,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.ERROR,
                    CustomValidationType.ALLOWED_VALUES.value: ["asc", "desc"]
                }
            ),
            Parameter(
                name="orderby",
                param_type=ParameterType.SELECT,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.ERROR,
                    CustomValidationType.ALLOWED_VALUES.value: [
                        "id", "date", "title", "slug", "modified", "include"
                    ]
                }
            )
        ]
    
    def get_output_schema(self) -> List[OutputParameter]:
        return [
            OutputParameter(
                key="coupons",
                name="Coupons",
                param_type=OutputParameterType.OBJECT,
                is_array=True,
                parent=None,
                default_value=None
            ),
            OutputParameter(
                key="id",
                name="ID",
                param_type=OutputParameterType.INTEGER,
                is_array=False,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="code",
                name="Code",
                param_type=OutputParameterType.STRING,
                is_array=False,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="amount",
                name="Amount",
                param_type=OutputParameterType.STRING,
                is_array=False,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="date_created",
                name="Date Created",
                param_type=OutputParameterType.STRING,
                is_array=False,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="date_modified",
                name="Date Modified",
                param_type=OutputParameterType.STRING,
                is_array=False,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="discount_type",
                name="Discount Type",
                param_type=OutputParameterType.STRING,
                is_array=False,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="description",
                name="Description",
                param_type=OutputParameterType.STRING,
                is_array=False,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="date_expires",
                name="Date Expires",
                param_type=OutputParameterType.STRING,
                is_array=False,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="usage_count",
                name="Usage Count",
                param_type=OutputParameterType.INTEGER,
                is_array=False,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="individual_use",
                name="Individual Use",
                param_type=OutputParameterType.BOOLEAN,
                is_array=False,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="product_ids",
                name="Product IDs",
                param_type=OutputParameterType.INTEGER,
                is_array=True,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="excluded_product_ids",
                name="Excluded Product IDs",
                param_type=OutputParameterType.INTEGER,
                is_array=True,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="usage_limit",
                name="Usage Limit",
                param_type=OutputParameterType.INTEGER,
                is_array=False,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="usage_limit_per_user",
                name="Usage Limit Per User",
                param_type=OutputParameterType.INTEGER,
                is_array=False,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="limit_usage_to_x_items",
                name="Limit Usage to X Items",
                param_type=OutputParameterType.INTEGER,
                is_array=False,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="free_shipping",
                name="Free Shipping",
                param_type=OutputParameterType.BOOLEAN,
                is_array=False,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="product_categories",
                name="Product Categories",
                param_type=OutputParameterType.INTEGER,
                is_array=True,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="exclude_product_categories",
                name="Exclude Product Categories",
                param_type=OutputParameterType.INTEGER,
                is_array=True,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="exclude_sale_items",
                name="Exclude Sale Items",
                param_type=OutputParameterType.BOOLEAN,
                is_array=False,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="minimum_amount",
                name="Minimum Amount",
                param_type=OutputParameterType.STRING,
                is_array=False,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="maximum_amount",
                name="Maximum Amount",
                param_type=OutputParameterType.STRING,
                is_array=False,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="email_restrictions",
                name="Email Restrictions",
                param_type=OutputParameterType.STRING,
                is_array=True,
                parent="coupons",
                default_value=None
            ),
            OutputParameter(
                key="used_by",
                name="Used By",
                param_type=OutputParameterType.STRING,
                is_array=True,
                parent="coupons",
                default_value=None
            ),
        ]

    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            # Get validated parameters
            logging.info("Extracting validated parameters")
            store_url = input_data.validated_data["store_url"]
            consumer_key = input_data.validated_data["consumer_key"]
            consumer_secret = input_data.validated_data["consumer_secret"]
            
            # get optional parameters
            optional_parameters = {}
            for param in self.get_parameter_schema():
                if param.name in input_data.validated_data:
                    optional_parameters[param.name] = input_data.validated_data[param.name]
            
            # Initialize WooCommerce client
            logging.info(f"Initializing WooCommerce client for store: {store_url}")
            wc_config = WooCommerceConfig(
                store_url=store_url,
                consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                auth_type=WooCommerceAuthType.BASIC
            )
            wc = WooCommerceClass(wc_config)

            # Get coupon
            coupons = wc.get_coupons(params=optional_parameters)

            # Format coupons
            formatted_coupons = []

            for coupon in coupons:
                formatted_coupon = {
                    "id": coupon.get("id"),
                    "code": coupon.get("code"),
                    "amount": coupon.get("amount"),
                    "date_created": coupon.get("date_created"),
                    "date_modified": coupon.get("date_modified"),
                    "discount_type": coupon.get("discount_type"),
                    "description": coupon.get("description"),
                    "date_expires": coupon.get("date_expires"),
                    "usage_count": coupon.get("usage_count"),
                    "individual_use": coupon.get("individual_use"),
                    "product_ids": coupon.get("product_ids"),
                    "excluded_product_ids": coupon.get("excluded_product_ids"),
                    "usage_limit": coupon.get("usage_limit"),
                    "usage_limit_per_user": coupon.get("usage_limit_per_user"),
                    "limit_usage_to_x_items": coupon.get("limit_usage_to_x_items"),
                    "free_shipping": coupon.get("free_shipping"),
                    "product_categories": coupon.get("product_categories"),
                    "exclude_product_categories": coupon.get("exclude_product_categories"),
                    "exclude_sale_items": coupon.get("exclude_sale_items"),
                    "minimum_amount": coupon.get("minimum_amount"),
                    "maximum_amount": coupon.get("maximum_amount"),
                    "email_restrictions": coupon.get("email_restrictions"),
                    "used_by": coupon.get("used_by")
                }
                formatted_coupons.append(formatted_coupon)

            # Extract coupon data
            output_data = {
                "coupons": formatted_coupons
            }
            
            # Return the filtered coupons
            return StandardOutput(
                output_data, 
                self.get_output_schema()
            )

        except Exception as e:
            error_msg = f"Error retrieving coupons: {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)


from pprint import pprint
pprint([p.to_json() for p in GetWooCommerceCoupons().get_parameter_schema()])
print('\n\n')
pprint([p.to_json() for p in GetWooCommerceCoupons().get_output_schema()])
