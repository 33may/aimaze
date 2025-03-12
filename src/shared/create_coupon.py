from typing import List
import logging
from datetime import datetime
from shared.FunctionClass import BaseFunction
from shared.ParameterClass import Parameter, ParameterType
from shared.OutputParameterClass import OutputParameter, OutputParameterType
from shared.InputClass import StandardInput
from shared.OutputClass import StandardOutput
from shared.ValidationClass import ValidationSeverity, CustomValidationType
from functions_classes.WooCommerceClass import WooCommerceClass, WooCommerceConfig, WooCommerceAuthType

class CreateWooCommerceCoupon(BaseFunction):
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
                name="code",
                param_type=ParameterType.STRING,
                required=True,
                validation_rules={
                    CustomValidationType.MIN_LENGTH.value: 1,
                    CustomValidationType.MAX_LENGTH.value: 50,
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="amount",
                param_type=ParameterType.STRING,
                required=True,
                validation_rules={
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="discount_type",
                param_type=ParameterType.SELECT,
                required=True,
                validation_rules={
                    CustomValidationType.ALLOWED_VALUES.value: [
                        "percent", "fixed_cart", "fixed_product"
                    ],
                    "severity": ValidationSeverity.ERROR
                }
            ),
            Parameter(
                name="description",
                param_type=ParameterType.STRING,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="date_expires",
                param_type=ParameterType.STRING,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="individual_use",
                param_type=ParameterType.BOOLEAN,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="product_ids",
                param_type=ParameterType.ARRAY,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="excluded_product_ids",
                param_type=ParameterType.ARRAY,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="usage_limit",
                param_type=ParameterType.INTEGER,
                required=False,
                validation_rules={
                    CustomValidationType.MIN_VALUE.value: 0,
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="usage_limit_per_user",
                param_type=ParameterType.INTEGER,
                required=False,
                validation_rules={
                    CustomValidationType.MIN_VALUE.value: 0,
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="limit_usage_to_x_items",
                param_type=ParameterType.INTEGER,
                required=False,
                validation_rules={
                    CustomValidationType.MIN_VALUE.value: 0,
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="free_shipping",
                param_type=ParameterType.BOOLEAN,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="product_categories",
                param_type=ParameterType.ARRAY,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="excluded_product_categories",
                param_type=ParameterType.ARRAY,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="exclude_sale_items",
                param_type=ParameterType.BOOLEAN,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="minimum_amount",
                param_type=ParameterType.STRING,
                required=False,
                validation_rules={
                    CustomValidationType.MIN_VALUE.value: 0,
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="maximum_amount",
                param_type=ParameterType.STRING,
                required=False,
                validation_rules={
                    CustomValidationType.MIN_VALUE.value: 0,
                    "severity": ValidationSeverity.WARNING
                }
            ),
            Parameter(
                name="email_restrictions",
                param_type=ParameterType.ARRAY,
                required=False,
                validation_rules={
                    "severity": ValidationSeverity.WARNING
                }
            )
        ]
    
    def get_output_schema(self) -> List[OutputParameter]:
        return [
            OutputParameter(
                key="id",
                name="Coupon ID",
                param_type=OutputParameterType.INTEGER,
                is_array=False,
                parent=None,
                default_value=None
            )
        ]

    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            # Get required parameters
            store_url = input_data.validated_data["store_url"]
            consumer_key = input_data.validated_data["consumer_key"]
            consumer_secret = input_data.validated_data["consumer_secret"]
            code = input_data.validated_data["code"]
            amount = input_data.validated_data["amount"]
            discount_type = input_data.validated_data["discount_type"]

            # Get optional parameters
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

            coupon_data = {
                "code": code,
                "amount": amount,
                "discount_type": discount_type
            }

            for key, value in optional_parameters.items():
                coupon_data[key] = value

            output = wc.create_coupon(coupon_data)

            output_data = {
                "id": output["id"]
            }
            
            return StandardOutput(output_data, self.get_output_schema())

        except Exception as e:
            error_msg = f"Error creating coupon: {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)