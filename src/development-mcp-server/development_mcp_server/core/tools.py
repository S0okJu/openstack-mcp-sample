from typing import Optional
from fastmcp import Context

from development_mcp_server.core.data import read_markdown, DevelopmentRule


async def analyze_code_secure(code: str, ctx: Context) -> str:
    """
    Analyze code from predefined security rules.
    
    Args:
        code: The code to analyze
        ctx: Context object for logging and sampling
        
    Returns:
        str: Analysis result or error message
    """
    try:
        rule = read_markdown(DevelopmentRule.SECURITY)
        
        # https://gofastmcp.com/servers/logging
        # await ctx.info(f"Analyze rule:{len(rule)}")
        
        # Use LLM Sampling. It is useful when tools need to leverage the LLM capabilities.
        # https://gofastmcp.com/servers/sampling

        # A system prompt is a set of overarching instructions that define how the AI should behave across all interactions. 
        # If the user prompt is the “what,” the system prompt is the "how" and "why" behind the AI's responses. 
        # System prompts are typically set once and remain consistent unless you decide to change the AI's overall behavior or role. 
        # They're like the job description and guidelines you give to your AI assistant.
        # https://www.regie.ai/blog/user-prompts-vs-system-prompts
        response = await ctx.sample(
            messages=f"'You should analyze the code following the security rule: {code}'.",
            system_prompt=f"""You are a OpenStack software Developer.
                You must follow this predefined rule: {rule}
                If you find the problem, solve it"""
        )
        return response.text
    except RuntimeError as e:
        return str(e)
    except Exception as e:
        return str(e)
        

    
    
    