from typing import Optional
import openstack 

def connect_openstack() -> Optional[openstack.connection.Connection]:
    return openstack.connect()