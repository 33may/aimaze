import anthropic
import yaml
import tiktoken



# anthropic_client = anthropic.Anthropic()

openai_tokenizer = tiktoken.get_encoding("o200k_base")


def parse_yaml(yaml_file_path):
    with open(yaml_file_path, 'r') as yaml_file:
        try:
            yaml_data = yaml.safe_load(yaml_file)
        except yaml.YAMLError as exc:
            print(f"Error parsing YAML file: {exc}")
            return

    return yaml_data


def py_to_yml(val):
    return yaml.dump(val, default_flow_style=False)

yaml_file_path = 'asana_oas.yaml'
data = parse_yaml(yaml_file_path)

# print(data)

endpoints = data['paths']

total_endpoints = 0
openai_token_counts = []
# anthropic_token_counts = []

for val in endpoints.values():
    total_endpoints += len(val.keys()) - 1
    yaml_endpoint = py_to_yml(val)

    openai_tokens = len(openai_tokenizer.encode(yaml_endpoint))
    openai_token_counts.append(openai_tokens)

    # anthropic_tokens = anthropic_client.count_tokens(yaml_endpoint)
    # anthropic_token_counts.append(anthropic_tokens)

def calculate_stats(token_list):
    if not token_list:
        return 0, 0, 0
    return sum(token_list) / len(token_list), min(token_list), max(token_list)

avg_openai, min_openai, max_openai = calculate_stats(openai_token_counts)
# avg_anthropic, min_anthropic, max_anthropic = calculate_stats(anthropic_token_counts)

print(f"Total endpoints: {total_endpoints}")
print(f"OpenAI Tokens - Avg: {avg_openai:.2f}, Min: {min_openai}, Max: {max_openai}")
# print(f"Anthropic Tokens - Avg: {avg_anthropic:.2f}, Min: {min_anthropic}, Max: {max_anthropic}")

