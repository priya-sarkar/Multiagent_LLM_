import numpy as np
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor, as_completed
from .template import Template
from ..llm.agent import Agent, GPT
from ..llm.api_key import api_keys
from ..llm.role import names
from ..prompt.scenario import agent_role, game_description, round_description
from ..prompt.form import agent_output_form
from ..prompt.personality import stubborn, suggestible
from ..visual.gen_html import gen_html
from ..visual.plot import plot_result

class ScalarDebate(Template):
    """
    A class representing a simulation of scalar debate between multiple agents.

    This class extends the Template class and provides functionality to set up 
    and run a simulation where multiple agents engage in debates, taking into 
    account their positions, personalities, and knowledge connectivity.

    Args:
        args: Command-line arguments and configuration.
        connectivity_matrix: Matrix defining agent knowledge connectivity.

    Raises:
        ValueError: If arguments are invalid or insufficient.
    """
    def __init__(self, args, connectivity_matrix):
        super().__init__(args)
        self._n_agents = args.agents
        self._init_input =  game_description +"\n" + agent_output_form
        self._round_description = round_description
        self._positions = [[]] * args.n_exp
        self._output_file = args.out_file
        self._n_suggestible = args.n_suggestible
        self._n_stubborn = args.n_stubborn
        self._bomb_locations = [[0, 100] for _ in range(args.n_exp)]
        self._metrics = [{} for _ in range(self._n_experiment)]

        np.random.seed(0)

        # Define the connectivity matrix for agent knowledge
        # m(i, j) = 1 means agent i knows the position of agent j
        self._m = connectivity_matrix

        # Safety checks
        # if args.n_stubborn + args.n_suggestible > self._n_agents:
        #     raise ValueError("stubborn + suggestible agents exceed "
        #                      f"total agents: {self._n_agents}")
        # if len(api_keys) < self._n_agents * args.n_exp:
        #     raise ValueError("api_keys are not enough for "
        #                      f"{self._n_agents} agents")
        # if self._m.shape[0] != self._m.shape[1]:
        #     raise ValueError("connectivity_matrix is not a square matrix, "
        #                      f"shape: {self._m.shape}")
        # if self._m.shape[0] != self._n_agents:
        #     raise ValueError("connectivity_matrix size doesn't match the "
        #                      f"number of agents: {self._m.shape}")

    def _generate_agents(self, simulation_ind):
        """
        Generate agent instances based on provided parameters.

        Args:
            simulation_ind: Index of the current simulation.

        Returns:
            List of generated agents.
        """
        agents = []
        position = np.random.randint(0, 100, size=self._n_agents)
        for idx in range(self._n_agents):
            position_others = position[self._m[idx, :]]

            # Create agent instances
            agent = Agent(position=position[idx],
                          other_position=position_others,
                          key="dummy key",
                          model="gpt-3.5-turbo-0613",
                          name=names[idx])

            # Add personality, neutral by default
            personality = ""
            if idx < self._n_stubborn:
                personality = stubborn
            elif self._n_stubborn <= idx < (
                self._n_stubborn + self._n_suggestible):
                personality = suggestible

            agent.memories_update(role='system',
                                  content=agent_role + personality)
            agents.append(agent)

        self._positions[simulation_ind] = position
        return agents

    # def  _generate_question(self, agent, round) -> str:
    #     """
    #     Generate a question for an agent in a given round.

    #     Args:
    #         agent: The agent for which to generate the question.
    #         round: The current round number.

    #     Returns:
    #         A formatted question for the agent.
    #     """
    #     if round == 0:
    #         input = self._init_input.format(agent.position, 
    #                                         agent.other_position)
    #     else:
    #         input = self._round_description.format(agent.position, 
    #                                                agent.other_position)
    #     return input

    def _generate_question(self, agent, round, simulation_ind):
        
        bombs = self._bomb_locations[simulation_ind]
        if len(bombs) == 0:
            return f"All bombs have been diffused. You are at {agent.position}, and the other agent is at {agent.other_position}. Please choose your next position."

        
        bombs_str = ', '.join(map(str, bombs))  # 🔥 Convert [0, 100] -> "0, 100"

        other_pos_str = ', '.join(map(str, agent.other_position))
        if round == 0:
            input = self._init_input.format(bombs_str, agent.position, agent.other_position)
            # print(f"Question {input}")
        else:
            input = self._round_description.format(bombs_str, agent.position, agent.other_position)
        return input

    def _exp_postprocess(self):
        """
        Perform post-processing after the experiment, including saving 
        records and generating plots.
        """
        is_success, filename = self.save_record(self._output_file)
        if is_success:
            # Call functions to plot and generate HTML
            plot_result(filename, self._output_file)
            gen_html(filename, self._output_file)

    def _round_postprocess(self, simulation_ind, round, results, agents):
        """
        Perform post-processing for each round of the simulation.

        Args:
            simulation_ind: Index of the current simulation.
            round: The current round number.
            results: Results from the round.
            agents: List of agents.
        """
        
        # --- Metric Tracking Logic in ScalarDebate._round_postprocess ---
        # Add this in the beginning of _round_postprocess (if round == 0)
        # if round == 0:
        #     self._metrics[simulation_ind]['correct_moves'] = [0] * len(agents)
        #     self._metrics[simulation_ind]['first_defuse'] = None
        #     self._metrics[simulation_ind]['second_defuse'] = None
        #     self._metrics[simulation_ind]['fluctuation'] = [0] * len(agents)

        # # Add this after updating agent positions
        # bombs_before = len(self._bomb_locations[simulation_ind])
        old_bomb_list=self._bomb_locations[simulation_ind]
        bombs = self._bomb_locations[simulation_ind]
        # # Detect defuse events
        # if bombs_before == 2 and len(bombs) == 1 and self._metrics[simulation_ind]['first_defuse'] is None:
        #     self._metrics[simulation_ind]['first_defuse'] = round
        # if bombs_before == 1 and len(bombs) == 0 and self._metrics[simulation_ind]['second_defuse'] is None:
        #     self._metrics[simulation_ind]['second_defuse'] = round
        # if bombs:
        #     for idx, agent in enumerate(agents):
        #         traj = agent._trajectory
        #         if len(traj) < 2:
        #             continue  # No previous movement
        #         prev_pos = traj[-2]
        #         new_pos = traj[-1]

        #         # Find closest bomb to previous position
        #         closest_bomb = min(bombs, key=lambda b: abs(b - prev_pos))
        #         old_dist = abs(prev_pos - closest_bomb)
        #         new_dist = abs(new_pos - closest_bomb)

        #         if new_dist < old_dist:
        #             self._metrics[simulation_ind]['correct_moves'][idx] += 1
        # print(f"Round {round} , {self._metrics[simulation_ind]['correct_moves'] } out of {self._metrics[simulation_ind]['second_defuse']}")
            

        for idx, agent in enumerate(agents):
            res_filtered = np.array(results)[self._m[idx, :]]
            # res_filtered = [results[i] for i in range(len(results)) if self._m[idx, i]]

            other_position = [x for _, x in res_filtered]
            agent.other_position = other_position
        bombs_still_active = self._bomb_locations[simulation_ind]
        bombs_diffused_this_round = []
        for agent in agents:
            if agent._bomb_diffused:  # If agent claimed a bomb
                # bombs_diffused_this_round.extend(agent._bomb_diffused[-1])  # take latest diffused
                latest_bomb = agent._bomb_diffused[-1:] if agent._bomb_diffused else []
                bombs_diffused_this_round.extend(latest_bomb)

        bombs_still_active = [b for b in bombs_still_active if b not in bombs_diffused_this_round]
        print(f"[Simulation {simulation_ind}] After round {round}, active bombs: {self._bomb_locations[simulation_ind]}")

        # Update master bomb list
        self._bomb_locations[simulation_ind] = bombs_still_active
        self._update_metrics(simulation_ind, round, agents, old_bomb_list)
        

    def _update_record(self, record, agent_contexts, simulation_ind, agents):
        """
        Update the record with agent contexts for a given simulation.

        Args:
            record: The record to be updated.
            agent_contexts: Contexts of the agents.
            simulation_ind: Index of the current simulation.
            agents: List of agents.
        """
        record[tuple(self._positions[simulation_ind])] = agent_contexts
    def _plot_agent_trajectories(self, agents, simulation_ind):
        """
        Plot the 1D movement trajectories of agents over rounds.
        """
        plt.figure(figsize=(10, 4))

        for idx, agent in enumerate(agents):
            trajectory = agent._trajectory  # list of scalar positions
            plt.plot(trajectory, label=f"Agent {idx}", marker='o')

        plt.title(f"Agent 1D Trajectories - Simulation {simulation_ind}")
        plt.xlabel("Round")
        plt.ylabel("Position")
        plt.ylim(0, 100)
        plt.xlim(0, 10)
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        output_dir = os.path.join(self._output_file, "plots")
        os.makedirs(output_dir, exist_ok=True)

        filename = os.path.join(output_dir, f"trajectory_sim{simulation_ind}.png")
        plt.savefig(filename, bbox_inches='tight')
        plt.close()  # ✅ Don't use plt.show() in background thread
        print(f"[Saved] Plot saved to: {filename}")
    # --- New function to compute game metrics ---
    def _update_metrics(self, simulation_ind, round, agents, old_bomb_list):
        if round == 0:
            
            self._metrics[simulation_ind]['correct_moves'] = [0] * len(agents)
            self._metrics[simulation_ind]['rounds_to_clear_bombs'] = None
            self._metrics[simulation_ind]['first_defuse'] = None
            self._metrics[simulation_ind]['second_defuse'] = None
            self._metrics[simulation_ind]['fluctuation'] = [0] * len(agents)
            self._metrics[simulation_ind]['total_moves'] = 0
            

        bombs_before = len(old_bomb_list)
        bombs = self._bomb_locations[simulation_ind]
        
        if bombs_before == 2 and len(bombs) == 1 and self._metrics[simulation_ind]['first_defuse'] is None:
            self._metrics[simulation_ind]['first_defuse'] = round
        if bombs_before == 1 and len(bombs) == 0 and self._metrics[simulation_ind]['second_defuse'] is None:
            self._metrics[simulation_ind]['second_defuse'] = round
        if bombs:
            for idx, agent in enumerate(agents):
                
                traj = agent._trajectory
                if len(traj) < 2:
                    continue
                prev_pos = traj[-2]
                new_pos = traj[-1]
                
                if(round>1):
                    if (prev_pos < 50 and new_pos > 50) or (prev_pos > 50 and new_pos < 50):
                        self._metrics[simulation_ind]['fluctuation'][idx] += 1

                closest_bomb = min(bombs, key=lambda b: abs(b - prev_pos))
                old_dist = abs(prev_pos - closest_bomb)
                new_dist = abs(new_pos - closest_bomb)
                
                if new_dist < old_dist:
                    self._metrics[simulation_ind]['correct_moves'][idx] += 1
        if not bombs and self._metrics[simulation_ind]['rounds_to_clear_bombs'] is None:
            self._metrics[simulation_ind]['rounds_to_clear_bombs'] = round
        self._metrics[simulation_ind]['total_moves'] += 2 
        print(f"[Simulation {simulation_ind}]{self._metrics}")

    def _summarize_metrics(self):
        n_agents = len(self._metrics[0]['correct_moves'])
        total_sims = len(self._metrics)

        avg_metrics = {
            'correct_moves': [0] * n_agents,
            'fluctuation': [0] * n_agents,
            'rounds_to_clear_bombs': [],
            'first_defuse': [],
            'second_defuse': []
        }

        for metric in self._metrics:
            for i in range(n_agents):
                avg_metrics['correct_moves'][i] += metric['correct_moves'][i]
                avg_metrics['fluctuation'][i] += metric['fluctuation'][i]
            for key in ['rounds_to_clear_bombs', 'first_defuse', 'second_defuse']:
                val = metric[key]
                if val is not None:
                    avg_metrics[key].append(val)

        for key in ['correct_moves', 'fluctuation']:
            avg_metrics[key] = [round(x / total_sims, 2) for x in avg_metrics[key]]
        for key in ['rounds_to_clear_bombs', 'first_defuse', 'second_defuse']:
            if avg_metrics[key]:
                avg_metrics[key] = round(sum(avg_metrics[key]) / len(avg_metrics[key]), 2)
            else:
                avg_metrics[key] = "N/A"

        print("\n=== Average Metrics Over All Simulations ===")
        for key, val in avg_metrics.items():
            print(f"{key}: {val}")

        return avg_metrics
