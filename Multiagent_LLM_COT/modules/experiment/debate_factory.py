
from .scalar_debate import ScalarDebate

def debate_factory(name, args, connectivity_matrix):
    """
    Create a debate instance based on the given name and arguments.

    Args:
        name (str): The name of the debate type (either "scalar" or "2d").
        args (dict): A dictionary of arguments to initialize the debate.
        connectivity_matrix (list): The connectivity matrix for the debate.

    Returns:
        Debate: An instance of the appropriate debate class (ScalarDebate or Vector2dDebate).

    Note:
        If the 'name' argument is not recognized, the function returns None.

    Example:
        To create a ScalarDebate:
        debate_factory("scalar", args, connectivity_matrix)

        To create a Vector2dDebate:
        debate_factory("2d", args, connectivity_matrix)
    """
    if name == "scalar":
        return ScalarDebate(args, connectivity_matrix)

    else:
        return None