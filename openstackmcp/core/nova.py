from typing import List, Dict, Any 
import openstack 

def list_servers(conn:openstack.connect.Connection) -> List[Dict[str, Any]]:
    """Get nova server lists and return results"""
    try:
        
        # 서버 목록 가져오기
        servers = conn.compute.servers()
        
        results = []
        for server in servers:
            server_info = {
                'id': server.id,
                'name': server.name,
                'status': server.status,
                'created_at': server.created_at,
                'updated_at': server.updated_at,
            } 
            
            # 선택적 필드들 - 존재하는 경우에만 추가
            if hasattr(server, 'image') and server.image:
                server_info['image_id'] = server.image.get('id') if isinstance(server.image, dict) else server.image
            
            if hasattr(server, 'flavor') and server.flavor:
                server_info['flavor_id'] = server.flavor.get('id') if isinstance(server.flavor, dict) else server.flavor
            
            if hasattr(server, 'addresses') and server.addresses:
                server_info['networks'] = server.addresses
            
            if hasattr(server, 'security_groups') and server.security_groups:
                server_info['security_groups'] = server.security_groups
            
            if hasattr(server, 'key_name') and server.key_name:
                server_info['key_name'] = server.key_name
                
            if hasattr(server, 'availability_zone') and server.availability_zone:
                server_info['availability_zone'] = server.availability_zone
            
            results.append(server_info)
            
        return results
        
    except Exception as e:
        raise Exception(f"Failed to list servers: {str(e)}")