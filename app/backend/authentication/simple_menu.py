from django.http import JsonResponse

def simple_menu_data(request):
    return JsonResponse({
        'projects': [
            {'id': 1, 'name': 'Test Project 1', 'projectName': 'Test Project 1'},
            {'id': 2, 'name': 'Test Project 2', 'projectName': 'Test Project 2'}
        ],
        'categories': [
            {
                'id': 1,
                'name': 'Dashboard',
                'modules': [
                    {'id': 1, 'name': 'Main Dashboard', 'description': 'System dashboard', 'is_active': True}
                ]
            },
            {
                'id': 2, 
                'name': 'Safety Management',
                'modules': [
                    {'id': 2, 'name': 'Safety Observation', 'description': 'Safety reports', 'is_active': True},
                    {'id': 3, 'name': 'Incident Management', 'description': 'Incident tracking', 'is_active': True}
                ]
            }
        ]
    })