import requests
import json


class GPT:
    """
    Initialize the GPT class for interacting with OpenAI's GPT model.
    GPT provides basic methods for interacting with the model and parsing its
    output.
    """

    def __init__(self, key: str, model: str = 'gpt-3.5-turbo-0613',
                 temperature: float = 0.2, keep_memory: bool = True):
        """
        Initialize the GPT class.

        Args:
            key (str): OpenAI API key.
            model (str): The model to use (default: gpt-3.5-turbo-0613).
            temperature (float): Temperature for text generation (default: 0.7).
            keep_memory (bool): Whether to retain memories (default: True).
        """
        self._model = model
        self._openai_key = key
        self._cost = 0
        self._memories = []
        self._keep_memory = keep_memory
        self._temperature = temperature
        self._history = []

    def get_memories(self):
        """
        Get the current memories.

        Returns:
            list: List of memories.
        """
        return self._memories

    def get_history(self):
        """
        Get the conversation history.

        Returns:
            list: List of conversation history.
        """
        return self._history

    def memories_update(self, role: str, content: str):
        """
        Update memories to set roles (system, user, assistant) and content,
        forming a complete memory.

        Args:
            role (str): Role (system, user, assistant).
            content (str): Content.

        Raises:
            ValueError: If an unrecognized role is provided or if roles are
            added in an incorrect sequence.
        """
        if role not in ["system", "user", "assistant"]:
            raise ValueError(f"Unrecognized role: {role}")

        if role == "system" and len(self._memories) > 0:
            raise ValueError('System role can only be added when memories are '
                             'empty')
        if (role == "user" and len(self._memories) > 0 and
            self._memories[-1]["role"] == "user"):
            raise ValueError('User role can only be added if the previous '
                             'round was a system or assistant role')
        if (role == "assistant" and len(self._memories) > 0 and
            self._memories[-1]["role"] != "user"):
            raise ValueError('Assistant role can only be added if the previous '
                             'round was a user role')
        self._memories.append({"role": role, "content": content})
        self._history.append({"role": role, "content": content})

    def generate_answer(self, input: str, try_times=0, **kwargs) -> str:
        """
        # Interact with the GPT model and generate an answer.

        # Args:
        #     input (str): Prompt or user input.
        #     try_times (int): Number of attempts (default is 0).
        #     kwargs: Additional parameters for the model.

        # Returns:
        #     str: Text-based output result.

        # Raises:
        #     ConnectionError: If there's an error in generating the answer.
        """
        if not self._keep_memory:
            self._memories = [self._memories[0]]

        if try_times == 0:
            self._memories.append({"role": "user", "content": input})
            self._history.append({"role": "user", "content": input})
        else:
            if self._memories[-1]["role"] == "assistant":
                self._memories = self._memories[:-1]

        try:
            
            url = "http://localhost:6570/completion"
            prompt = "\n".join([msg["content"] for msg in self._memories])
            data = {
                "model": self._model,
                "prompt": prompt,
                "temperature": 0.6,
                "n_predict": kwargs.get("max_tokens", 150)  # Ensure consistency
            }

            
            headers = {"Content-Type": "application/json"}
            r = requests.post(url, json=data, headers=headers)
            response_json = r.json()

            r = requests.post(url, json=data, headers=headers)
            response = r.json()
            content = response_json.get("content", "").strip()
            response = {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": content
                    }
                }]
            }

            content = response['choices'][0]['message']['content']
            self._memories.append({"role": "assistant", "content": content})
            self._history.append({"role": "assistant", "content": content})
            return content
        except Exception as e:
            
            raise ConnectionError(f"Error in generate_answer: {e}")
            print(_)
            

