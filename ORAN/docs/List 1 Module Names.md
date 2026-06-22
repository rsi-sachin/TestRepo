List 1: Module Names

1\. RAN INTENT PROVIDER (simple stub controlled through a orchestrator)

2\. SMO (simple stub controlled through a orchestrator)

3\. sub-module NON\_RT\_RIC (simple stub controlled through a orchestrator), parent is SMO

4\. NEAR\_RT\_RIC (simulator as per ORAN specifications - primary target), parent is ORAN\_INT\_INFO\_SOURCE

5\. ORAN\_EXT\_INFO\_SOURCE (simple stub controlled through a orchestrator), parent is ORAN\_INT\_INFO\_SOURCE

6\. sub-module O\_CU\_CP (simple stub controlled through a orchestrator), parent is ORAN\_INT\_INFO\_SOURCE

7\. sub-moduleO\_CU\_DP (simple stub controlled through a orchestrator), parent is ORAN\_INT\_INFO\_SOURCE

8\. sub-moduleO\_DU (simple stub controlled through a orchestrator), parent is ORAN\_INT\_INFO\_SOURCE

9\. sub-moduleO\_ENODEB (simple stub controlled through a orchestrator), parent is ORAN\_INT\_INFO\_SOURCE

10\. ORAN\_INT\_INFO\_SOURCE 

Functional Interfaces

1. E2 - used by module 6,7,8,9 to interact with module 4 
2. O1 - used by module 4, 6,7,8,9 to interact with 2
3. A1 - used by module 3 and 4
4. Generic Functional APIs - used by module 5 and 2



orchestrator is a top level module that sequentially or in parallel can issue commands to the modules/sub-modules it controls.

primary target is the actual module for which source code is written as per ORAN specifications. Timers, User contexts, Alerts, Counters, State Machines, Buffers etc are created for primary target.

current primary target is mentioned in above list. Once one unit is successfully developed and tested in this system, another module or sub-module shall become primary target. 

Goal is to create real time simulators for all the units mentioned in List 1.



As per Section 4.1.3 A1 Service Architecture, 

Non-RT RIC module defines policies that are provided to Near-RT RIC over A1 interface.

This statement is interpreted as 

1. Non-RT RIC has a functionality to create policies, Near-RT RIC to work as per these policies. 
2. Implement A1 interface as an API
3. Define the API called A1 Interface to communicate information about different policies to another module Near-RT RIC.
4. Each policy's status and feedback are exchanged using A1 interface (API) between Non-RT RIC and Near-RT RIC.
5. Non-RT RIC acts like a Master and Near-RT RIC acts like as Slave.



Next step: 

1. Implement monitoring function that receives input from Module 10 (comprising different sub-modules)

2\. Implement O1 interface as an API through which information is exchanged as per Step 1 above.

