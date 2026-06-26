import asyncio
import json
from typing import TypedDict
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, END
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from a2a_types import create_task, create_response, A2ATask, A2AResponse

load_dotenv()
model = ChatAnthropic(model="claude-sonnet-4-6")

server_params = StdioServerParameters(
    command="python",
    args=["mcp_server.py"]
)

class SupportState(TypedDict):
    customer_message: str
    customer_id: str
    order_id: str
    intent: str
    final_response: str

# A reusable helper: connect to the MCP server, call one tool, return the result.
async def call_mcp_tool(tool_name: str, arguments: dict) -> dict:
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            raw_text = result.content[0].text
            return json.loads(raw_text)

def classify_intent(state: SupportState) -> SupportState:
    prompt = f"""Classify this customer message into exactly one word:
either "order_status" or "billing".
Message: {state['customer_message']}
Reply with only the one word, nothing else."""
    result = model.invoke(prompt)
    state["intent"] = result.content.strip().lower()
    return state

async def handle_order_status_task(task: A2ATask, order_id: str) -> A2AResponse:
    order_data = await call_mcp_tool("lookup_order_status", {"order_id": order_id})

    prompt = f"""You are the Order Status specialist agent. A customer asked:
"{task['message']}"

Here is the REAL order data you looked up:
{json.dumps(order_data)}

Write a short, friendly reply using only the facts above. If there's an error
in the data, apologize and explain you couldn't find that order."""
    result = model.invoke(prompt)
    return create_response(task, sender="order_status_agent", result=result.content)

async def handle_billing_task(task: A2ATask, customer_id: str) -> A2AResponse:
    billing_data = await call_mcp_tool("lookup_billing_info", {"customer_id": customer_id})

    prompt = f"""You are the Billing specialist agent. A customer asked:
"{task['message']}"

Here is the REAL billing data you looked up:
{json.dumps(billing_data)}

Write a short, friendly reply using only the facts above."""
    result = model.invoke(prompt)
    return create_response(task, sender="billing_agent", result=result.content)

async def order_status_node(state: SupportState) -> SupportState:
    task = create_task(sender="supervisor", receiver="order_status_agent", message=state["customer_message"])
    response = await handle_order_status_task(task, state["order_id"])
    state["final_response"] = response["result"]
    return state

async def billing_node(state: SupportState) -> SupportState:
    task = create_task(sender="supervisor", receiver="billing_agent", message=state["customer_message"])
    response = await handle_billing_task(task, state["customer_id"])
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

async def main():
    result = await app.ainvoke({
        "customer_message": "Where is my order? It hasn't arrived yet.",
        "customer_id": "",
        "order_id": "",
        "intent": "",
        "final_response": ""
    })
    print("Detected intent:", result["intent"])
    print("Final response:", result["final_response"])

asyncio.run(main())
