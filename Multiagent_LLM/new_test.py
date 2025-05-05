import datetime
import subprocess

def main(n_agent):
  rounds = 5# number of rounds in single experiment
  agents = n_agent
  n_stubborn = 0 # number of stubborn agents
  n_suggestible = 0 # number of suggestible agents
  n_exp = 9 # number of experiments
  current_datetime = datetime.datetime.now()
  # Format the date as a string
  formatted_date = current_datetime.strftime("%Y-%m-%d_%H-%M")
  out_file = "./log/scalar_debate/n_agents{}_rounds{}_n_exp{}_{}".format(agents, rounds, n_exp, formatted_date)
  # Build the command line
  cmd = [
    'python', './run.py',
    '--rounds', str(rounds),
    '--out_file', out_file,
    '--agents', str(agents),
    '--n_stubborn', str(n_stubborn),
    '--n_suggestible', str(n_suggestible),
    '--n_exp', str(n_exp),
    # '--not_full_connected' # uncomment this if you want use other topology structures
  ]
  # Run the command
  subprocess.run(cmd)

if __name__ == "__main__":
  main(n_agent=2)
