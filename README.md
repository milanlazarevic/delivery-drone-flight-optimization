# Delivery drone optimization proxy for ArduPilot SITL and QGroundControl

### Description
This project implements a MAVLink proxy between ArduPilot SITL and QGroundControl for delivery drone mission optimization. The proxy intercepts mission uploads from QGroundControl, extracts waypoints, applies route optimization algorithms, and forwards the optimized mission to the autopilot.

The system is designed to evaluate and compare different optimization approaches, including Greedy Search and Ant Colony Optimization, in a simulated drone delivery environment. By reducing the total flight distance and improving waypoint ordering, the project aims to increase mission efficiency and reduce energy consumption.


### 1. Requirements
- [QGroundControl](https://docs.qgroundcontrol.com/master/en/qgc-user-guide/getting_started/download_and_install.html)
- [ArduPilot SITL](https://ardupilot.org/dev/docs/setting-up-sitl-on-linux.html)

### 2. Optimization algorithms
- [Greedy search](https://en.wikipedia.org/wiki/Greedy_algorithm)
- [Ant colony](https://en.wikipedia.org/wiki/Ant_colony_optimization_algorithms) 


<img width="775" height="867" alt="image" src="https://github.com/user-attachments/assets/9a93fac2-c526-48d7-8954-cec808e86e2d" />

