"""
Vehicle process module for hold information
"""

# Libraries
from typing import Callable
from collections import namedtuple
import numpy as np


class Vehicles():
    """
    A class to crate and hold vehicles information.

    The Vehicles in a CVRPTW problem service the customers and belong to a
    depot. The class Vehicles creates a list of named tuples describing the
    Vehicles.  The main characteristics are the vehicle capacity, fixed cost,
    and cost per km.  The fixed cost of using a certain type of vehicles can be
    higher or lower than others. If a vehicle is used, i.e. this vehicle serves
    at least one node, then this cost is added to the objective function.
    """

    starts = None
    ends = None

    def __init__(
            self,
            capacity=100,
            cost=100,
            number=None
    ):
        Vehicle = namedtuple('Vehicle', ['index', 'capacity', 'cost'])

        self.number = np.size(capacity) if number is None else number
        idxs = np.array(range(0, self.number))

        if np.isscalar(capacity):
            capacities = capacity * np.ones_like(idxs)
        elif np.size(capacity) != self.number:
            print('capacity is neither scalar, nor the same size as num!')
        else:
            capacities = capacity

        if np.isscalar(cost):
            costs = cost * np.ones_like(idxs)
        elif np.size(cost) != self.number:
            print(np.size(cost))
            print('cost is neither scalar, nor the same size as num!')
        else:
            costs = cost


        print('comparative - ', list(zip(idxs, capacities, costs)))

        self.vehicles = [
            Vehicle(idx, capacity, cost)
            for idx, capacity, cost in zip(idxs, capacities, costs)
        ]

    def get_total_capacity(self) -> float:
        """Total capacity"""
        return (sum([c.capacity for c in self.vehicles]))

    def return_starting_callback(
            self,
            customers,
            same_start_finish=False
    ) -> Callable:
        """Starting callback process"""
        # Create a different starting and finishing depot for each vehicle
        self.starts = [
            int(customers.central_start_node()) for o in range(self.number)
        ]
        if same_start_finish:
            self.ends = self.starts
        else:
            self.ends = [
                int(customers.central_start_node(invert=True))
                for o in range(self.number)
            ]
        # The depots will not have demands, so zero them.
        for depot in self.starts:
            customers.zero_depot_demands(depot)
        for depot in self.ends:
            customers.zero_depot_demands(depot)

        return lambda v: self.starts[v]
