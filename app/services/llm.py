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
        
        # Enable tools if configured
        tools = get_tools_for_agent(agent.tools_config or [])
        if tools:
            llm = llm.bind_tools(tools)
        
        # Construct initial messages
        messages = []
        if agent.system_prompt:
            messages.append(SystemMessage(content=agent.system_prompt))
            
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        
        messages.append(HumanMessage(content=user_input))
        
        try:
            logger.info(f"Stream start for {agent.name}")
            yield " " # Keep-alive
            
            # Simple tool loop
            max_iterations = 5
            for _ in range(max_iterations):
                response_message = None
                content_yielded = False
                
                async for chunk in llm.astream(messages):
                    if response_message is None:
                        response_message = chunk
                    else:
                        response_message += chunk
                    
                    if chunk.content:
                        yield chunk.content
                        content_yielded = True
                
                messages.append(response_message)
                
                if not response_message.tool_calls:
                    break
                
                # Execute tools
                for tool_call in response_message.tool_calls:
                    tool_name = tool_call["name"].lower()
                    tool_args = tool_call["args"]
                    
                    # Yield status update for frontend
                    yield f"[STATUS: {tool_name}]"
                    
                    # Find the tool function
                    selected_tool = next((t for t in tools if t.name == tool_name), None)
                    if selected_tool:
                        logger.info(f"Executing tool: {tool_name} with {tool_args}")
                        tool_result = await selected_tool.ainvoke(tool_args)
                        
                        # Handle specific tool output for sources
                        display_result = tool_result
                        if tool_name == "web_search":
                            try:
                                results = json.loads(tool_result)
                                # Yield sources to frontend
                                yield f"[SOURCES: {json.dumps(results)}]"
                                # Format simplified version for LLM
                                display_result = "\n\n".join([
                                    f"Source: {r.get('title')}\nLink: {r.get('link')}\nSnippet: {r.get('snippet')}"
                                    for r in results
                                ])
                            except:
                                pass

                        messages.append(AIMessage(
                            content="",
                            tool_calls=[tool_call],
                            additional_kwargs={"tool_call_id": tool_call["id"]}
                        ))
                        messages.append(HumanMessage(content=f"Tool {tool_name} result: {display_result}"))
                    else:
                        messages.append(HumanMessage(content=f"Error: Tool {tool_name} not found."))
                
                # If we had tool calls, we continue the loop to let LLM process results
                
        except Exception as e:
            logger.error(f"Error during streaming: {str(e)}", exc_info=True)
            yield f"\n\n**Error:** {str(e)}\n\nPlease check your configuration."

llm_service = LLMService()
