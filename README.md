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
