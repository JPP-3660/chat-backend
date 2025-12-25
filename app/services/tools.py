from langchain_community.tools import DuckDuckGoSearchRun
from langchain_experimental.utilities import PythonREPL
from langchain_core.tools import tool

@tool
def calculator(expression: str) -> str:
    """Calculate the result of a mathematical expression."""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def web_search(query: str) -> str:
    """Search the web for information using DuckDuckGo."""
    try:
        search = DuckDuckGoSearchRun()
        return search.invoke(query)
    except Exception as e:
        return f"Search failed: {str(e)}"

@tool
def code_executor(code: str) -> str:
    """Execute Python code and return the output. Use this for complex calculations or data processing."""
    try:
        repl = PythonREPL()
        return repl.run(code)
    except Exception as e:
        return f"Execution failed: {str(e)}"

def get_tools_for_agent(tools_config: list) -> list:
    tools = []
    if "calculator" in tools_config:
        tools.append(calculator)
    if "web_search" in tools_config:
        tools.append(web_search)
    if "code_executor" in tools_config:
        tools.append(code_executor)
    return tools
