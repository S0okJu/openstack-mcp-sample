from development_mcp_server.core.data import (
    read_markdown, DevelopmentRule
)

async def get_security_rules():
    """Provide security rules if you """
    return read_markdown(DevelopmentRule.SECURITY)
    
