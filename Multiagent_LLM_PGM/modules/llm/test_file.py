
from gpt import GPT  # Adjust the import if needed

# Initialize the GPT class
gpt = GPT(key="dummy_key", model="gpt-3.5-turbo")
# test_prompt ={
#   "model": "gpt-3.5-turbo",
#   "messages": [
#     {
#       "role": "user",
#       "content": "this is system"
#     },
#     {
#       "role": "system",
#       "content": "Hello, how are you?"
#     }
#   ],
#   "temperature": 0.7,
#   "max_tokens": 256
# }


# Define a test prompt
# test_prompt = "I am at (x,y) = (12,10), you are at (x,y) = (0,0), what is the centroid between us? Give me (x,y) co-ordinates"
test_prompt ="How goes it?"
# Generate a response
try:
    response = gpt.generate_answer(test_prompt)
    print("Response:", response)
except Exception as e:
    print("Error during test:", e)
