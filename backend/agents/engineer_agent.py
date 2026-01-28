"""
Engineer Agent - The Autonomous Developer.
Uses FileSystem and Terminal tools to analyze and update the codebase.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import json

from ..services.llm_service import llm_service
from ..tools.filesystem import filesystem
from ..tools.terminal import terminal

class AgentResponse(BaseModel):
    response: str
    metadata: Dict[str, Any] = {}

class EngineerAgent:
    """
    Autonomous Developer Agent.
    Can read files, write code, and run commands.
    """
    
    def __init__(self):
        self.system_prompt = """
        You are 'The Engineer', an advanced AI developer agent.
        Your goal is to help the user build, debug, and fix their project.
        
        Capabilities:
        1. Explore Key Files: Use filesystem.list_dir() and read_file().
        2. Analyze Code: Understand the context before changing it.
        3. Modify Code: Use write_file() to update code.
        4. Run Commands: Use terminal.run_command() to run tests/linters.
        
        Guidelines:
        - SAFETY FIRST: Do not delete critical files without confirmation.
        - VERIFY: Run tests after changes if possible.
        - EXPLAIN: Tell the user exactly what you changed.
        
        You have access to a 'tools' dictionary in the context with:
        - 'filesystem': instance
        - 'terminal': instance
        
        To use a tool, output a JSON block like:
        ```json
        {
            "tool": "filesystem",
            "action": "read_file",
            "args": {"path": "backend/api/main.py"}
        }
        ```
        If no tool is needed, just reply with text.
        """

    async def process(self, message: str, context: Dict[str, Any] = None) -> AgentResponse:
        """
        Process user message, potentially calling tools.
        """
        # Simple ReAct Loop (Think -> Act -> Observe)
        # For MVP, we'll do: LLM -> Single Tool Call -> LLM Summary
        
        history = context.get("history", [])
        
        # 1. PLAN: Ask LLM what to do
        prompt = f"User Request: {message}\n\nProject History: {history[-3:]}\n\nWhat is the next step? Return a JSON tool call if needed, or a text response."
        
        llm_response = await llm_service.generate(
            prompt=prompt,
            system_prompt=self.system_prompt,
            temperature=0.2 # Low temp for precise tool usage
        )
        
        content = llm_response.content
        tool_result = None
        executed_tool = False
        
        # 2. ACT: Check for tool calls (Naive parsing for MVP)
        # Look for ```json ... ``` blocks
        if "```json" in content:
            try:
                json_str = content.split("```json")[1].split("```")[0].strip()
                tool_call = json.loads(json_str)
                
                tool_name = tool_call.get("tool")
                action = tool_call.get("action")
                args = tool_call.get("args", {})
                
                if tool_name == "filesystem":
                    if action == "list_dir":
                        tool_result = await filesystem.list_dir(**args)
                    elif action == "read_file":
                        tool_result = await filesystem.read_file(**args)
                    elif action == "write_file":
                        tool_result = await filesystem.write_file(**args)
                        
                elif tool_name == "terminal":
                    if action == "run_command":
                        tool_result = await terminal.run_command(**args)
                
                executed_tool = True
                
            except Exception as e:
                tool_result = f"Tool Execution Error: {str(e)}"
        
        # 3. OBSERVE & RESPOND
        if executed_tool:
            # Final summary pass
            summary_prompt = f"User Request: {message}\nTool Action: {content}\nTool Result: {str(tool_result)[:2000]}\n\nExplain what you did and the result to the user."
            final_res = await llm_service.generate(
                prompt=summary_prompt,
                system_prompt=self.system_prompt
            )
            return AgentResponse(
                response=final_res.content,
                metadata={"tool_used": True, "result": str(tool_result)[:500]}
            )
        
        return AgentResponse(
            response=content,
            metadata={"tool_used": False}
        )

# Singleton
engineer_agent = EngineerAgent()
