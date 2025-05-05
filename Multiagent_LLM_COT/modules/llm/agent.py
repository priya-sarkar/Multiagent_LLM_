import re
from .gpt import GPT
from ..prompt.summarize import summarizer_role
from ..prompt.form import summarizer_output_form

class Agent(GPT):

    def __init__(self, position, other_position, key: str, name=None, 
                 model: str = 'gpt-3.5-turbo-0613', temperature: float = 0.7):
        super().__init__(key=key, model=model, temperature=temperature)
        self._name = name
        self._position = position  # Current position of the agent
        self._other_position = other_position  # Positions of other agents
        self._trajectory = [self.position]  # Record the agent's movement trajectory
        self._summarizer = GPT(key=key, model="gpt-3.5-turbo-0613", 
                               keep_memory=False)
        self._summarize_result = ""
        self._summarizer_descriptions = summarizer_output_form
        self._summarizer.memories_update(role='system', content=summarizer_role)
        self._bomb_diffused = [] 
    @property
    def name(self):
        return self._name

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value

    @property
    def other_position(self):
        return self._other_position

    @other_position.setter
    def other_position(self, value):
        self._other_position = value

    @property
    def summarize_result(self):
        return self._summarize_result
    
    # @property
    # def bomb_locations(self):
    #     return self._bomb_locations

    # @bomb_locations.setter
    # def bomb_locations(self, value):
    #     self._bomb_locations = value

    def answer(self, input, idx, round, simulation_ind, try_times=0) -> tuple:
        # """
        # Generate an answer using the GPT model.

        # Args:
        #     input (str): Input text or prompt.
        #     idx: Index.
        #     round: Round.
        #     simulation_ind: Simulation index.
        #     try_times (int): Number of times the answer generation is attempted.

        # Returns:
        #     tuple: Index and the updated position of the agent.
        # """
        try:
            # print("Input in agent:", input ,try_times)
            # print("***********in agent GPT ip:", input)
            answer = self.generate_answer(input=input, try_times=try_times)
            # print("***********in agent GPT Response:", answer)
            self.position = self.parse_output(answer)
            return idx, self.position
        except Exception as e:
            # print("Input:", input ,try_times)
            try_times += 1
            if try_times < 4:
                print(f"An error occurred when agent {self._name} tried to "
                      f"generate answers: {e},try_times: {try_times + 1}/4.")
                return self.answer(input=input, idx=idx, 
                                   round=round, simulation_ind=simulation_ind, 
                                   try_times=try_times)
            else:
                print("After three attempts, the error still remains "
                      f"unresolved, the input is:\n'{input}'\n.")

    def summarize(self, agent_answers):
        """
        Generate a summary of agent answers.

        Args:
            agent_answers (list): List of agent answers.
        """
        if len(agent_answers) == 0:
            self._summarize_result = ""
        else:
            self._summarize_result = self._summarizer.generate_answer(
                self._summarizer_descriptions.format(agent_answers))

    def parse_output(self, output):
        # matches = re.findall(r'[-+]?\d*\.\d+|\d+', output)
        # if matches:
        #     x = float(matches[-1])
        #     self._trajectory.append(x)
        #     return x
        # else:
        #     raise ValueError(f"output: \n{output}\n can not be parsed")
        
        """
        Parse the model output to extract next position (x, y) and bomb diffused.
        Updates internal state accordingly.
        """
        # Match Position [x, y]
        pos_match = re.search(r'Position:\s*(\d+)', output)
        # pos_match = re.search(r'Position:\s*\[(\d+)\]', output)
        # Match Bombs Diffused [b]
        bomb_match = re.search(r'Defused:\s*(\d+)', output)
        bomb_list = [0,100]
        
        if pos_match: 
            # Update agent's position
            x = float(pos_match.group(1))
            self._position = x
            self._trajectory.append(x)
            if bomb_match:
                bomb = int(bomb_match.group(1))
                # print(f"From agent{self._name} parser -bomb_match - {bomb}")
                if bomb in bomb_list:
                    self._bomb_diffused.append(bomb)
                    # print(f"From agent{self._name} parser - {self._bomb_diffused}")
            else: 
                bomb=None
            # print(f"Agent No {self._name}: trajectory {self._trajectory}")
            return x
        else:
            raise ValueError(f"\nOutput parsing failed:{output}\n")
