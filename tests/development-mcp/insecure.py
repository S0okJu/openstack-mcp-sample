
import openstack

def create_server(name, image, flavor):
    conn = openstack.connect()
    server = conn.compute.create_server(
        name=name,
        image_id=image,
        flavor_id=flavor
    )
    return server 
