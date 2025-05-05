
from gpt import GPT  # Adjust the import if needed

gpt = GPT(key="dummy_key", model="gpt-3.5-turbo")

test_prompt ="How goes it?"
# Generate a response
try:
    response = gpt.generate_answer(test_prompt)
    print("Response:", response)
except Exception as e:
    print("Error during test:", e)
