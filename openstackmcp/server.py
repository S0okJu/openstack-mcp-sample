from mcp.server.fastmcp import FastMCP
import tools
mcp = FastMCP('openstack-mcp-test')

def main():
    mcp.run()

if __name__ == "__main__":
    main()