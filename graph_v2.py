from typing import TypedDict
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic   
from langgraph.graph import stategraph, END
load_dotenv()
model=ChatAnthropic(model="claude-sonnet-4-6")

class support(TypedDict):
    accuracy: str
    precision: str
    recall: str

def classify_intent(state: supportstate)
    prompt=f"""classify this customer message into one word;
    either "order status" or "billing".
message: {state['customer_message']}
reply with only one word, nothing else"""
    result=model.invoke(prompt)
    state['intent']=result.content.strip().lower()
    return state
def order_status_node(st)

    