agent_role = """You are an agent moving in a one-dimensional space from 0 to 100. 
The goal is to defuse all active bombs as fast as possible."""

game_description = """ Bomb can be Defused only if an agent goes to the exact bomb location. You cannot defuse a bomb if you are not at the bomb location.
There are only two active bombs located at {}. 
You are at {}.There is another agent at {} who can also defuse bombs. 
You need to choose your next position in order to defuse bombs quickly. """

round_description = """ There are active bombs at locations {}. You cannot defuse a bomb if you are not at the bomb location.
You have now moved to {}, the position of the other agent is {}, please choose your next position to efficiently defuse bombs."""
