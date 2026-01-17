import api from '@common/utils/axiosetup';

export interface TenantPayload {
  name: string;
  display_name?: string;
  status?: string;
}

export interface MasterPayload {
  email: string;
  password?: string;
  tenant_id?: string;
  username?: string;
  is_active?: boolean;
}

export interface SubscriptionPayload {
  plan?: string;
  status?: string;
  seats?: number;
  current_period_start?: string | null;
  current_period_end?: string | null;
  renewal_at?: string | null;
  last_payment_at?: string | null;
  payment_provider?: string | null;
  notes?: string | null;
}

export interface SaaSSettingsPayload {
  platform_name: string;
  platform_url?: string;
  support_email?: string;
  support_phone?: string;
  logo_url?: string;
  primary_color?: string;
  email_from_name?: string;
  email_from_address?: string;
  email_reply_to?: string;
  billing_provider?: string;
  billing_mode?: string;
  invoice_footer?: string;
  session_timeout_minutes?: number;
  audit_retention_days?: number;
  allow_self_signup?: boolean;
  require_mfa?: boolean;
  maintenance_mode?: boolean;
  updated_at?: string;
}

export const fetchTenants = async () => {
  const { data } = await api.get('/api/saas/tenants/');
  return data;
};

export const createTenant = async (payload: TenantPayload) => {
  const { data } = await api.post('/api/saas/tenants/', payload);
  return data;
};

export const updateTenant = async (id: string, payload: Partial<TenantPayload>) => {
  const { data } = await api.patch(`/api/saas/tenants/${id}/`, payload);
  return data;
};

export const suspendTenant = async (id: string) => {
  const { data } = await api.post(`/api/saas/tenants/${id}/suspend/`);
  return data;
};

export const reactivateTenant = async (id: string) => {
  const { data } = await api.post(`/api/saas/tenants/${id}/reactivate/`);
  return data;
};

export const deleteTenant = async (id: string) => {
  const { data } = await api.delete(`/api/saas/tenants/${id}/`);
  return data;
};

export const fetchMasters = async () => {
  const { data } = await api.get('/api/saas/masters/');
  return data;
};

export const createMaster = async (payload: MasterPayload) => {
  const { data } = await api.post('/api/saas/masters/', payload);
  return data;
};

export const updateMaster = async (id: number, payload: Partial<MasterPayload>) => {
  const { data } = await api.patch(`/api/saas/masters/${id}/`, payload);
  return data;
};

export const deleteMaster = async (id: number) => {
  const { data } = await api.delete(`/api/saas/masters/${id}/`);
  return data;
};

export const fetchSubscription = async (tenantId: string) => {
  const { data } = await api.get(`/api/saas/tenants/${tenantId}/subscription/`);
  return data;
};

export const updateSubscription = async (tenantId: string, payload: SubscriptionPayload) => {
  const { data } = await api.patch(`/api/saas/tenants/${tenantId}/subscription/`, payload);
  return data;
};

export const fetchAuditLogs = async (params?: { tenant_id?: string; actor_id?: string }) => {
  const { data } = await api.get('/api/saas/audit-logs/', { params });
  return data;
};

export const fetchTenantModules = async (tenantId: string) => {
  const { data } = await api.get(`/api/saas/tenants/${tenantId}/modules`);
  return data;
};

export const updateTenantModules = async (tenantId: string, enabled_modules: string[]) => {
  const { data } = await api.patch(`/api/saas/tenants/${tenantId}/modules`, { enabled_modules });
  return data;
};

export const syncTenant = async (tenantId: string, payload: { master_admin_id: string; tenant_name?: string; company_id?: string }) => {
  const { data } = await api.post(`/api/saas/tenants/${tenantId}/sync`, payload);
  return data;
};

export const fetchSaasSettings = async () => {
  const { data } = await api.get('/api/saas/settings');
  return data;
};

export const updateSaasSettings = async (payload: Partial<SaaSSettingsPayload>) => {
  const { data } = await api.patch('/api/saas/settings', payload);
  return data;
};
