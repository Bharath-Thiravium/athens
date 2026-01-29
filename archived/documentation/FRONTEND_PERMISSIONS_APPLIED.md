# Frontend Permission System Implementation

## ✅ Components Updated with Permission System

### 1. JobTraining ✅ (Reference Implementation)
- **File**: `frontedn/src/features/jobtraining/components/JobTrainingList.tsx`
- **Features**: Complete permission system with edit/delete buttons
- **Permission Flow**: AdminUser → Permission Request → ProjectAdmin Approval → 15-min window

### 2. InductionTraining ✅ (Updated)
- **File**: `frontedn/src/features/inductiontraining/components/InductionTrainingList.tsx`
- **Added**: 
  - `usePermissionControl` hook
  - Permission-aware edit handler
  - Permission-aware delete handler
  - `PermissionRequestModal` component

### 3. ToolboxTalk ✅ (Updated)
- **File**: `frontedn/src/features/toolboxtalk/components/ToolboxTalkList.tsx`
- **Added**:
  - `usePermissionControl` hook
  - Permission-aware edit handler
  - Permission-aware delete handler
  - `PermissionRequestModal` component

### 4. SafetyObservation ✅ (Already has permissions)
- **File**: `frontedn/src/features/safetyobservation/components/SafetyObservationList.tsx`
- **Status**: Already implemented with permission system

### 5. Worker ✅ (Already has permissions)
- **File**: `frontedn/src/features/worker/components/WorkerList.tsx`
- **Status**: Already implemented with permission system

## 🔄 Components Needing Updates

### 6. MOM (Minutes of Meeting)
- **File**: `frontedn/src/features/mom/components/MomList.tsx`
- **Needs**: Permission system integration

### 7. PTW (Permit to Work)
- **File**: `frontedn/src/features/ptw/components/PermitList.tsx`
- **Needs**: Permission system integration

### 8. Incident Management
- **File**: `frontedn/src/features/incidentmanagement/components/IncidentList.tsx`
- **Needs**: Permission system integration

### 9. Manpower
- **File**: `frontedn/src/features/manpower/components/ManpowerView.tsx`
- **Needs**: Permission system integration

## 🛠️ Implementation Pattern

Each component follows this pattern:

### 1. Imports
```typescript
import { usePermissionControl } from '../../../hooks/usePermissionControl';
import PermissionRequestModal from '../../../components/permissions/PermissionRequestModal';
```

### 2. Hook Setup
```typescript
const { django_user_type } = useAuthStore();
const { executeWithPermission, showPermissionModal, permissionRequest, closePermissionModal, onPermissionRequestSuccess } = usePermissionControl({
  onPermissionGranted: () => fetchData()
});
```

### 3. Edit Handler
```typescript
const handleEdit = async (record) => {
  if (django_user_type !== 'adminuser') {
    setEditingItem(record);
    return;
  }
  
  try {
    const response = await api.get('/api/v1/permissions/check/', {
      params: {
        permission_type: 'edit',
        object_id: record.id,
        app_label: 'module_name',
        model: 'model_name'
      }
    });
    
    if (response.data.has_permission) {
      setEditingItem(record);
    } else {
      executeWithPermission(
        () => api.patch(`/endpoint/${record.id}/`, {}),
        'edit item'
      ).then(() => setEditingItem(record));
    }
  } catch (error) {
    executeWithPermission(
      () => api.patch(`/endpoint/${record.id}/`, {}),
      'edit item'
    ).then(() => setEditingItem(record));
  }
};
```

### 4. Delete Handler
```typescript
const handleDelete = async (record) => {
  if (django_user_type === 'adminuser') {
    try {
      const response = await api.get('/api/v1/permissions/check/', {
        params: {
          permission_type: 'delete',
          object_id: record.id,
          app_label: 'module_name',
          model: 'model_name'
        }
      });
      
      if (response.data.has_permission) {
        await api.delete(`/endpoint/${record.id}/`);
      } else {
        await executeWithPermission(
          () => api.delete(`/endpoint/${record.id}/`),
          'delete item'
        );
      }
    } catch (permError) {
      await executeWithPermission(
        () => api.delete(`/endpoint/${record.id}/`),
        'delete item'
      );
    }
  } else {
    await api.delete(`/endpoint/${record.id}/`);
  }
};
```

### 5. Permission Modal
```typescript
{showPermissionModal && permissionRequest && (
  <PermissionRequestModal
    visible={showPermissionModal}
    onCancel={closePermissionModal}
    onSuccess={onPermissionRequestSuccess}
    permissionType={permissionRequest.permissionType}
    objectId={permissionRequest.objectId}
    contentType={permissionRequest.contentType}
    objectName={permissionRequest.objectName}
  />
)}
```

## 🎯 Next Steps

To complete the frontend permission system:

1. **Update MomList.tsx** with permission system
2. **Update PermitList.tsx** with permission system  
3. **Update IncidentList.tsx** with permission system
4. **Update ManpowerView.tsx** with permission system

## 🔧 Key Features Implemented

- **Permission-aware Edit/Delete buttons**
- **Real-time permission checking**
- **Graceful fallback to permission request flow**
- **User-friendly permission request modals**
- **Automatic refresh after permission granted**
- **Consistent UI/UX across all components**

## 📋 Module Mapping

| Component | App Label | Model Name | Endpoint |
|-----------|-----------|------------|----------|
| JobTraining | jobtraining | jobtraining | /jobtraining/ |
| InductionTraining | inductiontraining | inductiontraining | /induction/ |
| ToolboxTalk | tbt | toolboxtalk | /tbt/ |
| SafetyObservation | safetyobservation | safetyobservation | /safety-observations/ |
| Worker | worker | worker | /workers/ |
| MOM | mom | mom | /mom/ |
| PTW | ptw | permit | /permits/ |
| Incident | incidentmanagement | incident | /incidents/ |

## 🎉 Result

The permission system is now consistently applied across the major frontend components, providing:

- **Secure access control** for AdminUsers
- **Seamless user experience** with modal-based permission requests
- **Complete audit trail** of all permission requests and approvals
- **Time-limited permissions** (15 minutes) for security
- **Consistent UI patterns** across all modules
