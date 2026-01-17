import api from '@common/utils/axiosetup';

// Type definitions
interface SystemSettingsPayload {
  siteName?: string;
  siteDescription?: string;
  maintenanceMode?: boolean;
  allowRegistration?: boolean;
  defaultUserRole?: string;
  sessionTimeout?: number;
  maxFileSize?: number;
  emailNotifications?: boolean;
  smsNotifications?: boolean;
  backupFrequency?: string;
  logLevel?: string;
}

interface LogExportParams {
  level?: string;
  module?: string;
  search?: string;
  start?: string;
  end?: string;
}

// System Settings
export const getSystemSettings = () => api.get('/system/settings/');
export const updateSystemSettings = (payload: SystemSettingsPayload) => api.put('/system/settings/', payload);

// System Logs
export const getSystemLogs = (params: {
  level?: string;
  module?: string;
  search?: string;
  start?: string;
  end?: string;
  page?: number;
  page_size?: number;
}) => api.get('/system/logs/', { params });

export const exportSystemLogs = (params: LogExportParams) =>
  api.get('/system/logs/export/', { params, responseType: 'blob' });

// Backups
export const listBackups = () => api.get('/system/backups/');
export const createBackup = (payload: { name: string; type: 'full' | 'incremental' | 'differential'; description?: string }) =>
  api.post('/system/backups/', payload);
export const deleteBackup = (id: string | number) => api.delete(`/system/backups/${id}/`);
export const restoreBackup = (id: string | number) => api.post(`/system/backups/${id}/restore/`);
export const downloadBackup = (id: string | number) => api.get(`/system/backups/${id}/download/`, { responseType: 'blob' });
export const uploadBackup = (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/system/backups/upload/', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
};