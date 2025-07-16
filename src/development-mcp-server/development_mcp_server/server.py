from mcp.server.fastmcp import FastMCP

from development_mcp_server.core import resources, tools

mcp = FastMCP(
    'OpenStack Development MCP Server',
)

mcp.resource(
    uri='resource://security-rules',
    name= 'SecurityRules',
    description='This is a security rules.'
    )(resources.get_security_rules)

mcp.tool(
    name = 'analyze_code_secure',
    description= 'Analyze code from predefined security rules'
)(tools.analyze_code_secure)


if __name__ == '__main__':
    mcp.run()