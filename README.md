# TaskRestApi
REST API for managing tasks using poetry, FastAPI and dependency-injector

## Requirements

REST API which will manage tasks, each task is assigned to a user. Each user is only able
to see their own tasks.
A task can only have one status at a time, which could be one of the following:
- Pending
- Doing
- Blocked
- Done


If a task were to be deleted, it must be moved into a history table for record purposes.
The following requirements must be met:
- Python 3.9 and 3.10 support
- Correctly apply code formatting, preferably using the Black format
- Apply type annotations
- Use of a light weight framework
- Tasks must be stored in a database
- Database must be managed by code using migrations


Bonus items:
• Sub task support
• Restoring of deleted tasks
• Setting due dates for tasks
• Adding labels for tasks
• Documentation illustrating the design and thought process for the implemented solution

![Task Api Spec](./docs/images/task-api.png)

##TODO

- pre-commit
  - ~~black code formatting~~
  - linting
- project setup
  - ~~fastapi~~
  - ~~directory structure~~
    - ~~tests~~
    - ~~routes~~
    - ~~dependency injector~~
- ~~spec out task api endpoints~~
  - ~~endpoints~~
  - resources
  - request structure
  - response structure
    - common error format
  - edge cases
- ~~model design~~
- migrations
- get tasks endpoint
  - ~~initial implementation~~
  - filtering
  - pagination
- update task endpoint
  - ~~PUT replace of tasks~~
  - PATCH partial update
- ~~delete task endpoint~~
- ~~database setup~~
- ~~history table migration~~
- ~~add method to Taskmanager to retrieve a deleted task history entry~~
- restore task endpoint
- documentation on how to setup the project

## Icebox

Things I want to get back to, time permitting. Putting them on ice.

How should the user_id be passed into the TaskManager? Should it be its own parameter or as part of CreateTask, UpdateTask... ?

## Trade Offs & Assumptions

I am not going to implement proper authentication. I will assume that user management and authentication is handled by a middleware or api gateway or authentication service, and will use a query parameter to set the user_id.
I will also assume no user knows another users user_id.
I have chosen a query parameter so that swagger ui is easy to use. You can't edit request headers easily without editing the request headers manually via the web console or browser extension. 
I don't want to spend time configuring authentication properly using one of many authentication mechanisms.

TODO: add assumption about number of sub tasks
TODO: add trade off about returning None from TaskManager instead of raising an Exception or returning Errors
TODO: tradeoff for not implementing partial update (PATCH), and how all sub tasks will need to be passed in request body with PUT.
TODO: add external documentation links to tradeoffs and assumptions
TODO: test code duplication
TODO: add note about how fast the in memory tests are

## Retrospective

### Could I have used sqlite inmemory database instead of writing my own custom inmemory database using dictionaries and keys? 

It would have made filtering and pagination easier to implement in memory. 
It would have forced me to think about the database structure earlier, which I would prefer to delay until the whole api is fleshed out.
Databases require configuration and setup, and I would prefer to delay making decisions about that until later.

### How come I have used pydantic's BaseModel.model_dump() everywhere? 

This exercise has shown gaps in my knowledge of how to use pydantic efficiently. Something I will work on in the future.

### How come I didn't setup linting/mypy from the start?

I wanted to get started and implement the api endpoints first. I haven't setup linting in a while and did not want to spend long at the start setting up and debugging it.


