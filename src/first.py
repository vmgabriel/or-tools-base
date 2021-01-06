"""
The first Program
"""

# Libraries
from ortools.linear_solver import pywraplp


def first_solver() -> (float, float, float):
    """The First Solver"""
    # Create the Linear solver with the GLOP backend
    solver = pywraplp.Solver.CreateSolver('GLOP')
    # pywraplp is created in c++
    # GLOP_LINEAR_PROGRAMMING specifies GLOP solver

    # create the variables
    _x = solver.NumVar(0, 1, 'x')
    _y = solver.NumVar(0, 2, 'y')

    print('Number of variables = {}'.format(solver.NumVariables()))

    # Contraints
    _ct = solver.Constraint(0, 2, 'ct')
    _ct.SetCoefficient(_x, 1)
    _ct.SetCoefficient(_y, 1)
    # Set coefficient

    # objective function
    objective = solver.Objective()
    objective.SetCoefficient(_x, 3)
    objective.SetCoefficient(_y, 1)
    objective.SetMaximization()

    # Solver
    solver.Solve()
    return _x.solution_value(), _y.solution_value(), objective.Value()
