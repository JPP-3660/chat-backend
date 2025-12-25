from typing import List, Dict, Any, Generator
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.models.agent import Agent
from app.core.config import settings
import os
from app.services.tools import get_tools_for_agent

# You would load API key from settings/env
# os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY 

import logging

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        # Default fallback
        self.default_model = "llama3"

    def get_llm(self, model_config: Dict[str, Any] = {}):
        model_name = model_config.get("model", self.default_model)
        temperature = model_config.get("temperature", 0.7)
        return ChatOllama(
            base_url=settings.OLLAMA_BASE_URL,
            model=model_name, 
            temperature=temperature,
        )

    async def chat_stream(
        self, 
        agent: Agent, 
        history: List[Dict[str, str]], 
        user_input: str
    ) -> Generator[str, None, None]:
        
        llm = self.get_llm(agent.model_config_data)
        
        # Tools disabled for stability debugging
        # tools = get_tools_for_agent(agent.tools_config or [])
        # if tools:
        #     llm = llm.bind_tools(tools)
        
        # Construct messages
        messages = []
        if agent.system_prompt:
            messages.append(SystemMessage(content=agent.system_prompt))
            
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        
        messages.append(HumanMessage(content=user_input))
        
        # Stream response
        try:
            logger.info(f"Stream start for {agent.name}")
            yield " " # Keep-alive
            async for chunk in llm.astream(messages):
                if chunk.content:
                    yield chunk.content
        except Exception as e:
            logger.error(f"Error during streaming: {str(e)}", exc_info=True)
            yield f"\n\n**Error:** {str(e)}\n\nPlease check your API Key configuration."

llm_service = LLMService()
