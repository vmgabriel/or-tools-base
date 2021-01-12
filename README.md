# Or Tool Tutorial 1

## Description
The OR tools is a solver problem of optimization:

- Vehicle Routing: The most important for deliver packages
- Scheduling: problem for complex tasks
- Bin Packing: Pack as many objects

This use algorithms to narrow down the search set for find the optimal.

Problems that solve:

- Contraint Programming: Solve mathematics problems.
- Linear and mixed-integer program: Problems based into configuration of single problems.
- Vehicle Routing: Library for indentifying best vehicle routes given constraints.
- Graph algorithms: short path into graph

This find the best solution out of large set of possible solutions

Each of optimization problems bas the following elements:
- The objective: The quantity to optimize -> for example minimize cost.
- The contraints: Restrictions on the set of possible solutions.

The first step for solve an optimization problem is identifying this two elements.

1. Optimizing minimize

For each language, the basic steps for setting up and solving a problem are the same:
- Import the required libraries.
- Declare the solver.
- Create the variables.
- Define the constraints.
- Define the objective function.
- Invoke the solver and display the results.


**Vehicle Routing**
One of the  most important application of optimization is vehicle routing the goal is to find the best routes for a fleet of vehicles visiting a set of locations.

The most famous routing problem is the Traveling Salesman Problem(TSP): This find the shortest route for slaesman who needs to visit customers at different locations and return to locations and return to the starting point. This can represented by a graph.

A more general version of the TSP is the vehicle routing problem(VRP) in which there are multiple vehicles. In most cases, VRPs have constraints: for example, vehivles might have capacities for the maximum weight or volume of items they can carry, or drivers might be required to visit locations during specified time windows, in this case use the following cases for solve:
- Traveling salesman problem: the classic routing problem
- Vehicle Routing Problem: A generalization of the TSP with various vehicles
- VRP with capacity constraints: the vehicles have maximum capacities for the items
- VRP with time windows: The vehicles must visit the locations in specified the interval
- VRP with resource contraints: sush as space or personnel to load and unload vehicles at the depot
- VRP with dropped visits: the vehicles are not required all location

**Traveling Salesman Problem**
Shows who to solve the TSP

there are various ways for resolve problems in this style, the control is the mode for resolve this situation and mode with this manage control

**Vehicle Routing Problem**
in VRP the goal is to find optimal routes for multiples vehicles visiting a set of locations.

A better way to define optimal routes is to minimize the length of the longest single route among all vehicles this is the right definition if the goal is to complete all deliveries as soon as possible.

- Capacity contraints -> pick up items at each location
- Time windows -> each location must be visited within a specific time window

We need the distence of matrix for solve that problems

**Manhattan distance**
Distance between two points (x1,x2) and (y1,y2) is defined to be |x1 - y1| + |x2 - y2|

[manhattan implementing](https://gist.github.com/vmgabriel/2cd48fe2b560a35e290a393d23abdd80 "manhattan implementing")

**Google Distance Matrix API**
For create the distance matrix for any set of locations defined by addresses, or by latitudes and longitudes.

[Documentation of Google Distance Matrix](https://developers.google.com/maps/gmp-get-started#create-billing-account "Configuration of Google Distance Matrix API")


**Capacity Constraints**
Capacitated Vehicle Routing Problem(CVRP) is a VRP in which vehicles with limited carrying capacity need to pick up for deliver, this hava a maximum capacity

**Vehicle Routing with Pickups and Deliveries**
This is VRP in which each vehicle picks up items at various locations and drops them off at others.
Minimize  the length of longest route.

**Vehicle Routing Problem with Time Windows VRPTWs**
Many vehicles routing problems involve scheduling visits to customers who are only abailable during specific time windows.

**Dimension Routing**
The routing solver uses an object called a dimension to keep track of quantities that accumulate along a vehicle's route, such asthe travel time or, if the vehicle is making pickups and deliveries, the total weight.

this include two issues.

- VRPTW
- CVRP

**Resource Contraints**
VRPTW that also has constraints at the depot all vehicles need to ve loaded before departing the depot and unloaded upon return. Since there are only two available loading docks, at most wto vehicles can ve loaded of unloaded or unloaded at the same time. As a result, some vehicles must wait for others to ve loaded, delaying their departure from the depot. The problem is to find optimal vehicle routes for the VRPTW thtat also meet the loading and unloading constraints at the depot.


**Penalties and Dropping Visits**
How to handle routing problems that have no feasible solution, dueto constraints. For example, if you are given a VRP with capacity constraints in which the total demand at all locations exceeds the total capacity of the vehicles, no solution is possible, in such cases, the vehicles must drop visits to some locatiosn. The problem is how to decide which visits to drop.

To solve the problem, we introduce new costs - called penalties

**Common Routing Tasks**
Some common tasks related to solving vehicle routing problems

**Routing Options**
For Routing Solver this can following:

- Search Limits: Terminate the solver after it reaches a specified limit, such as the maximum length of time
- First Solution Strategy: Method for solver uses to find an initial solution.
- Search Status: Print status
- Local Search Options: Local Strategies - Metaheuristics -
- Propagation Control: -> verify full propagation

## Installation
Load with:
```bash
make dependencies
```

if the installation is for production then:
```bash
make dependencies ENV=production
```

## Load
for run program:
- previous install dependencies

```bash
make run
```

if the run is for production then
```bash
make run ENV=production
```
