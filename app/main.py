from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/tasks/{task_id}")
async def say_hello(task_id: str):
    return {"message": f"Hello {task_id}"}
