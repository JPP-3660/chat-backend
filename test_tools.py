from app.services.tools import web_search, code_executor

print("Testing Web Search...")
try:
    result = web_search.invoke("stock price of nvidia")
    print(f"Search Result: {result[:200]}...")
except Exception as e:
    print(f"Search Failed: {e}")

print("\nTesting Code Executor...")
try:
    result = code_executor.invoke("print(2 + 2)")
    print(f"Code Execution Result: {result}")
except Exception as e:
    print(f"Code Executor Failed: {e}")
