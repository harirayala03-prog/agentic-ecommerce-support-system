from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
load_dotenv()
model=ChatAnthropic(model="claude-sonnet-4-6")
response=model.invoke("Hello, Claude! tell me about accuracy of kimi ai model")
print(response)