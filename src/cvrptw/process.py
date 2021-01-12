"""
Load the process for proced into module of cvrptw
"""

# Libraries
from datetime import timedelta
from matplotlib import pyplot as plt
import numpy as np
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2

# Modules
from cvrptw.customer import Customers
from cvrptw.vehicle import Vehicles


def discrete_cmap(N, base_cmap=None):
    """
    Create an N-bin discrete colormap from the specified input map
    """
    # Note that if base_cmap is a string or None, you can simply do
    #    return plt.cm.get_cmap(base_cmap, N)
    # The following works for string, None, or a colormap instance:

    base = plt.cm.get_cmap(base_cmap)
    color_list = base(np.linspace(0, 1, N))
    cmap_name = base.name + str(N)
    return base.from_list(cmap_name, color_list, N)


def vehicle_output_string(manager, routing, plan):
    """
    Return a string displaying the output of the routing instance and
    assignment (plan).
    Args: routing (ortools.constraint_solver.pywrapcp.RoutingModel): routing.
    plan (ortools.constraint_solver.pywrapcp.Assignment): the assignment.
    Returns:
        (string) plan_output: describing each vehicle's plan.
        (List) dropped: list of dropped orders.
    """
    dropped = []
    for order in range(routing.Size()):
        if (plan.Value(routing.NextVar(order)) == order):
            dropped.append(str(order))

    capacity_dimension = routing.GetDimensionOrDie('Capacity')
    time_dimension = routing.GetDimensionOrDie('Time')
    plan_output = ''

    for route_number in range(routing.vehicles()):
        order = routing.Start(route_number)
        plan_output += 'Route {0}:'.format(route_number)
        if routing.IsEnd(plan.Value(routing.NextVar(order))):
            plan_output += ' Empty \n'
        else:
            while True:
                load_var = capacity_dimension.CumulVar(order)
                time_var = time_dimension.CumulVar(order)
                node = manager.IndexToNode(order)
                plan_output += \
                    ' {node} Load({load}) Time({tmin}, {tmax}) -> '.format(
                        node=node,
                        load=plan.Value(load_var),
                        tmin=str(timedelta(seconds=plan.Min(time_var))),
                        tmax=str(timedelta(seconds=plan.Max(time_var))))

                if routing.IsEnd(order):
                    plan_output += ' EndRoute {0}. \n'.format(route_number)
                    break
                order = plan.Value(routing.NextVar(order))
        plan_output += '\n'

    return (plan_output, dropped)


def build_vehicle_route(manager, routing, plan, customers, veh_number):
    """
    Build a route for a vehicle by starting at the strat node and
    continuing to the end node.
    Args: routing (ortools.constraint_solver.pywrapcp.RoutingModel): routing.
    plan (ortools.constraint_solver.pywrapcp.Assignment): the assignment.
    customers (Customers): the customers instance.  veh_number (int): index of
    the vehicle
    Returns:
        (List) route: indexes of the customers for vehicle veh_number
    """
    veh_used = routing.IsVehicleUsed(plan, veh_number)
    print('Vehicle {0} is used {1}'.format(veh_number, veh_used))
    if veh_used:
        route = []
        node = routing.Start(veh_number)  # Get the starting node index
        route.append(customers.customers[manager.IndexToNode(node)])
        while not routing.IsEnd(node):
            route.append(customers.customers[manager.IndexToNode(node)])
            node = plan.Value(routing.NextVar(node))

        route.append(customers.customers[manager.IndexToNode(node)])
        return route
    else:
        return None


def plot_vehicle_routes(veh_route, ax1, customers, vehicles):
    """
    Plot the vehicle routes on matplotlib axis ax1.
    Args: veh_route (dict): a dictionary of routes keyed by vehicle idx.  ax1
    (matplotlib.axes._subplots.AxesSubplot): Matplotlib axes  customers
    (Customers): the customers instance.  vehicles (Vehicles): the vehicles
    instance.
  """
    veh_used = [v for v in veh_route if veh_route[v] is not None]

    cmap = discrete_cmap(vehicles.number + 2, 'nipy_spectral')

    for veh_number in veh_used:

        lats, lons = zip(*[(c.lat, c.lon) for c in veh_route[veh_number]])
        lats = np.array(lats)
        lons = np.array(lons)
        s_dep = customers.customers[vehicles.starts[veh_number]]
        s_fin = customers.customers[vehicles.ends[veh_number]]
        ax1.annotate(
            'v({veh}) S @ {node}'.format(
                veh=veh_number, node=vehicles.starts[veh_number]),
            xy=(s_dep.lon, s_dep.lat),
            xytext=(10, 10),
            xycoords='data',
            textcoords='offset points',
            arrowprops=dict(
                arrowstyle='->',
                connectionstyle='angle3,angleA=90,angleB=0',
                shrinkA=0.05),
        )
        ax1.annotate(
            'v({veh}) F @ {node}'.format(
                veh=veh_number, node=vehicles.ends[veh_number]),
            xy=(s_fin.lon, s_fin.lat),
            xytext=(10, -20),
            xycoords='data',
            textcoords='offset points',
            arrowprops=dict(
                arrowstyle='->',
                connectionstyle='angle3,angleA=-90,angleB=0',
                shrinkA=0.05),
        )
        ax1.plot(lons, lats, 'o', mfc=cmap(veh_number + 1))
        ax1.quiver(
            lons[:-1],
            lats[:-1],
            lons[1:] - lons[:-1],
            lats[1:] - lats[:-1],
            scale_units='xy',
            angles='xy',
            scale=1,
            color=cmap(veh_number + 1))


def run():
    """Solve the problem"""
    # Create a set of customer, (and depot) stops.
    customers = Customers(
        num_stops=50,
        min_demand=1,
        max_demand=15,
        box_size=40,
        min_tw=3,
        max_tw=6
    )

    # Create a list of inhomgenious vehicle capacities as integer units.
    capacity = [50, 75, 100, 125, 150, 175, 200, 250]

    # Create a list of inhomogeneous fixed vehicle costs.
    cost = [int(100 + 2 * np.sqrt(c)) for c in capacity]

    # Create a set of vehicles, the number set by the length of capacity.
    vehicles = Vehicles(capacity=capacity, cost=cost)

    # check to see that the problem is feasible, if we don't have enough
    # vehicles to cover the demand, there is no point in going further.
    assert (customers.get_total_demand() < vehicles.get_total_capacity())

    # Set the starting nodes, and create a callback fn for the starting node.
    start_fn = vehicles.return_starting_callback(
        customers,
        same_start_finish=False
    )

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(
        customers.number,  # int number
        vehicles.number,  # int number
        vehicles.starts,  # List of int start depot
        vehicles.ends)  # List of int end depot

    customers.set_manager(manager)

    # Set model parameters
    model_parameters = pywrapcp.DefaultRoutingModelParameters()

    # The solver parameters can be accessed from the model parameters. For example :
    #   model_parameters.solver_parameters.CopyFrom(
    #       pywrapcp.Solver.DefaultSolverParameters())
    #    model_parameters.solver_parameters.trace_propagation = True

    # Make the routing model instance.
    routing = pywrapcp.RoutingModel(manager, model_parameters)

    parameters = pywrapcp.DefaultRoutingSearchParameters()
    # Setting first solution heuristic (cheapest addition).
    parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    # Routing: forbids use of TSPOpt neighborhood, (this is the default behaviour)
    parameters.local_search_operators.use_tsp_opt = pywrapcp.BOOL_FALSE
    # Disabling Large Neighborhood Search, (this is the default behaviour)
    parameters.local_search_operators.use_path_lns = pywrapcp.BOOL_FALSE
    parameters.local_search_operators.use_inactive_lns = pywrapcp.BOOL_FALSE

    parameters.time_limit.seconds = 10
    parameters.use_full_propagation = True
    # parameters.log_search = True

    # Create callback fns for distances, demands, service and transit-times.
    dist_fn = customers.return_dist_callback()
    dist_fn_index = routing.RegisterTransitCallback(dist_fn)

    dem_fn = customers.return_dem_callback()
    dem_fn_index = routing.RegisterUnaryTransitCallback(dem_fn)

    # Create and register a transit callback.
    serv_time_fn = customers.make_service_time_call_callback()
    transit_time_fn = customers.make_transit_time_callback()

    def tot_time_fn(from_index, to_index):
        """
        The time function we want is both transit time and service time.
        """
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return serv_time_fn(
            from_node,
            to_node
        ) + transit_time_fn(
            from_node,
            to_node
        )

    tot_time_fn_index = routing.RegisterTransitCallback(tot_time_fn)

    # Set the cost function (distance callback) for each arc, homogeneous for
    # all vehicles.
    routing.SetArcCostEvaluatorOfAllVehicles(dist_fn_index)

    # Set vehicle costs for each vehicle, not homogeneous.
    for veh in vehicles.vehicles:
        routing.SetFixedCostOfVehicle(veh.cost, int(veh.index))

    # Add a dimension for vehicle capacities
    null_capacity_slack = 0
    routing.AddDimensionWithVehicleCapacity(
        dem_fn_index,  # demand callback
        null_capacity_slack,
        capacity,  # capacity array
        True,
        'Capacity')
    # Add a dimension for time and a limit on the total time_horizon
    routing.AddDimension(
        tot_time_fn_index,  # total time function callback
        customers.time_horizon,
        customers.time_horizon,
        True,
        'Time')

    time_dimension = routing.GetDimensionOrDie('Time')
    for cust in customers.customers:
        if cust.tw_open is not None:
            time_dimension.CumulVar(manager.NodeToIndex(cust.index)).SetRange(
                cust.tw_open.seconds, cust.tw_close.seconds)
    """
     To allow the dropping of orders, we add disjunctions to all the customer
    nodes. Each disjunction is a list of 1 index, which allows that customer to
    be active or not, with a penalty if not. The penalty should be larger
    than the cost of servicing that customer, or it will always be dropped!
    """
    # To add disjunctions just to the customers, make a list of non-depots.
    non_depot = set(range(customers.number))
    non_depot.difference_update(vehicles.starts)
    non_depot.difference_update(vehicles.ends)
    penalty = 400000  # The cost for dropping a node from the plan.
    nodes = [
        routing.AddDisjunction([
            manager.NodeToIndex(c)
        ], penalty) for c in non_depot
    ]

    # This is how you would implement partial routes if you already knew part
    # of a feasible solution for example:
    # partial = np.random.choice(list(non_depot), size=(4,5), replace=False)

    # routing.CloseModel()
    # partial_list = [partial[0,:].tolist(),
    #                 partial[1,:].tolist(),
    #                 partial[2,:].tolist(),
    #                 partial[3,:].tolist(),
    #                 [],[],[],[]]
    # print(routing.ApplyLocksToAllVehicles(partial_list, False))

    # Solve the problem !
    assignment = routing.SolveWithParameters(parameters)

    # The rest is all optional for saving, printing or plotting the solution.
    if assignment:
        # # save the assignment, (Google Protobuf format)
        # save_file_base = os.path.realpath(__file__).split('.')[0]
        # if routing.WriteAssignment(save_file_base + '_assignment.ass'):
        #    print('succesfully wrote assignment to file ' + save_file_base +
        #          '_assignment.ass')

        print('The Objective Value is {0}'.format(assignment.ObjectiveValue()))

        plan_output, dropped = vehicle_output_string(
            manager,
            routing,
            assignment
        )
        print(plan_output)
        print('dropped nodes: ' + ', '.join(dropped))

        # you could print debug information like this:
        # print(routing.DebugOutputAssignment(assignment, 'Capacity'))

        vehicle_routes = {}
        for veh in range(vehicles.number):
            vehicle_routes[veh] = build_vehicle_route(
                manager,
                routing,
                assignment,
                customers,
                veh
            )

        # Plotting of the routes in matplotlib.
        fig = plt.figure()
        ax = fig.add_subplot(111)
        # Plot all the nodes as black dots.
        clon, clat = zip(*[(c.lon, c.lat) for c in customers.customers])
        ax.plot(clon, clat, 'k.')
        # plot the routes as arrows
        plot_vehicle_routes(vehicle_routes, ax, customers, vehicles)
        plt.show()

    else:
        print('No assignment')
