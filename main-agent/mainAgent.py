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


def mainAgent(query: str) -> dict:
    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    messages.append(HumanMessage(content=query))

    llm = get_llm_with_tools()

    # Build tool lookup map
    tool_map = {t.name: t for t in ALL_TOOLS}

    tools_used = []
    max_iterations = 10

    for i in range(max_iterations):
        response = llm.invoke(messages)
        messages.append(response)

        # No tool calls means the agent is done
        if not response.tool_calls:
            break

        # Execute each tool call
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

    return {
        "response": response.content,
    }