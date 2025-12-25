import sys
import os

# Add the backend directory to sys.path so we can import app modules
sys.path.append(os.getcwd())

try:
    from app.services.llm import LLMService, llm_service
    from app.core.config import settings
    
    print(f"OLLAMA_BASE_URL: {settings.OLLAMA_BASE_URL}")
    print(f"Default Model: {llm_service.default_model}")
    
    # Try to instantiate a model
    llm = llm_service.get_llm()
    print(f"LLM Instance: {type(llm)}")
    
    print("Verification Successful!")
except Exception as e:
    print(f"Verification Failed: {e}")
    import traceback
    traceback.print_exc()
