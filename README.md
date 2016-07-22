# JSONLoadBalancer

This package contains a LoadBalancer that allows a list of tasks to be distributed to Workers.

## Install

...

## Getting Started


The following scheme explains the use of the package :

```

                       +--------------+
                       |              |     info     +----------+
                       | Health Check | <----------> |          |
                       |              |              | Worker 1 |
+----------+  tasks    +------^-------+        +---> |          |
| Client 1 +----+             |                |     +----------+
+----------+    |             |info          task
                |    +--------v----------+     |     +----------+
+----------+    |    |                   |     |     |          |
| Client 2 +-------->+   Load Balancer   | <-------> | Worker 2 |
+----------+    |    |                   |     |     |          |
                |    +-------------------+     |     +----------+
+----------+    |                              |
| Client 3 +----+                              |     +----------+
+----------+                                   +---> |          |
                                                     | Worker 3 |
    ...                                              |          |
                                                     +----------+
                                                         ...

```

## Classes

The JSONLoadBalancer Package contains 4 main classes:
   -The Client, that send tasks
   -The Worker, that receive tasks
   -The Load Balancer, that distribute tasks
   -The Helth Check, that monitor the Load Balancer and the Workers status

All the messages between the classes are exchanged in json format.

## Starts the Load Balancer

To start the LoadBalancer, open two python consoles.
In the first :

```python
from JSONLoadBalancer import LoadBalancer
LB = LoadBalancer()
LB.startLB(log=True)
```

In the second :

```python
from JSONLoadBalancer import HealthCheck
HC = HealthCheck(log=True)
HC.startHC()
```

This will starts the LoadBalancer and the HealthCheck

## Define Workers

To create a worker, use the following syntax :

```python
from JSONLoadBalancer import Worker
WK = Worker(id, lbport, healthport)
```

Where :
  - `id` (string) is the worker unique id.
  - `lbport` (int) and `healthport` (int) are two ports listened by the worker in order to receive task from the Load Balancer and receive message from the Health Check

Then you will add tasks the worker should do.

```python
WK.addTask('DIAG',diagTask)
```

Here, when the worker receive a task named `'DIAG'`, it will call the diagTask function.
A task function must be in the form `taskFunction(**kwargs)` :
    the first kwargs argurments will be `kwargs['tasks']` and contains the task message coming from the Client.

Then, when all tasks are defined, start the worker using :
```python
WK.startWK()
```

## Start Client

To create a client, use the following syntax :

```python
from JSONLoadBalancer import Client
CL = Client()
```

Then create the tasks you want to send. A task is a dict that must contains a key named `'TASK'` :

```python
task = {'data': '/scratch/data/matrix19160.npy', 'load': 12}
```

You can then organize your task dict as you want, as long as the Workers are programmed to be able to understand it.
There are two reserved keys, that are `'HELLO'` and `'TASK'`, your task dict should not contain these two keys.
When the task is to be sent, send it using :

```python
CL.sendTask(taskname,task)
```

Where `taskname` (string) is the name of the task (your workers should also have a function that is able to read a task having this name)
The client interface will add two keys to the task dict :
    ```python{'HELLO' : 'TOWORKER'}``` in order to tell the Load Balancer that this is a task to be done by a Worker.
    ```python{'TASK' : taskname}``` to describe the task to be done by the worker

## Advance usages

...

## Licence

?


