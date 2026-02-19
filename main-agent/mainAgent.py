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


def mainAgent(query: str, history: list = None) -> dict:
    """
    query: user input string
    history: list of dicts, each with {"role": "user"|"assistant", "content": ...}
    """
    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    if history:
        for turn in history:
            if turn["role"] == "user":
                messages.append(HumanMessage(content=turn["content"]))
            elif turn["role"] == "assistant":
                messages.append(AIMessage(content=turn["content"]))
    messages.append(HumanMessage(content=query))

    llm = get_llm_with_tools()
    tool_map = {t.name: t for t in ALL_TOOLS}
    tools_used = []
    max_iterations = 10

    for i in range(max_iterations):
        response = llm.invoke(messages)
        messages.append(response)
        if not response.tool_calls:
            break
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            print(f"[Tool Call] {tool_name}({tool_args})")
            tool_fn = tool_map.get(tool_name)
            if not tool_fn:
                result = f"Error: Tool '{tool_name}' not found"
            else:
                try:
                    result = tool_fn.invoke(tool_args)
                except Exception as e:
                    result = f"Error: {str(e)}"
            tools_used.append({"tool": tool_name, "args": tool_args, "result": result})
            messages.append(ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"],
            ))

    # Build new history for next turn
    new_history = []
    for m in messages:
        if isinstance(m, HumanMessage):
            new_history.append({"role": "user", "content": m.content})
        elif isinstance(m, AIMessage):
            new_history.append({"role": "assistant", "content": m.content})

    return {
        "response": response.content,
        "history": new_history,
    }