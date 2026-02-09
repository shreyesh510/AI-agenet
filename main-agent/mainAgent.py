from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from prompts.system_prompt import SYSTEM_PROMPT
from langchain_openai import ChatOpenAI
import config
from tools import ALL_TOOLS



def get_llm_with_tools():
    """Create LLM instance with tools bound"""
    llm = ChatOpenAI(
        model=config.OPENAI_MODEL,
        temperature=0,
        api_key=config.OPENAI_API_KEY,
    )
    return llm.bind_tools(ALL_TOOLS)


def mainAgent(query: str) -> str:
    # Placeholder for the main agent logic
    # This function should process the query and return a response
    
    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    user_message = HumanMessage(content=query)
    messages.append(user_message)

      # Get LLM with tools
    llm = get_llm_with_tools()

    # Track tools used
    tools_used = []

    # Agent loop - process until no more tool calls
    max_iterations = 10
    iteration = 0


    return {"response": f"Processed query: {messages}"}