"""
App for vehicles routing problem - solving common problem
"""

# Libraries
from typing import Any, List
from csv import reader
from ortools.constraint_solver import pywrapcp


def read_csv(
        file_path: str,
        delimiter: str = ',',
        mode_list: bool = True
) -> List[Any]:
    """
    Read a file csv

    file_path: str -> Route of file ej: "./a/b/c.csv"
    delimiter: str -> delimiter for csv ej
    return [[],[],[],[]]
    """
    with open(file_path) as csv_file:
        csv_reader = reader(csv_file, delimiter=delimiter)
        return (
            list(map(lambda x: list(map(int, x)), list(csv_reader)[1:]))
            if mode_list else
            list(map(lambda x: tuple(map(int, x)), list(csv_reader)[1:]))
        )


def create_data_model():
    """Stores the data for the problem."""
    data = {}
    file_name = 'src/twelfth/data.csv'
    data['distance_matrix'] = read_csv(file_name)
    data['initial_routes'] = [
        [8, 16, 14, 13, 12, 11],
        [3, 4, 9, 10],
        [15, 1],
        [7, 5, 2, 6],
    ]
    data['num_vehicles'] = 4
    data['depot'] = 0
    return data


def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    max_route_distance = 0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        while not routing.IsEnd(index):
            plan_output += ' {} -> '.format(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        plan_output += '{}\n'.format(manager.IndexToNode(index))
        plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        print(plan_output)
        max_route_distance = max(route_distance, max_route_distance)
    print('Maximum of the route distances: {}m'.format(max_route_distance))


def run():
    """Solve the CVRP problem"""
    # Instantiate the data problem.
    data = create_data_model()

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(
        len(data['distance_matrix']),
        data['num_vehicles'],
        data['depot']
    )

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Distance constraint.
    dimension_name = 'Distance'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        3000,  # vehicle maximum travel distance
        True,  # start cumul to zero
        dimension_name
    )
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    initial_solution = routing.ReadAssignmentFromRoutes(
        data['initial_routes'],
        True
    )
    print('Initial solution:')
    print_solution(data, manager, routing, initial_solution)

    # Set default search parameters.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()

    # Solve the problem.
    solution = routing.SolveFromAssignmentWithParameters(
        initial_solution, search_parameters
    )

    # Print solution on console.
    if solution:
        print('Solution after search:')
        print_solution(data, manager, routing, solution)
