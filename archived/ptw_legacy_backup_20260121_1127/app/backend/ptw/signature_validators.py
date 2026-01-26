"""
Digital signature validation for PTW workflow enforcement.
Ensures signatures are present before critical workflow transitions.
"""
from rest_framework import serializers
from .models import DigitalSignature


def validate_required_signatures_for_action(permit, action, user):
    """
    Validate required signatures are present before workflow actions.
    
    Args:
        permit: Permit instance
        action: 'initiate_workflow', 'verify', or 'approve'
        user: Current user performing the action
    
    Raises:
        serializers.ValidationError with signature requirements
    """
    errors = {}
    
    if action == 'initiate_workflow':
        # Requestor signature required to submit/initiate workflow
        requestor_signature = DigitalSignature.objects.filter(
            permit=permit,
            signature_type='requestor',
            signatory=permit.created_by,
            signature_data__isnull=False
        ).exclude(signature_data='').first()
        
        if not requestor_signature:
            errors['signature'] = {
                'required': ['requestor'],
                'missing': ['requestor'],
                'message': 'Requestor digital signature is required before submitting.'
            }
    
    elif action == 'verify':
        # Verifier signature required to verify permit
        if not permit.verifier:
            errors['signature'] = {
                'required': ['verifier'],
                'missing': ['verifier'],
                'message': 'No verifier assigned to this permit.'
            }
        else:
            verifier_signature = DigitalSignature.objects.filter(
                permit=permit,
                signature_type='verifier',
                signatory=permit.verifier,
                signature_data__isnull=False
            ).exclude(signature_data='').first()
            
            if not verifier_signature:
                errors['signature'] = {
                    'required': ['verifier'],
                    'missing': ['verifier'],
                    'message': 'Verifier digital signature is required before verification.'
                }
    
    elif action == 'approve':
        # Approver signature required to approve permit
        approver = permit.approver or permit.approved_by
        if not approver:
            errors['signature'] = {
                'required': ['approver'],
                'missing': ['approver'],
                'message': 'No approver assigned to this permit.'
            }
        else:
            approver_signature = DigitalSignature.objects.filter(
                permit=permit,
                signature_type='approver',
                signatory=approver,
                signature_data__isnull=False
            ).exclude(signature_data='').first()
            
            if not approver_signature:
                errors['signature'] = {
                    'required': ['approver'],
                    'missing': ['approver'],
                    'message': 'Approver digital signature is required before approval.'
                }
    
    if errors:
        raise serializers.ValidationError(errors)


def validate_signature_authorization(permit, signature_type, user):
    """
    Validate user is authorized to create signature of given type.
    
    Args:
        permit: Permit instance
        signature_type: Type of signature being created
        user: User attempting to create signature
    
    Raises:
        serializers.ValidationError if unauthorized
    """
    authorized_users = {
        'requestor': permit.created_by_id,
        'verifier': permit.verifier_id,
        'approver': permit.approver_id or permit.approved_by_id,
        'issuer': permit.issuer_id,
        'receiver': permit.receiver_id,
    }
    
    if signature_type in authorized_users:
        required_user_id = authorized_users[signature_type]
        if not required_user_id:
            raise serializers.ValidationError({
                'signature_type': f'No assigned {signature_type} for this permit'
            })
        if user.id != required_user_id:
            raise serializers.ValidationError({
                'signature_type': f'Only the assigned {signature_type} can sign this permit'
            })