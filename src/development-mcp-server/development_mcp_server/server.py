from mcp.server.fastmcp import FastMCP

from development_mcp_server.core.resources import get_security_rules
from development_mcp_server.core.tools import analyze_code_secure


mcp = FastMCP(
    'OpenStack Development MCP Server',
)

mcp.resource(
    uri='resource://security-rules',
    name= 'SecurityRules',
    description='This is ...'
    )(get_security_rules)

mcp.tool(
    name = 'analyze_code_secure',
    description= 'Analyze code from predefined security rules'
)(analyze_code_secure)



if __name__ == '__main__':
    mcp.run()