from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os

os.environ["CUDA_VISIBLE_DEVICES"] = "1"

app = Flask(__name__)
MODEL_PATH = "/home/alvin/.cache/huggingface/hub/models--mistralai--Mistral-7B-Instruct-v0.3/snapshots/e0bc86c23ce5aae1db576c8cca6f06f1f73af2db"
# MODEL_PATH = "/home/alvin/.cache/huggingface/hub/models--Qwen--Qwen3-8B/snapshots/2069b3fae1114555f3c020c81410e51fa0f656f2"
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)

# Add special tokens
# special_tokens = {"additional_special_tokens": ["<|im_start|>", "<|im_end|>"]}
# tokenizer.add_special_tokens(special_tokens)

# Load model
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, torch_dtype=torch.float16).cuda()
# model = AutoModelForCausalLM.from_pretrained(
#     MODEL_PATH,
#     torch_dtype=torch.float16,
#     device_map="auto"
# )
# model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, device_map="auto", torch_dtype=torch.float16)
print("[DEBUG] Checking device allocations...")
for name, param in model.named_parameters():
    print(f"{name}: {param.device}")
    break  # print just one for sanity





# Resize model embeddings to account for added special tokens
model.resize_token_embeddings(len(tokenizer))
_ = model.generate(**tokenizer("warmup", return_tensors="pt").to(model.device), max_new_tokens=1)


@app.route('/completion', methods=['POST'])
def generate_text():
    data = request.json
    prompt = data.get("prompt", "")
    max_tokens = data.get("n_predict", 128)
    temperature = data.get("temperature", 0.2)
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    output_ids = model.generate(**inputs, max_new_tokens=max_tokens, temperature=temperature, do_sample = True)[0]

    # Extract only the newly generated tokens (excluding the input prompt)
    generated_tokens = output_ids[len(inputs["input_ids"][0]):]  
    response_text = tokenizer.decode(generated_tokens, skip_special_tokens=True)

    return jsonify({"content": response_text.strip()})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=6570,debug=False, use_reloader=False)

