from openstack import connection

conn = connection.Connection(
    region_name='example-region',
    auth={
        'auth_url': 'https://auth.example.com',
        'username': 'amazing-user',
        'password': 'super-secret-password',
        'project_id': '33aa1afc-03fe-43b8-8201-4e0d3b4b8ab5',
        'user_domain_id': '054abd68-9ad9-418b-96d3-3437bb376703',
    },
    compute_api_version='2',
    identity_interface='internal',
)