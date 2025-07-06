
from typing import List, Dict, Any
import json

from fastmcp import FastMCP
from openstackmcp.core.auth import connect_openstack

mcp = FastMCP('openstack-mcp-test')

class OpenStackMCP:
    def __init__(self, name='openstack-mcp'):
        self.server = FastMCP(name=mcp)
        self.conn = connect_openstack()
         
    def run(self):
        self.server.run()
    
    @self.server.tool()
    def nova_list(self) -> str:
        pass 

    
        

# if __name__ == "__main__":
#     mcp = OpenStackMCP()
#     mcp.run()