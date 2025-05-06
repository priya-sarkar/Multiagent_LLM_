Code repo for the course project 'Improving reasoning in multi-agent LLMs' for the course 'Topics in AI' at Indian Institute of Science, Bangalore offered in spring semester, 2025.

Repository contains code to simulate a two player game to understand collaboration among multiple agents (realised via LLMs ) in context of a common task. 
We propose test metric to measure agent performance and suggest prompt variations (Chain of Thought prompting and PGM aware prompts) that induce collaboration among the agents.
# Implementation Details
1. Create a python environments with all libraries in requirements.txt installed, activate it.
2. Download a fine-tuned LLM 
3. In api_server.py, change the MODEL_PATH to where the LLM is cached
4. Open terminal, run python api_server.py, LLM is hosted on local api, running from port = 6570
You should get following message from flask ->

``` * Serving Flask app 'api_server'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:6570
 * Running on http://10.72.243.118:6570
```
5. In run_test.py, change the simulation parameters like n_rounds (duration) , n_experiments (number of parallel experiments)
6. Open new terminal, activate environment, run python new_test.py
