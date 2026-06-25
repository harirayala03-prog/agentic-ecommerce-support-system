from typing import TypedDict
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, END
from a2a_types import create_task, create_response, A2ATask, A2AResponse

load_dotenv()
model = ChatAnthropic(model="claude-sonnet-4-6")

class SupportState(TypedDict):
    customer_message: str
    intent: str
    final_response: str

def classify_intent(state: SupportState) -> SupportState:
    prompt = f"""Classify this customer message into exactly one word:
either "order_status" or "billing".
Message: {state['customer_message']}
Reply with only the one word, nothing else."""
    result = model.invoke(prompt)
    state["intent"] = result.content.strip().lower()
    return state

def handle_order_status_task(task: A2ATask) -> A2AResponse:
    prompt = f"""You are the Order Status specialist agent. A customer asked:
"{task['message']}"
Pretend you checked the system and their order is in transit, arriving in 2 days.
Write a short, friendly reply telling them this."""
    result = model.invoke(prompt)
    return create_response(task, sender="order_status_agent", result=result.content)

def handle_billing_task(task: A2ATask) -> A2AResponse:
    prompt = f"""You are the Billing specialist agent. A customer asked:
"{task['message']}"
Pretend you checked their account and there are no overcharges, but offer to
review their last invoice if they'd like.
Write a short, friendly reply."""
    result = model.invoke(prompt)
    return create_response(task, sender="billing_agent", result=result.content)

def order_status_node(state: SupportState) -> SupportState:
    task = create_task(sender="supervisor", receiver="order_status_agent", message=state["customer_message"])
    response = handle_order_status_task(task)
    state["final_response"] = response["result"]
    return state

def billing_node(state: SupportState) -> SupportState:
    task = create_task(sender="supervisor", receiver="billing_agent", message=state["customer_message"])
    response = handle_billing_task(task)
    state["final_response"] = response["result"]
    return state

def route_by_intent(state: SupportState) -> str:
    if state["intent"] == "order_status":
        return "order_status_node"
    else:
        return "billing_node"

graph = StateGraph(SupportState)
graph.add_node("classify_intent", classify_intent)
graph.add_node("order_status_node", order_status_node)
graph.add_node("billing_node", billing_node)

graph.set_entry_point("classify_intent")
graph.add_conditional_edges(
    "classify_intent",
    route_by_intent,
    {
        "order_status_node": "order_status_node",
        "billing_node": "billing_node"
    }
)
graph.add_edge("order_status_node", END)
graph.add_edge("billing_node", END)

app = graph.compile()

result = app.invoke({
    "customer_message": "Hi, I think I was charged twice this month, can you check?",
    "intent": "",
    "final_response": ""
})

print("Detected intent:", result["intent"])
print("Final response:", result["final_response"])