from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback
import threading
import queue
import pickle
import os
from tqdm import tqdm

class Template(ABC):
    """
    A template class for designing and running experiments with multiple agents
    and rounds.

    This abstract class defines a template for designing experiments where 
    multiple agents interact in multiple rounds. Subclasses must implement 
    various methods to customize the behavior of the experiment, including 
    generating questions, managing agents, updating experiment records, and 
    performing post-processing.

    Attributes:
        _record (dict): A dictionary for recording experiment data.
        _n_agent (int): Number of agents participating in the experiment.
        _n_round (int): Number of rounds in the experiment.
        _n_experiment (int): Number of independent experiments to run.
        _lock (threading.Lock):
          A lock for ensuring thread safety during data updates.

    Subclasses should implement the following abstract methods:
        -  _generate_question
        - _generate_agents
        - _update_record
        - _round_postprocess
        - _exp_postprocess

    Public Methods:
        - run: Run the experiment using a thread pool for concurrency.
        - save_record: Save the experiment record to a file.

    To use this template, create a subclass that defines the specific behavior
    of the experiment.
    """
    def __init__(self, args):
        """
        Initialize the Template with provided arguments.

        Initializes instance variables for managing the experiment.
        """
        self._record = {}  # A dictionary for recording data
        self._n_agent = args.agents  # Number of agents
        self._n_round = args.rounds  # Number of rounds
        self._n_experiment = args.n_exp  # Number of experiments
        self._lock = threading.Lock()  # Lock for thread safety

    @abstractmethod
    def  _generate_question(self, agent, round, simulation_ind) -> str:
        """
        Generate a question for an agent in a specific round.

        Args:
            agent: An agent participating in the experiment.
            round: The current round of the experiment.

        Returns:
            str: The generated question.
        """
        pass

    @abstractmethod
    def _generate_agents(self, simulation_ind):
        """
        Generate a set of agents for a simulation.

        Args:
            simulation_ind: Index of the current simulation.

        Returns:
            list: A list of agent objects.
        """
        pass

    @abstractmethod
    def _update_record(self, record, agent_contexts, simulation_ind, agents):
        """
        Update the experiment record based on agent data.

        Args:
            record: The experiment record to be updated.
            agent_contexts: List of agent histories and data.
            simulation_ind: Index of the current simulation.
            agents: List of agents participating in the experiment.
        """
        pass

    @abstractmethod
    def _round_postprocess(self, simulation_ind, round, results, agents):
        """
        Perform post-processing for a round of the experiment.

        Args:
            simulation_ind: Index of the current simulation.
            round: The current round of the experiment.
            results: List of results from agents.
            agents: List of agents participating in the experiment.
        """
        pass

    @abstractmethod
    def _exp_postprocess(self):
        """
        Perform post-processing for the entire experiment.
        """
        pass

    def run(self):
        """
        Run the experiment using a thread pool for concurrency.
        """
        try:
            with ThreadPoolExecutor(max_workers=self._n_experiment) as executor:
                progress = tqdm(total=self._n_experiment * self._n_round, 
                                desc="Processing", dynamic_ncols=True)
                futures = {executor.submit(self._run_once, sim_ind, progress) 
                           for sim_ind in range(self._n_experiment)}

                for future in as_completed(futures):
                    if future.exception() is not None:
                        print("DEBUG2\n" ,future.exception())
                        print("A thread raised an exception: "
                              f"{future.exception()}")
                        traceback.print_exc() 
                progress.close()
                #Printing Average Score Here
            # self._summarize_metrics()
        except Exception as e:
            print(f"An exception occurred: {e}")
        finally:
            self._exp_postprocess()

    def _run_once(self, simulation_ind, progress):
        """
        Run a single simulation of the experiment.

        Args:
            simulation_ind: Index of the current simulation.
            progress: Progress bar for tracking the simulation's progress.
        """
        agents = self._generate_agents(simulation_ind)
        try:
            for round in range(self._n_round):
                results = queue.Queue()
                n_thread = len(agents) if round < 4 else 1
                with ThreadPoolExecutor(n_thread) as agent_executor:
                    futures = []
                    for agent_ind, agent in enumerate(agents):
                        question = self. _generate_question(agent, round, simulation_ind)
                        # print(f"Question: {question}")
                        futures.append(agent_executor
                                       .submit(agent.answer, question, 
                                               agent_ind, round, 
                                               simulation_ind))

                    for ind, future in enumerate(as_completed(futures)):
                        if future.exception() is not None:
                            print("A thread raised an exception: "
                                  f"{future.exception()}")
                        else:
                            idx, result = future.result()
                            results.put((idx, result))
                results = list(results.queue)
                results = sorted(results, key=lambda x: x[0])
                progress.update(1)
                self._round_postprocess(simulation_ind, round, results, agents)
                if round == self._n_round - 1:
                    print(f"[Simulation {simulation_ind}] Plotting final trajectories")
                    self._plot_agent_trajectories(agents, simulation_ind)
                    
            metric_path = os.path.join(self._output_file, "metric.txt")
            os.makedirs(os.path.dirname(metric_path), exist_ok=True)
            metric_file = open(metric_path, "a")  # append mode to avoid overwriting
            # === Write metric for this simulation ===
            metric_file.write(f"Simulation {simulation_ind}:\n")
            metric_file.write(str(self._metrics[simulation_ind]) + "\n\n")
            metric_file.close()  

        except Exception as e:
            print(f"error:{e}")
        finally:
            agent_contexts = [agent.get_history() for agent in agents]
            with self._lock:
                self._update_record(self._record, agent_contexts, 
                                   simulation_ind, agents)
            
            print(f"Final {self._metrics}")

    def save_record(self, output_dir: str):
        """
        Save the experiment record to a file.

        Args:
            output_dir: The directory where the record will be saved.

        Returns:
            Tuple: A tuple with a success indicator and the file path.
        """
        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            data_file = output_dir + '/data.p'

            # Save the record to a pickle file
            pickle.dump(self._record, open(data_file, "wb"))
            return True, data_file
        except Exception as e:
            print(f"An exception occurred while saving the file: {e}")
            print("Saving to the current directory instead.")
            # Backup in case of an exception
            pickle.dump(self._record, open("backup_output_file.p", "wb"))
            return False, ""