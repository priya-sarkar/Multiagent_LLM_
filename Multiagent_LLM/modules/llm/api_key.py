import openai
import math

# Set API base manually
openai.api_base = "http://localhost:6567"  # Change if needed

# Check if using a local LLM
use_local_llm = "localhost" in openai.api_base

if use_local_llm:
    api_keys = {0: "local_dummy_key"}  # Dummy key for compatibility
else:
    api_keys_all = {}  # No YAML, so set empty
    user_id = 2
    user_count = 3

    keys_per_user = math.ceil(len(api_keys_all) / user_count) if api_keys_all else 1
    start = keys_per_user * user_id
    end = min(keys_per_user * (user_id + 1), len(api_keys_all))

    print(f"user {user_id}/{user_count}, api_key index start: {start}, end: {end}")

    api_keys = {i - start: v 
                for i, (k, v) in enumerate(api_keys_all.items()) 
                if start <= i < end}

if __name__ == '__main__':
    print(api_keys)

