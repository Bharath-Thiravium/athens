def _get_checklist_details(permit):
    """Get safety checklist details"""
    permit_type = permit.permit_type
    
    if not permit_type.safety_checklist:
        return {'required': [], 'missing': []}
    
    permit_checklist = permit.safety_checklist or {}
    missing = []
    required = []
    
    # Handle case where permit_checklist is a list instead of dict
    if isinstance(permit_checklist, list):
        # Convert list to dict for compatibility
        checklist_dict = {}
        for item in permit_checklist:
            if isinstance(item, str):
                checklist_dict[item] = True
            elif isinstance(item, dict) and 'key' in item:
                checklist_dict[item['key']] = item.get('checked', True)
        permit_checklist = checklist_dict
    
    if isinstance(permit_type.safety_checklist, list):
        for item in permit_type.safety_checklist:
            if isinstance(item, dict):
                key = item.get('key')
                label = item.get('label', key)
                is_required = item.get('required', True)
                
                if is_required:
                    required.append(label)
                    if not permit_checklist.get(key):
                        missing.append(label)
            elif isinstance(item, str):
                required.append(item)
                if not permit_checklist.get(item):
                    missing.append(item)
    
    return {
        'required': required,
        'missing': missing
    }