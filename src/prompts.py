def step_1(cleaned_html_content: str) -> str:
    return f"""
    TASK: Analyze the API documentation below and extract key operational details.
    
    INSTRUCTIONS:
    1. Identify all API endpoints and their HTTP methods (GET/POST/PUT/DELETE)
    2. Extract required parameters (path, query, body) with data types
    3. Find authentication method (API key/OAuth/Basic) and placement (header/query)
    4. Identify response schema (JSON structure with sample fields)
    5. Output JSON format:
    
    {{
      "api_name": "ServiceName",
      "base_url": "https://api.example.com",
      "authentication": {{
        "type": "api_key",
        "placement": "header",
        "param_name": "Authorization"
      }},
      "endpoints": [
        {{
          "operation": "createItem",
          "method": "POST",
          "path": "/items",
          "parameters": [
            {{
              "name": "item_name",
              "type": "string",
              "required": true,
              "location": "body"
            }}
          ],
          "response_schema": {{
            "id": "integer",
            "name": "string"
          }}
        }}
      ]
    }}
    DOCUMENTATION:
    {cleaned_html_content}
    """

def step_2(output_from_step1: str,types: str) -> str:
    prompt = f"""
    TASK: Generate a class-based CRUD function using an object-oriented approach.
    
    INSTRUCTIONS:
    1. **Class Definition**: Create a Python class inheriting from `BaseFunction`.
    2. **Schema Definition**:
       - Implement `get_parameter_schema()` using the refined `VALIDATED_PARAMS`.
       - Construct an `OutputParameter` hierarchy from `RESPONSE_SCHEMA`, ensuring all fields are included.
    3. **Method Implementation**:
       - Implement `process()` with:
         - Parameter extraction using `StandardInput`
         - API client initialization following the `WooCommerceClass` pattern
         - Error handling with try/except and logging
         - API response parsing, ensuring it aligns with `response_schema`
         - Generating a structured output using `OutputParameter`
    4. **Code Style Compliance**:
       - Follow the snake_case convention
       - Use precise type hints
       - Implement verbose logging for debugging
       - Utilize `WooCommerceConfig`-style authentication
       - Maintain `OutputParameter` structure with parent/child relationships
    
    ---
    
    ### **API SPECIFICATION**:
    {output_from_step1}
    
    ---
    
    ### **TYPES FROM PROVIDED PYTHON FILE**:
    {types}


    
    ### **REQUIRED OUTPUT**:
    - Provide only the Python class inside triple backticks (` ```python ... ``` `).
        """

    return prompt