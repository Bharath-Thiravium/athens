import * as ptwAPI from '../features/ptw/api';

// Re-export all PTW API functions for centralized access
export const {
  // Permit Types
  getPermitTypes,
  getPermitType,
  
  // Permits
  getPermits,
  getPermit,
  createPermit,
  updatePermit,
  deletePermit,
  
  // Permit Actions
  approvePermit,
  rejectPermit,
  startWork,
  completeWork,
  closePermit,
  suspendPermit,
  resumePermit,
  cancelPermit,
  submitForApproval,
  submitForVerification,
  verifyPermit,
  rejectVerification,
  
  // Workflow API
  initiateWorkflow,
  assignVerifier,
  verifyPermitWorkflow,
  assignApprover,
  approvePermitWorkflow,
  getAvailableVerifiers,
  getAvailableApprovers,
  getWorkflowStatus,
  getMyWorkflowTasks,
  resubmitPermit,
  
  // Extensions
  requestExtension,
  approveExtension,
  rejectExtension,
  
  // Workers
  assignWorker,
  removeWorker,
  
  // Reports
  getPermitReports,
  exportPermitReport,
  
  // Notifications
  sendPermitNotification
} = ptwAPI;

export default {
  ...ptwAPI,
  verifyPermit: ptwAPI.verifyPermitWorkflow,
  approvePermit: ptwAPI.approvePermitWorkflow
};