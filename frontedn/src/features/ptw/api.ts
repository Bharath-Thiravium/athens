import api from '@common/utils/axiosetup';
import * as Types from './types';

const API_URL = '/api/v1/ptw';  // Update the API URL to match the backend

// Permit Types
export const getPermitTypes = () => 
  api.get<Types.PermitType[]>(`${API_URL}/permit-types/`);

export const getPermitType = (id: number) => 
  api.get<Types.PermitType>(`${API_URL}/permit-types/${id}/`);

// Permits
export const getPermits = (params?: any) => 
  api.get<Types.Permit[]>(`${API_URL}/permits/`, { params });

export const getPermit = (id: number) => 
  api.get<Types.Permit>(`${API_URL}/permits/${id}/`);

export const createPermit = (data: Partial<Types.Permit>) => {
  console.log('API createPermit - data being sent:', data);
  console.log('API createPermit - permit_type:', data.permit_type, typeof data.permit_type);
  return api.post<Types.Permit>(`${API_URL}/permits/`, data);
};

export const updatePermit = (id: number, data: Partial<Types.Permit>) => 
  api.put<Types.Permit>(`${API_URL}/permits/${id}/`, data);

export const deletePermit = (id: number) => 
  api.delete(`${API_URL}/permits/${id}/`);

// Permit Actions
export const approvePermit = (id: number, comments?: string) => 
  api.post(`${API_URL}/permits/${id}/approve/`, { comments });

export const rejectPermit = (id: number, comments: string) => 
  api.post(`${API_URL}/permits/${id}/reject/`, { comments });

export const startWork = (id: number) => 
  api.post(`${API_URL}/permits/${id}/start/`);

export const completeWork = (id: number) => 
  api.post(`${API_URL}/permits/${id}/complete/`);

export const closePermit = (id: number) => 
  api.post(`${API_URL}/permits/${id}/close/`);

export const suspendPermit = (id: number, reason: string) => 
  api.post(`${API_URL}/permits/${id}/suspend/`, { reason });

export const resumePermit = (id: number) => 
  api.post(`${API_URL}/permits/${id}/resume/`);

export const cancelPermit = (id: number, reason: string) => 
  api.post(`${API_URL}/permits/${id}/cancel/`, { reason });

export const submitForApproval = (id: number) => 
  api.post(`${API_URL}/permits/${id}/submit_for_approval/`);

// Add new API endpoints for verification workflow
export const submitForVerification = (id: number) => 
  api.post(`${API_URL}/permits/${id}/submit_for_verification/`);

export const verifyPermit = (id: number, comments: string = '') => 
  api.post(`${API_URL}/permits/${id}/verify/`, { comments });

export const rejectVerification = (id: number, comments: string) => 
  api.post(`${API_URL}/permits/${id}/reject_verification/`, { comments });

// Permit Extensions
export const requestExtension = (data: {
  permit: number;
  new_end_time: string;
  reason: string;
}) => api.post(`${API_URL}/extensions/`, data);

export const approveExtension = (id: number, comments?: string) => 
  api.post(`${API_URL}/extensions/${id}/approve/`, { comments });

export const rejectExtension = (id: number, comments: string) => 
  api.post(`${API_URL}/extensions/${id}/reject/`, { comments });

// Workers
export const assignWorker = (permitId: number, workerId: number) => 
  api.post(`${API_URL}/permits/${permitId}/workers/`, { worker: workerId });

export const removeWorker = (permitId: number, workerId: number) => 
  api.delete(`${API_URL}/permits/${permitId}/workers/${workerId}/`);

// Permit Notifications
export const sendPermitNotification = (_userId: string | number, _permitId: number, _action: string) => {
  // Use the existing notification context to send notifications
  // This will be implemented in the components
  return true;
};

// Workflow API
export const initiateWorkflow = (permitId: number) => 
  api.post(`${API_URL}/permits/${permitId}/workflow/initiate/`);

export const assignVerifier = (permitId: number, data: { verifier_id: number }) => 
  api.post(`${API_URL}/permits/${permitId}/workflow/assign-verifier/`, data);

export const verifyPermitWorkflow = (permitId: number, data: {
  action: 'approve' | 'reject';
  comments?: string;
  approver_id?: number;
}) => api.post(`${API_URL}/permits/${permitId}/workflow/verify/`, data);

export const assignApprover = (permitId: number, data: { approver_id: number }) => 
  api.post(`${API_URL}/permits/${permitId}/workflow/assign-approver/`, data);

export const approvePermitWorkflow = (permitId: number, data: {
  action: 'approve' | 'reject';
  comments?: string;
}) => api.post(`${API_URL}/permits/${permitId}/workflow/approve/`, data);

export const getAvailableVerifiers = (params?: string) => 
  api.get(`${API_URL}/workflow/verifiers/?${params || ''}`);

export const getAvailableApprovers = (params?: string) => 
  api.get(`${API_URL}/workflow/approvers/?${params || ''}`);

export const getWorkflowStatus = (permitId: number) => 
  api.get(`${API_URL}/permits/${permitId}/workflow/status/`);

export const getMyWorkflowTasks = () => 
  api.get(`${API_URL}/workflow/my-tasks/`);

export const resubmitPermit = (permitId: number) => 
  api.post(`${API_URL}/permits/${permitId}/workflow/resubmit/`);

// Reports API
export const getPermitReports = (params: {
  report_type: string;
  start_date?: string;
  end_date?: string;
}) => api.get(`${API_URL}/reports/`, { params });

export const exportPermitReport = (params: {
  report_type: string;
  start_date?: string;
  end_date?: string;
  format: 'pdf' | 'excel';
}) => api.get(`${API_URL}/reports/export/`, {
  params,
  responseType: 'blob' // Important for file downloads
});







