"""
Module for class customers
"""

# Libraries
from typing import Callable
from collections import namedtuple
from datetime import timedelta
import numpy as np

# Constants
RAD_EARTH = 6367
CIRC_EARTH = np.pi * RAD_EARTH
STDV = 6  # Standard deviation 99.9% will ve within +-3
# The number of seconds needed to 'unload' 1 unit of goods.
UNLOAD_TIME_BY_DEMAND = 300


def center_position(lat1, lat2) -> float:
    """Center the Position"""
    print(f'latitud center position debug - {lat1}')
    print(f'longitud center position debug - {lat2}')
    return lat1 - 0.5 * (lat1 - lat2)


def latitude_max(clat, box_size: int, is_upper: bool = True) -> float:
    """
    Latitude based into radious
    clat: center latitude
    box_size: integer base into length
    is_upper: boolean change if is upper or down
    """
    position_deg = clat - 180 if is_upper else clat + 180
    deg_box_size = position_deg * box_size
    return deg_box_size / CIRC_EARTH


def longitude_max(clat, clon, box_size: int, is_upper: bool = True) -> float:
    """
    Longitude based into radious
    clat: center latitude
    clon: center longitude
    box_size: length of
    """
    position_deg = clon - 180 if is_upper else clon + 180
    deg_box_size = position_deg * box_size
    circ_earth_radious = CIRC_EARTH * np.cos(np.deg2rad(clat))
    return deg_box_size / circ_earth_radious


def standard_coordinate(lat1, lat2, num_stops: int) -> float:
    """
    Standard Configuration Coordinate
    lat1: latitude main coordinate for use standard
    lat2: latitude secondary coordinate for use standard
    num_stops: configuration for steps
    """
    return (lat1 - np.random.randn(num_stops)) * ((lat2 - lat1) / STDV)


def haversine(lon1, lat1, lon2, lat2):
    """
        Calculate the great circle distance between two points
        on the earth specified in decimal degrees of latitude and longitude.
        https://en.wikipedia.org/wiki/Haversine_formula
        Args:
            lon1: longitude of pt 1,
            lat1: latitude of pt 1,
            lon2: longitude of pt 2,
            lat2: latitude of pt 2
        Returns:
            the distace in km between pt1 and pt2
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    _a = (
        np.sin(dlat / 2)**2 +
        np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    )
    _c = 2 * np.arcsin(np.sqrt(_a))

    # 6367 km is the radius of the Earth
    _km = 6367 * _c
    return _km


class Customers():
    """
    A class that generates and holds customers information.

    args: extend -> Additional Information
    """

    manager = None
    distmat = None

    def __init__(
            self,
            extents=None,
            center=(53.381393, -1.474611),
            box_size=10,
            num_stops=100,
            min_demand=0,
            max_demand=25,
            min_tw=1,
            max_tw=5
    ):
        # The number of customers and depots
        self.number = num_stops

        location = namedtuple('Location', ['lat', 'lon'])
        if extents is not None:
            self.extents = extents
            # The lower left and upper right points
            self.center = namedtuple(
                center_position(extents['urcrnrlat'], extents['llcrnrlat']),
                center_position(extents['urcrnrlon'], extents['llcrnrlon'])
            )
        else:
            (clat, clon) = self.center = location(center[0], center[1])

            # Area of points - left, right, upper, down
            self.extents = {
                'llcrnrlon': longitude_max(clat, clon, box_size),
                'llcrnrlat': latitude_max(clat, box_size),
                'urcrnrlon': longitude_max(clat, clon, box_size, False),
                'urcrnrlat': latitude_max(clat, box_size, False)
            }
        # Name of stop - indexed 0 or -1
        stops = np.array(range(0, num_stops))
        lats = standard_coordinate(
            self.extents['llcrnrlat'],
            self.extents['urcrnrlat'],
            num_stops
        )
        lons = standard_coordinate(
            self.extents['llcrnrlon'],
            self.extents['urcrnrlon'],
            num_stops
        )

        # uniformly distribuited integer demands
        demands = np.random.randint(min_demand, max_demand, num_stops)

        self.time_horizon = 24 * 60**2  # A 24 hour Period

        # The customers demand min to max hour time window for each delivery
        time_windows = np.random.randint(
            min_tw * 3600, max_tw * 3600, num_stops
        )

        # The Last time a delivery window can start
        latest_time = self.time_horizon - time_windows
        start_times = [None for o in time_windows]
        stop_times = [None for o in time_windows]

        # Make random timedeltas, nominally from the start of the day.
        for idx in range(self.number):
            stime = int(np.random.randint(0, latest_time[idx]))
            start_times[idx] = timedelta(seconds=stime)
            stop_times[idx] = (
                start_times[idx] + timedelta(seconds=int(time_windows[idx])))
        # A named tuple for the customer
        customer = namedtuple(
            'Customer',
            [
                'index',  # the index of the stop
                'demand',  # the demand for the stop
                'lat',  # the latitude of the stop
                'lon',  # the longitude of the stop
                'tw_open',  # timedelta window open
                'tw_close'
            ])  # timedelta window cls

        self.customers = [
            customer(idx, dem, lat, lon, tw_open, tw_close)
            for idx, dem, lat, lon, tw_open, tw_close in zip(
                    stops,
                    demands,
                    lats,
                    lons,
                    start_times,
                    stop_times
            )
        ]

        self.service_time_per_dem = UNLOAD_TIME_BY_DEMAND  # seconds

    def set_manager(self, manager):
        """Set Manager"""
        self.manager = manager

    def central_start_node(self, invert=False) -> int:
        """
        Random Starting Nonde
        """
        num_nodes = len(self.customers)
        dist = np.empty((num_nodes, 1))
        for idx_to in range(num_nodes):
            dist[idx_to] = haversine(
                self.center.lon, self.center.lat,
                self.customers[idx_to].lon,
                self.customers[idx_to].lat
            )
        furthest = np.max(dist)

        if invert:
            prob = dist * 1.0 / sum(dist)
        else:
            prob = (furthest - dist * 1.0) / sum(furthest - dist)
        indexes = np.array([range(num_nodes)])
        start_node = np.random.choice(
            indexes.flatten(), size=1, replace=True, p=prob.flatten()
        )
        return start_node[0]

    def make_distance_mat(self, method='haversine'):
        """Return the distance matrix and make it a member of Customer"""
        self.distmat = np.zeros((self.number, self.number))
        methods = {
            'haversine': haversine
        }
        assert method in methods
        for frm_idx in range(self.number):
            for to_idx in range(self.number):
                if frm_idx != to_idx:
                    frm_c = self.customers[frm_idx]
                    to_c = self.customers[to_idx]
                    self.distmat[frm_idx, to_idx] = haversine(
                        frm_c.lon,
                        frm_c.lat,
                        to_c.lon,
                        to_c.lat
                    )
        return self.distmat

    def get_total_demand(self) -> float:
        """
        Return the total demand of all customers.
        """
        return sum([c.demand for c in self.customers])

    def return_dist_callback(self, **kwargs) -> Callable:
        """
        Return a Callback function for distance matrix
        """
        self.make_distance_mat(**kwargs)

        def dist_return(from_index, to_index):
            # Convert from routing variable Index to distance matrix NodeIndex.
            from_node = self.manager.IndexToNode(from_index)
            to_node = self.manager.IndexToNode(to_index)
            return (self.distmat[from_node][to_node])

        return dist_return

    def zero_depot_demands(self, depot):
        """
        Zero out the demands and time windows of depot
        """
        start_depot = self.customers[depot]
        self.customers[depot] = start_depot._replace(
            demand=0,
            tw_open=None,
            tw_close=None
        )

    def return_dem_callback(self) -> Callable:
        """
        Return a callback function that gives the demands.
        Returns:
            function: dem_return(a) A function that takes the 'from' node
                index and returns the distance in km.
        """

        def dem_return(from_index):
            # Convert from routing variable Index to distance matrix NodeIndex.
            from_node = self.manager.IndexToNode(from_index)
            return self.customers[from_node].demand

        return dem_return


    def make_service_time_call_callback(self) -> Callable:
        """
        Return a callback function that provides
        the time spent servicing the customer
        """

        return lambda a, b: (
            self.customers[a].demand * self.service_time_per_dem
        )

    def make_transit_time_callback(self, speed_kmph=10) -> Callable:
        """
        Create a callback function transit time
        assuming an average speed of speed_kmph
        """
        return lambda a, b: (
            self.distmat[a][b] / (speed_kmph * 1.0 / 60**2)
        )
