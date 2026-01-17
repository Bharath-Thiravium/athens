import React, { useEffect, useState } from 'react';
import { Button, Card, Form, Input, Modal, Select, Space, Table, Tag, Typography, message } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { createMaster, deleteMaster, fetchMasters, fetchTenants, updateMaster } from '../services/saasApi';

interface TenantOption {
  id: string;
  name: string;
}

interface MasterRow {
  id: number;
  email: string;
  username?: string;
  athens_tenant_id?: string | null;
  tenant_name?: string | null;
  is_active?: boolean;
}

const MastersPage: React.FC = () => {
  const [masters, setMasters] = useState<MasterRow[]>([]);
  const [tenants, setTenants] = useState<TenantOption[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingMaster, setEditingMaster] = useState<MasterRow | null>(null);
  const [form] = Form.useForm();

  const normalizeList = (data: any) => {
    if (Array.isArray(data)) return data;
    if (Array.isArray(data?.results)) return data.results;
    return [];
  };

  const load = async () => {
    setLoading(true);
    try {
      const [masterData, tenantData] = await Promise.all([fetchMasters(), fetchTenants()]);
      const masterList = normalizeList(masterData);
      const tenantList = normalizeList(tenantData);
      setMasters(masterList);
      setTenants(tenantList.map((t: any) => ({ id: t.id, name: t.display_name || t.name })));
    } catch (err: any) {
      message.error('Failed to load masters');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const openCreate = () => {
    setEditingMaster(null);
    form.resetFields();
    setModalVisible(true);
  };

  const openEdit = (master: MasterRow) => {
    setEditingMaster(master);
    form.setFieldsValue({
      email: master.email,
      username: master.username,
      tenant_id: master.athens_tenant_id,
      is_active: master.is_active ?? true,
    });
    setModalVisible(true);
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      if (editingMaster) {
        const payload: any = {
          email: values.email,
          username: values.username || values.email,
          tenant_id: values.tenant_id,
          is_active: values.is_active,
        };
        if (values.password) {
          payload.password = values.password;
        }
        await updateMaster(editingMaster.id, payload);
        message.success('Master user updated');
      } else {
        await createMaster({
          email: values.email,
          password: values.password,
          tenant_id: values.tenant_id,
          username: values.username || values.email,
          is_active: values.is_active,
        });
        message.success('Master user created');
      }
      setModalVisible(false);
      load();
    } catch (err: any) {
      message.error(err?.response?.data?.detail || 'Operation failed');
    }
  };

  const handleDelete = async (master: MasterRow) => {
    Modal.confirm({
      title: 'Delete master user?',
      content: 'This will permanently remove the master user.',
      okText: 'Delete',
      okType: 'danger',
      onOk: async () => {
        await deleteMaster(master.id);
        message.success('Master user deleted');
        load();
      },
    });
  };

  const columns: ColumnsType<MasterRow> = [
    { title: 'Email', dataIndex: 'email', key: 'email' },
    { title: 'Username', dataIndex: 'username', key: 'username' },
    {
      title: 'Tenant',
      dataIndex: 'athens_tenant_id',
      key: 'athens_tenant_id',
      render: (_: any, record) => record.tenant_name || record.athens_tenant_id || '-',
    },
    {
      title: 'Status',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active: boolean) => <Tag color={active ? 'green' : 'red'}>{active ? 'Active' : 'Disabled'}</Tag>,
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record) => (
        <Space>
          <Button size="small" onClick={() => openEdit(record)}>
            Edit
          </Button>
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
            Master Users
          </Typography.Title>
          <Button type="primary" onClick={openCreate}>
            New Master
          </Button>
        </Space>
      }
    >
      <Table
        rowKey="id"
        dataSource={Array.isArray(masters) ? masters : []}
        columns={columns}
        loading={loading}
        pagination={{ pageSize: 10 }}
      />

      <Modal
        open={modalVisible}
        title={editingMaster ? 'Edit Master User' : 'Create Master User'}
        onCancel={() => setModalVisible(false)}
        onOk={handleSubmit}
        okText={editingMaster ? 'Update' : 'Create'}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="email" label="Email" rules={[{ required: true, type: 'email' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="username" label="Username">
            <Input />
          </Form.Item>
          <Form.Item name="password" label="Password" rules={editingMaster ? [] : [{ required: true }]}>
            <Input.Password />
          </Form.Item>
          <Form.Item name="tenant_id" label="Tenant" rules={[{ required: true }]}>
            <Select placeholder="Select tenant">
              {tenants.map((tenant) => (
                <Select.Option key={tenant.id} value={tenant.id}>
                  {tenant.name}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="is_active" label="Status" initialValue={true}>
            <Select
              options={[
                { label: 'Active', value: true },
                { label: 'Disabled', value: false },
              ]}
            />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};

export default MastersPage;
