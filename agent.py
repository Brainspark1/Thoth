from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

# Model
llm = ChatOllama(model="llama3.2")

# Tool
search = DuckDuckGoSearchRun()

@tool
def web_search(query: str) -> str:
    """Search internet for information."""
    return search.run(query)

tools = [web_search]

# Agent (using new LangChain v0.3+ API)
from langchain.agents import create_agent

agent = create_agent(
    llm,
    tools,
    system_prompt="""You are a research AI assistant.

Think step by step."""
)

print("\nThoth")
print("Type 'exit' to quit\n")

while True:
    user_input = input("You: ")

    if user_input.lower() in ["exit", "quit"]:
        break

    result = agent.invoke({
        "messages": [("user", user_input)]
    })

    # Get the last message from the model
    for message in reversed(result["messages"]):
        if hasattr(message, "type") and message.type == "ai" and message.content:
            print("\nAI:", message.content)
            break
    print()

