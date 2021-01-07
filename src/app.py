"""
App configuration
"""

# Modules
from first import first_solver
from second import solve as second_solver
from third import solve as third_solver


def load():
    """Load process"""
    # Load the first
    solve1, solve2, objective = first_solver()
    print('Solution for first problem')
    print(f'Objective - {objective}')
    print(f'x - {solve1}')
    print(f'y - {solve2}')

    print('--------------------')
    second_solver()

    print('--------------------')
    third_solver()


if __name__ == '__main__':
    load()
