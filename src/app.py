"""
App configuration
"""

# Modules
from first import first_solver
from second import solve as second_solver
from third import solve as third_solver
from fourth import solve as fourth_solver
from fifth import solve as fifth_solver
from sixth import solve as sixth_solver


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

    print('--------------------')
    fourth_solver()

    print('--------------------')
    fifth_solver()

    print('--------------------')
    # sixth_solver()


if __name__ == '__main__':
    load()
