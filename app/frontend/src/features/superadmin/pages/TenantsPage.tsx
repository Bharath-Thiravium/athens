import React, { useEffect, useState } from 'react';
import { Button, Card, Checkbox, Form, Input, Modal, Select, Space, Table, Tag, Typography, message } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import {
  createTenant,
  deleteTenant,
  fetchTenants,
  fetchTenantModules,
  reactivateTenant,
  suspendTenant,
  syncTenant,
  updateTenantModules,
  updateTenant,
} from '../services/saasApi';

interface Tenant {
  id: string;
  name: string;
  display_name?: string;
  status: string;
}

const TenantsPage: React.FC = () => {
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingTenant, setEditingTenant] = useState<Tenant | null>(null);
  const [form] = Form.useForm<Tenant>();
  const [modulesVisible, setModulesVisible] = useState(false);
  const [modulesLoading, setModulesLoading] = useState(false);
  const [modulesTenant, setModulesTenant] = useState<Tenant | null>(null);
  const [availableModules, setAvailableModules] = useState<string[]>([]);
  const [selectedModules, setSelectedModules] = useState<string[]>([]);
  const [syncVisible, setSyncVisible] = useState(false);
  const [syncTenantTarget, setSyncTenantTarget] = useState<Tenant | null>(null);
  const [syncForm] = Form.useForm();

  const normalizeList = (data: any) => {
    if (Array.isArray(data)) return data;
    if (Array.isArray(data?.results)) return data.results;
    return [];
  };

  const load = async () => {
    setLoading(true);
    try {
      const data = await fetchTenants();
      setTenants(normalizeList(data));
    } catch (err: any) {
      message.error('Failed to load tenants');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const openCreate = () => {
    setEditingTenant(null);
    form.resetFields();
    setModalVisible(true);
  };

  const openEdit = (tenant: Tenant) => {
    setEditingTenant(tenant);
    form.setFieldsValue(tenant);
    setModalVisible(true);
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      if (editingTenant) {
        await updateTenant(editingTenant.id, values);
        message.success('Tenant updated');
      } else {
        await createTenant(values);
        message.success('Tenant created');
      }
      setModalVisible(false);
      load();
    } catch (err: any) {
      message.error(err?.response?.data?.detail || 'Operation failed');
    }
  };

  const handleSuspend = async (tenant: Tenant) => {
    await suspendTenant(tenant.id);
    message.success('Tenant suspended');
    load();
  };

  const handleReactivate = async (tenant: Tenant) => {
    await reactivateTenant(tenant.id);
    message.success('Tenant reactivated');
    load();
  };

  const handleDelete = async (tenant: Tenant) => {
    Modal.confirm({
      title: 'Delete tenant?',
      content: 'This will permanently remove the tenant and its subscription data.',
      okText: 'Delete',
      okType: 'danger',
      onOk: async () => {
        await deleteTenant(tenant.id);
        message.success('Tenant deleted');
        load();
      },
    });
  };

  const openSync = (tenant: Tenant) => {
    setSyncTenantTarget(tenant);
    syncForm.setFieldsValue({
      tenant_name: tenant.display_name || tenant.name,
      master_admin_id: '',
      company_id: '',
    });
    setSyncVisible(true);
  };

  const handleSync = async () => {
    if (!syncTenantTarget) return;
    try {
      const values = await syncForm.validateFields();
      await syncTenant(syncTenantTarget.id, values);
      message.success('Tenant synced for module management');
      setSyncVisible(false);
    } catch (err: any) {
      message.error(err?.response?.data?.detail || 'Tenant sync failed');
    }
  };

  const openModules = async (tenant: Tenant) => {
    setModulesTenant(tenant);
    setModulesVisible(true);
    setModulesLoading(true);
    try {
      const data = await fetchTenantModules(tenant.id);
      setAvailableModules(Array.isArray(data?.available_modules) ? data.available_modules : []);
      setSelectedModules(Array.isArray(data?.enabled_modules) ? data.enabled_modules : []);
    } catch (err: any) {
      message.error(err?.response?.data?.detail || 'Failed to load tenant modules');
      setModulesVisible(false);
    } finally {
      setModulesLoading(false);
    }
  };

  const saveModules = async () => {
    if (!modulesTenant) return;
    setModulesLoading(true);
    try {
      await updateTenantModules(modulesTenant.id, selectedModules);
      message.success('Modules updated');
      setModulesVisible(false);
    } catch (err: any) {
      message.error(err?.response?.data?.detail || 'Failed to update modules');
    } finally {
      setModulesLoading(false);
    }
  };

  const formatModuleLabel = (moduleKey: string) =>
    moduleKey
      .replace(/_/g, ' ')
      .replace(/\b\w/g, (c) => c.toUpperCase());

  const tenantModuleCategories = [
    { key: 'dashboard', label: 'Dashboard & Core', modules: ['authentication'] },
    { key: 'safety', label: 'Safety Management', modules: ['safetyobservation', 'incidentmanagement', 'ptw', 'inspection'] },
    { key: 'training', label: 'Training & Development', modules: ['inductiontraining', 'jobtraining', 'tbt'] },
    { key: 'workforce', label: 'Workforce Management', modules: ['worker', 'manpower'] },
    { key: 'communication', label: 'Communication', modules: ['mom', 'voice_translator'] },
    { key: 'admin', label: 'System Administration', modules: ['permissions', 'system'] },
    { key: 'environment', label: 'Environment Management', modules: ['environment'] },
    { key: 'quality', label: 'Quality Management', modules: ['quality'] },
  ];

  const categorizedModules = tenantModuleCategories
    .map((category) => ({
      ...category,
      modules: category.modules.filter((moduleKey) => availableModules.includes(moduleKey)),
    }))
    .filter((category) => category.modules.length > 0);

  const categorizedModuleKeys = new Set(
    categorizedModules.flatMap((category) => category.modules)
  );
  const uncategorizedModules = availableModules.filter(
    (moduleKey) => !categorizedModuleKeys.has(moduleKey)
  );

  const columns: ColumnsType<Tenant> = [
    { title: 'Name', dataIndex: 'name', key: 'name' },
    { title: 'Display Name', dataIndex: 'display_name', key: 'display_name' },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const color = status === 'active' ? 'green' : status === 'disabled' ? 'red' : 'blue';
        return <Tag color={color}>{status}</Tag>;
      },
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button size="small" onClick={() => openEdit(record)}>
            Edit
          </Button>
          <Button size="small" onClick={() => openModules(record)}>
            Modules
          </Button>
          <Button size="small" onClick={() => openSync(record)}>
            Sync
          </Button>
          {record.status === 'active' ? (
            <Button danger size="small" onClick={() => handleSuspend(record)}>
              Suspend
            </Button>
          ) : (
            <Button type="primary" size="small" onClick={() => handleReactivate(record)}>
              Reactivate
            </Button>
          )}
          <Button danger size="small" onClick={() => handleDelete(record)}>
            Delete
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <Card
      title={
        <Space align="center">
          <Typography.Title level={4} style={{ margin: 0 }}>
            Tenants (Companies)
          </Typography.Title>
          <Button type="primary" onClick={openCreate}>
            New Tenant
          </Button>
        </Space>
      }
    >
      <Table
        rowKey="id"
        dataSource={Array.isArray(tenants) ? tenants : []}
        columns={columns}
        loading={loading}
        pagination={{ pageSize: 10 }}
      />

      <Modal
        open={modalVisible}
        title={editingTenant ? 'Edit Tenant' : 'Create Tenant'}
        onCancel={() => setModalVisible(false)}
        onOk={handleSubmit}
        okText={editingTenant ? 'Update' : 'Create'}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="Name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="display_name" label="Display Name">
            <Input />
          </Form.Item>
          <Form.Item name="status" label="Status" initialValue="active">
            <Select
              options={[
                { label: 'Active', value: 'active' },
                { label: 'Disabled', value: 'disabled' },
              ]}
            />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        open={modulesVisible}
        title={modulesTenant ? `Manage Modules: ${modulesTenant.display_name || modulesTenant.name}` : 'Manage Modules'}
        onCancel={() => setModulesVisible(false)}
        onOk={saveModules}
        okText="Save Modules"
        confirmLoading={modulesLoading}
      >
        <Typography.Paragraph className="text-color-text-muted">
          Select which modules are enabled for this tenant. Disabled modules will be blocked by tenant middleware.
        </Typography.Paragraph>
        <Checkbox.Group
          value={selectedModules}
          onChange={(values) => setSelectedModules(values as string[])}
          style={{ width: '100%' }}
        >
          <Space direction="vertical" style={{ width: '100%' }}>
            {categorizedModules.map((category) => (
              <div key={category.key} style={{ width: '100%' }}>
                <Typography.Text strong>{category.label}</Typography.Text>
                <Space direction="vertical" style={{ width: '100%', marginTop: 8, paddingLeft: 12 }}>
                  {category.modules.map((moduleKey) => (
                    <Checkbox key={moduleKey} value={moduleKey}>
                      {formatModuleLabel(moduleKey)}
                    </Checkbox>
                  ))}
                </Space>
              </div>
            ))}
            {uncategorizedModules.length > 0 && (
              <div style={{ width: '100%' }}>
                <Typography.Text strong>Other</Typography.Text>
                <Space direction="vertical" style={{ width: '100%', marginTop: 8, paddingLeft: 12 }}>
                  {uncategorizedModules.map((moduleKey) => (
                    <Checkbox key={moduleKey} value={moduleKey}>
                      {formatModuleLabel(moduleKey)}
                    </Checkbox>
                  ))}
                </Space>
              </div>
            )}
          </Space>
        </Checkbox.Group>
      </Modal>

      <Modal
        open={syncVisible}
        title={syncTenantTarget ? `Sync Tenant: ${syncTenantTarget.display_name || syncTenantTarget.name}` : 'Sync Tenant'}
        onCancel={() => setSyncVisible(false)}
        onOk={handleSync}
        okText="Sync Tenant"
      >
        <Typography.Paragraph className="text-color-text-muted">
          Create the AthensTenant record so modules can be managed. Master Admin ID must be a UUID.
        </Typography.Paragraph>
        <Form form={syncForm} layout="vertical">
          <Form.Item
            name="master_admin_id"
            label="Master Admin ID (UUID)"
            rules={[{ required: true, message: 'Master Admin ID is required' }]}
          >
            <Input placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" />
          </Form.Item>
          <Form.Item name="tenant_name" label="Tenant Name">
            <Input />
          </Form.Item>
          <Form.Item name="company_id" label="Company ID (UUID)">
            <Input placeholder="optional UUID" />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};

export default TenantsPage;
