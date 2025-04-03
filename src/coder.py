from markdownify import markdownify as md
from openai import OpenAI

from src.scraper.scraper import get_content

SCHEMA_EXTRACTION_PROMPT = """
The markdown section below is part of an API documentation, containing endpoints with their input/output schema's. Convert every endpoint as listed in the documentation into json schema's as instructed below.

Here is an example:
```markdown (example)
    List all coupons
    ----------------
    This API helps you to list all the coupons that have been created.
    ### HTTP request
    *GET*
    ###### /wp\-json/wc/v3/coupons
    ```
    curl https://example.com/wp-json/wc/v3/coupons \
     -u consumer_key:consumer_secret
    ```
    ```
    WooCommerce.get("coupons")
     .then((response) => {{
     console.log(response.data);
     }})
     .catch((error) => {{
     console.log(error.response.data);
     }});
    ```
    ```
    <?php print_r($woocommerce->get('coupons')); ?>
    ```
    ```
    print(wcapi.get("coupons").json())
    ```
    ```
    woocommerce.get("coupons").parsed_response
    ```
    > JSON response example:
    ```
    [
     {{
     "id": 720,
     "code": "free shipping",
     "amount": "0.00",
     "date_created": "2017-03-21T15:25:02",
     "date_created_gmt": "2017-03-21T18:25:02",
     "date_modified": "2017-03-21T15:25:02",
     "date_modified_gmt": "2017-03-21T18:25:02",
     "discount_type": "fixed_cart",
     "description": "",
     "date_expires": null,
     "date_expires_gmt": null,
     "usage_count": 0,
     "individual_use": true,
     "product_ids": [],
     "excluded_product_ids": [],
     "usage_limit": null,
     "usage_limit_per_user": null,
     "limit_usage_to_x_items": null,
     "free_shipping": true,
     "product_categories": [],
     "excluded_product_categories": [],
     "exclude_sale_items": false,
     "minimum_amount": "0.00",
     "maximum_amount": "0.00",
     "email_restrictions": [],
     "used_by": [],
     "meta_data": [],
     "_links": {{
     "self": [
     {{
     "href": "https://example.com/wp-json/wc/v3/coupons/720"
     }}
     ],
     "collection": [
     {{
     "href": "https://example.com/wp-json/wc/v3/coupons"
     }}
     ]
     }}
     }},
     {{
     "id": 719,
     "code": "10off",
     "amount": "10.00",
     "date_created": "2017-03-21T15:23:00",
     "date_created_gmt": "2017-03-21T18:23:00",
     "date_modified": "2017-03-21T15:23:00",
     "date_modified_gmt": "2017-03-21T18:23:00",
     "discount_type": "percent",
     "description": "",
     "date_expires": null,
     "date_expires_gmt": null,
     "usage_count": 0,
     "individual_use": true,
     "product_ids": [],
     "excluded_product_ids": [],
     "usage_limit": null,
     "usage_limit_per_user": null,
     "limit_usage_to_x_items": null,
     "free_shipping": false,
     "product_categories": [],
     "excluded_product_categories": [],
     "exclude_sale_items": true,
     "minimum_amount": "100.00",
     "maximum_amount": "0.00",
     "email_restrictions": [],
     "used_by": [],
     "meta_data": [],
     "_links": {{
     "self": [
     {{
     "href": "https://example.com/wp-json/wc/v3/coupons/719"
     }}
     ],
     "collection": [
     {{
     "href": "https://example.com/wp-json/wc/v3/coupons"
     }}
     ]
     }}
     }}
    ]
    ```
    #### Available parameters
    | Parameter | Type | Description |
    | --- | --- | --- |
    | `context` | string | Scope under which the request is made; determines fields present in response. Options: `view` and `edit`. Default is `view`. |
    | `page` | integer | Current page of the collection. Default is `1`. |
    | `per_page` | integer | Maximum number of items to be returned in result set. Default is `10`. |
    | `search` | string | Limit results to those matching a string. |
    | `after` | string | Limit response to resources published after a given ISO8601 compliant date. |
    | `before` | string | Limit response to resources published before a given ISO8601 compliant date. |
    | `modified_after` | string | Limit response to resources modified after a given ISO8601 compliant date. |
    | `modified_before` | string | Limit response to resources modified after a given ISO8601 compliant date. |
    | `dates_are_gmt` | boolean | Whether to consider GMT post dates when limiting response by published or modified date. |
    | `exclude` | array | Ensure result set excludes specific IDs. |
    | `include` | array | Limit result set to specific ids. |
    | `offset` | integer | Offset the result set by a specific number of items. |
    | `order` | string | Order sort attribute ascending or descending. Options: `asc` and `desc`. Default is `desc`. |
    | `orderby` | string | Sort collection by object attribute. Options: `date`, `modified`, `id`, `include`, `title` and `slug`. Default is `date`. |
    | `code` | string | Limit result set to resources with a specific code. |
```


```json (example)
[{{"List all coupons":
    {{"input": [{{'name': 'store_url', 'required': True, 'type': 'url' }},
     {{'name': 'consumer_key', 'required': True, 'type': 'string' }},
     {{'name': 'consumer_secret', 'required': True, 'type': 'string' }},
     {{'name': 'page', 'required': False, 'type': 'integer' }},
     {{'name': 'per_page', 'required': False, 'type': 'integer' }},
     {{'name': 'search', 'required': False, 'type': 'string' }},
     {{'name': 'after', 'required': False, 'type': 'string' }},
     {{'name': 'before', 'required': False, 'type': 'string' }},
     {{'name': 'modified_after', 'required': False, 'type': 'string' }},
     {{'name': 'modified_before', 'required': False, 'type': 'string' }},
     {{'name': 'exclude', 'required': False, 'type': 'array' }},
     {{'name': 'include', 'required': False, 'type': 'array' }},
     {{'name': 'offset', 'required': False, 'type': 'integer' }},
     {{'name': 'order', 'required': False, 'type': 'select' }},
     {{'name': 'orderby', 'required': False, 'type': 'select'}}]

      "output": [{{'is_array': True, 'name': 'Coupons', 'type': 'object' }},
     {{'is_array': False, 'name': 'ID', 'type': 'integer' }},
     {{'is_array': False, 'name': 'Code', 'type': 'string' }},
     {{'is_array': False, 'name': 'Amount', 'type': 'string' }},
     {{'is_array': False, 'name': 'Date Created', 'type': 'string' }},
     {{'is_array': False, 'name': 'Date Modified', 'type': 'string' }},
     {{'is_array': False, 'name': 'Discount Type', 'type': 'string' }},
     {{'is_array': False, 'name': 'Description', 'type': 'string' }},
     {{'is_array': False, 'name': 'Date Expires', 'type': 'string' }},
     {{'is_array': False, 'name': 'Usage Count', 'type': 'integer' }},
     {{'is_array': False, 'name': 'Individual Use', 'type': 'boolean' }},
     {{'is_array': True, 'name': 'Product IDs', 'type': 'integer' }},
     {{'is_array': True, 'name': 'Excluded Product IDs', 'type': 'integer' }},
     {{'is_array': False, 'name': 'Usage Limit', 'type': 'integer' }},
     {{'name': 'Usage Limit Per User', 'type': 'integer' }},
     {{'name': 'Limit Usage to X Items', 'type': 'integer' }},
     {{'is_array': False, 'name': 'Free Shipping', 'type': 'boolean' }},
     {{'is_array': True, 'name': 'Product Categories', 'type': 'integer' }},
     {{'is_array': True, 'name': 'Exclude Product Categories', 'type': 'integer' }},
     {{'name': 'Exclude Sale Items', 'type': 'boolean' }},
     {{'name': 'Minimum Amount', 'type': 'string' }},
     {{'name': 'Maximum Amount', 'type': 'string' }},
     {{'is_array': True, 'name': 'Email Restrictions', 'type': 'string' }},
     {{'is_array': True, 'name': 'Used By', 'type': 'string'}}]
    }}]
```


Here is the page you need to parse:
```markdown
{docs}
```

Make sure to return the json object only (without the ```json ... ``` padding).

"""




client = OpenAI()

CODING_PROMPT = """

Write me a Python function that wraps the API call(s) in the json schema. Make the function documentation minimal. Make sure to implement the wrapper as a BaseFunction using the classes and types in the attached python file (import these, don't copy them into your solution). For ease of access for you, these have all been merged into one file. But the code should call each function from the respective file (as listed in the comment of all_types.py) from shared.whatever, as an example: 'from shared.FunctionClass import BaseFunction'


Types (by file):
```python
{types}
````


The API schema:
```json
{docs}
```


Respond only with your script wrapped in ```python ...```, and implement the tiniest test call I can run to verify the integrity off your script. Your script will be automatically executed as part of a testing procedure, so make sure the tests run automatically at the end of your script."""


with open("src/test/all_types.py", "r") as f:
    types = f.read()

URL = "https://jsonplaceholder.typicode.com/guide/"
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            # "content": CODING_PROMPT.format(types=types, docs=md(get_content(URL))),
            "content": SCHEMA_EXTRACTION_PROMPT.format(docs=md(get_content(URL))),
        }
    ],
    model="gpt-4o",
)

response = chat_completion.choices[0].message.content

print(response)

# code = extract_code(response)
# with open("src/test/out.py", "w") as f:
#     f.write(code)
# exec(code)
