from typing import TypedDict, Literal
import uuid

class A2ATask(TypedDict):
    task_id: str
    sender: str
    receiver: str
    message: str
    status: Literal["submitted"]

class A2AResponse(TypedDict):
    task_id: str
    sender: str
    receiver: str
    result: str
    status: Literal["completed", "input-required", "failed"]

def create_task(sender: str, receiver: str, message: str) -> A2ATask:
    return {
        "task_id": str(uuid.uuid4()),
        "sender": sender,
        "receiver": receiver,
        "message": message,
        "status": "submitted"
    }

def create_response(task: A2ATask, sender: str, result: str, status: str = "completed") -> A2AResponse:
    return {
        "task_id": task["task_id"],
        "sender": sender,
        "receiver": task["sender"],
        "result": result,
        "status": status
    }