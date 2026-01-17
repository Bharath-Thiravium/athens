from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import CustomUser, UserDetail, AdminDetail, CompanyDetail

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def signature_template_data_safe(request):
    """Bulletproof signature template data endpoint"""
    try:
        user = request.user
        has_template = False
        template_data = None
        
        # Check for existing template
        if user.user_type == 'adminuser':
            try:
                user_detail = UserDetail.objects.get(user=user)
                if user_detail.signature_template:
                    has_template = True
                    template_data = user_detail.signature_template_data
            except UserDetail.DoesNotExist:
                pass
        elif user.user_type == 'projectadmin':
            try:
                admin_detail = AdminDetail.objects.get(user=user)
                if admin_detail.signature_template:
                    has_template = True
                    template_data = admin_detail.signature_template_data
            except AdminDetail.DoesNotExist:
                pass
        
        # Get user data safely
        full_name = f"{user.name or ''} {user.surname or ''}".strip() or user.username
        employee_id = 'Not set'
        signature_url = None
        
        # Get employee ID and signature URL from UserDetail if available
        if user.user_type == 'adminuser':
            try:
                user_detail = UserDetail.objects.get(user=user)
                employee_id = user_detail.employee_id or 'Not set'
                if user_detail.signature_template:
                    signature_url = user_detail.signature_template.url
            except UserDetail.DoesNotExist:
                pass
        elif user.user_type == 'projectadmin':
            try:
                admin_detail = AdminDetail.objects.get(user=user)
                if admin_detail.signature_template:
                    signature_url = admin_detail.signature_template.url
            except AdminDetail.DoesNotExist:
                pass
        
        user_data = {
            'full_name': full_name,
            'designation': user.designation or 'Not set',
            'company_name': user.company_name or 'Not set',
            'employee_id': employee_id,
            'has_company_logo': False,
            'logo_url': None
        }
        
        # Update template_data to include signature URL
        if signature_url:
            template_data = {'signature_url': signature_url}
            
        # Check missing fields
        missing_fields = []
        if user_data['full_name'] == user.username:
            missing_fields.append('Full Name')
        if user_data['designation'] == 'Not set':
            missing_fields.append('Designation')
        if user_data['company_name'] == 'Not set':
            missing_fields.append('Company Name')
            
        can_create_template = len(missing_fields) == 0
        
        return Response({
            'can_create_template': can_create_template,
            'missing_fields': missing_fields,
            'user_data': user_data,
            'has_existing_template': has_template,
            'template_data': template_data
        })
        
    except Exception:
        return Response({
            'can_create_template': False,
            'missing_fields': ['Complete Your Profile First'],
            'user_data': {
                'full_name': 'Not set',
                'designation': 'Not set',
                'company_name': 'Not set',
                'employee_id': 'Not set',
                'has_company_logo': False,
                'logo_url': None
            },
            'has_existing_template': False,
            'template_data': None
        })