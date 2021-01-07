"""
Process for solver TSP
"""

# Libraries
from typing import Any, List
from csv import reader
from ortools.constraint_solver import pywrapcp, routing_enums_pb2


def read_csv(file_path: str, delimiter: str = ',') -> List[List[Any]]:
    """
    Read a file csv

    file_path: str -> Route of file ej: "./a/b/c.csv"
    delimiter: str -> delimiter for csv ej
    return [[],[],[],[]]
    """
    with open(file_path) as csv_file:
        csv_reader = reader(csv_file, delimiter=delimiter)
        return list(map(lambda x: list(map(int, x)), list(csv_reader)[1:]))


def print_solution(manager, routing, solution):
    """Prints solution on console."""
    print('Objective: {} miles'.format(solution.ObjectiveValue()))
    index = routing.Start(0)
    plan_output = 'Route for vehicle 0:\n'
    route_distance = 0
    while not routing.IsEnd(index):
        plan_output += ' {} ->'.format(manager.IndexToNode(index))
        previous_index = index
        index = solution.Value(routing.NextVar(index))
        route_distance += routing.GetArcCostForVehicle(
            previous_index,
            index,
            0
        )
    plan_output += ' {}\n'.format(manager.IndexToNode(index))
    print(plan_output)
    plan_output += 'Route distance: {}miles\n'.format(route_distance)


def operation():
    """Solve TSP"""
    file_path = 'src/second/data.csv'
    data = {}
    data['distance_matrix'] = read_csv(file_path)
    data['num_vehicles'] = 1
    data['depot'] = 0

    print('data - ', data)

    manager = pywrapcp.RoutingIndexManager(
        len(data['distance_matrix']),
        data['num_vehicles'],
        data['depot']
    )
    routing = pywrapcp.RoutingModel(manager)
    # RouringIndexManager have input parameters
    # 1. number of rows
    # 2. number of vehicles
    # 3. number corresponding to the depot

    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    solution = routing.SolveWithParameters(search_parameters)
    if solution:
        print_solution(manager, routing, solution)
