import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from markdownify import markdownify as md
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.logging import RichHandler
from rich.syntax import Syntax
import logging

from scraper import clean_html
from parser import extract_code
from src.prompts import step_1, step_2

# Load environment variables
load_dotenv()

# Initialize OpenRouter API Key
key = os.getenv("OPENROUTER_API_KEY")

# Setup logging with RichHandler without color
console = Console(color_system=None)  # Disable color
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(console=console, rich_tracebacks=True, markup=False)]
)
logger = logging.getLogger("WooCommerceLogger")

# Progress Bar Setup
progress = Progress(
    SpinnerColumn(),
    TextColumn("{task.description}"),
    transient=True  # Disappear when done
)
task_id = progress.add_task("Processing API details...", total=5)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=key,
)

def interact_model(messages, model="google/gemini-2.0-flash-thinking-exp:free"):
    console.print("Sending request to OpenRouter AI Model...")

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": messages,
            }
        ],
        model=model,
    )

    console.print("Response received successfully!")
    return chat_completion.choices[0].message.content

with progress:
    progress.update(task_id, description="Reading WooCommerce API Docs...", advance=1)
    with open("test/wooCommerce/wooCommerce.html", "r") as f:
        cleaned_html = clean_html(f.read())
        api_docs = md(cleaned_html)

    progress.update(task_id, description="Reading Type Definitions...", advance=1)
    with open("test/all_types.py", "r") as f:
        type_defs = f.read()

    # Step 1: Extract API details
    progress.update(task_id, description="Generating API Details...", advance=1)
    prompt = step_1(api_docs)
    response = interact_model(prompt)

    console.print("Extracting API details...")
    try:
        api_details = json.loads(extract_code(response)[0])
    except (json.JSONDecodeError, IndexError) as e:
        console.print(f"Failed to parse API details: {str(e)}")
        exit(1)

    # Log API details as JSON (formatted)
    console.print("Extracted API Details:")
    console.print(json.dumps(api_details, indent=4), highlight=False)

    endpoints_list = api_details.get("endpoints", [])
    if not endpoints_list:
        console.print("No endpoints found in API details.")
        exit(1)

    api_template = api_details.copy()

    # Step 2: Generate CRUD functions
    for i, endpoint in enumerate(endpoints_list, start=1):
        console.print(f"Processing Endpoint {i}/{len(endpoints_list)}: {endpoint.get('operation', 'Unknown')}")
        api_template["endpoints"] = endpoint

        progress.update(task_id, description=f"Generating CRUD function for {endpoint.get('operation', 'Unknown')}...", advance=1)
        prompt = step_2(api_template, type_defs)

        # Call LLM for Python code generation
        python_response = interact_model(prompt)

        # Extract Python code from response
        extracted_python_code = extract_code(python_response)[0]

        # Log Python output in a readable format
        console.print(f"Generated Code for {endpoint['operation']}:")
        console.print(Syntax(extracted_python_code, "python", theme="monokai", line_numbers=True))

    progress.update(task_id, completed=5)
    console.print("API Processing Complete!")

# Optional: Save Output
# with open("src/test/out_may.py", "w") as f:
#     f.write(code)
