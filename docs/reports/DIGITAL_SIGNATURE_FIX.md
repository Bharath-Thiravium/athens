# Digital Signature Template Fix

## Problem
The digital signature template was showing "Complete Your Profile First" with all fields showing "Not set" even when user profile data was available.

## Root Cause
The `/authentication/signature/template/data/` endpoint was not properly implemented to fetch user profile data from the database.

## Solution Implemented

### 1. Enhanced Signature Template Data Endpoint
**File**: `/var/www/athens/backend/authentication/signature_views.py`

**Changes Made**:
- Implemented proper user data fetching logic based on user type
- Added support for different user types (master, projectadmin, adminuser)
- Added company logo detection based on user hierarchy
- Added proper error handling and fallback values

**Key Features**:
- **User Data Fetching**: Gets full name, designation, and company name from appropriate models
- **Logo Detection**: Fetches company logos based on user type hierarchy:
  - Master admin: From CompanyDetail
  - EPC users: Inherit from master admin's CompanyDetail
  - Client/Contractor: From AdminDetail
- **Template Status**: Checks if signature template already exists
- **Validation**: Identifies missing required fields

### 2. Added Missing Endpoints
**New Endpoints Added**:
```python
# Preview existing signature template
GET /authentication/signature/template/preview/

# Create new signature template
POST /authentication/signature/template/create/
```

### 3. Fixed Server Errors
**Issues Fixed**:
- Removed problematic import that was causing server crashes
- Added proper API decorators to authentication views
- Simplified template creation to avoid import dependencies

## API Response Structure

### Template Data Response
```json
{
  "can_create_template": true,
  "missing_fields": [],
  "user_data": {
    "full_name": "John Smith",
    "designation": "Safety Engineer", 
    "company_name": "ABC Company",
    "has_company_logo": true,
    "logo_url": "http://example.com/media/logos/logo.png"
  },
  "has_existing_template": false,
  "template_data": null
}
```

### Error Response
```json
{
  "can_create_template": false,
  "missing_fields": ["Full Name", "Designation"],
  "user_data": {
    "full_name": "Not set",
    "designation": "Not set", 
    "company_name": "Not set",
    "has_company_logo": false,
    "logo_url": null
  },
  "has_existing_template": false,
  "template_data": null
}
```

## User Type Hierarchy

### Data Source Priority:
1. **Master Admin**: CompanyDetail model
2. **EPC Users**: Inherit from Master Admin's CompanyDetail
3. **Project Admins (Client/Contractor)**: AdminDetail model
4. **Admin Users**: UserDetail model + inherit from creator

### Logo Inheritance:
- **EPC users** automatically inherit company logo from master admin
- **Client/Contractor users** use their own uploaded logos
- **Admin users** inherit from their creator's logo

## Testing

### Endpoints Working:
- ✅ `GET /authentication/signature/template/data/` - Returns proper user data
- ✅ `GET /authentication/signature/template/preview/` - Returns template preview URL
- ✅ `POST /authentication/signature/template/create/` - Creates signature template
- ✅ Server restart successful without errors

### Expected Behavior:
1. **Complete Profile Users**: Will see "Digital Signature Template Ready" message
2. **Incomplete Profile Users**: Will see specific missing fields listed
3. **Template Preview**: Available for users with existing templates
4. **Automatic Creation**: Templates created when profile is saved

## Frontend Integration

The frontend `DigitalSignatureTemplate.tsx` component will now receive proper user data and can:
- Display actual user information instead of "Not set"
- Show appropriate status messages based on profile completeness
- Enable template creation for users with complete profiles
- Display template previews for existing templates

## Files Modified

1. `/var/www/athens/backend/authentication/signature_views.py` - Enhanced endpoint implementation
2. `/var/www/athens/backend/authentication/urls.py` - Added new endpoint routes  
3. `/var/www/athens/backend/authentication/views.py` - Fixed server errors

## Result

The digital signature template now properly:
- ✅ Fetches user profile data from database
- ✅ Shows actual user information instead of "Not set"
- ✅ Determines template creation eligibility accurately
- ✅ Provides proper error messages for missing data
- ✅ Supports all user types in the system hierarchy