import React, { useEffect, useState } from 'react';
import { Button, Card, DatePicker, Form, Input, InputNumber, Modal, Select, Space, Table, Tag, Typography, message } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';
import { fetchSubscription, fetchTenants, updateSubscription } from '../services/saasApi';

interface TenantRow {
  id: number;
  name: string;
  status: string;
}

interface SubscriptionRow {
  tenant_id: number;
  plan?: string;
  status?: string;
  seats?: number;
  current_period_start?: string | null;
  current_period_end?: string | null;
  renewal_at?: string | null;
  last_payment_at?: string | null;
  payment_provider?: string | null;
}

const SubscriptionsPage: React.FC = () => {
  const [rows, setRows] = useState<(TenantRow & { subscription?: SubscriptionRow | null })[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [activeTenant, setActiveTenant] = useState<TenantRow | null>(null);
  const [form] = Form.useForm();

  const normalizeList = (data: any) => {
    if (Array.isArray(data)) return data;
    if (Array.isArray(data?.results)) return data.results;
    return [];
  };

  const load = async () => {
    setLoading(true);
    try {
      const tenantRaw = await fetchTenants();
      const tenantData: TenantRow[] = normalizeList(tenantRaw);
      const subs = await Promise.all(
        tenantData.map(async (tenant) => {
          try {
            const subscription = await fetchSubscription(tenant.id);
            return { ...tenant, subscription };
          } catch (err) {
            return { ...tenant, subscription: null };
          }
        })
      );
      setRows(subs);
    } catch (err: any) {
      message.error('Failed to load subscriptions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const openEdit = (tenant: TenantRow, subscription?: SubscriptionRow | null) => {
    setActiveTenant(tenant);
    form.setFieldsValue({
      plan: subscription?.plan,
      status: subscription?.status,
      seats: subscription?.seats,
      current_period_start: subscription?.current_period_start ? dayjs(subscription.current_period_start) : null,
      current_period_end: subscription?.current_period_end ? dayjs(subscription.current_period_end) : null,
      renewal_at: subscription?.renewal_at ? dayjs(subscription.renewal_at) : null,
      last_payment_at: subscription?.last_payment_at ? dayjs(subscription.last_payment_at) : null,
      payment_provider: subscription?.payment_provider,
    });
    setModalVisible(true);
  };

  const handleSubmit = async () => {
    if (!activeTenant) return;
    try {
      const values = await form.validateFields();
      const payload = {
        ...values,
        current_period_start: values.current_period_start ? values.current_period_start.toISOString() : null,
        current_period_end: values.current_period_end ? values.current_period_end.toISOString() : null,
        renewal_at: values.renewal_at ? values.renewal_at.toISOString() : null,
        last_payment_at: values.last_payment_at ? values.last_payment_at.toISOString() : null,
      };
      await updateSubscription(activeTenant.id, payload);
      message.success('Subscription updated');
      setModalVisible(false);
      load();
    } catch (err: any) {
      message.error(err?.response?.data?.detail || 'Failed to update subscription');
    }
  };

  const columns: ColumnsType<TenantRow & { subscription?: SubscriptionRow | null }> = [
    { title: 'Tenant', dataIndex: 'name', key: 'name' },
    {
      title: 'Status',
      dataIndex: ['subscription', 'status'],
      key: 'status',
      render: (status: string) => <Tag color="blue">{status || 'unset'}</Tag>,
    },
    { title: 'Plan', dataIndex: ['subscription', 'plan'], key: 'plan', render: (v: string) => v || 'unset' },
    { title: 'Seats', dataIndex: ['subscription', 'seats'], key: 'seats', render: (v: number) => v ?? '-' },
    {
      title: 'Current Period',
      key: 'period',
      render: (_, record) =>
        record.subscription?.current_period_start && record.subscription?.current_period_end ? (
          <span>
            {dayjs(record.subscription.current_period_start).format('YYYY-MM-DD')} →{' '}
            {dayjs(record.subscription.current_period_end).format('YYYY-MM-DD')}
          </span>
        ) : (
          '-'
        ),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Button size="small" onClick={() => openEdit(record, record.subscription)}>
          Edit
        </Button>
      ),
    },
  ];

  return (
    <Card title={<Typography.Title level={4} style={{ margin: 0 }}>Subscriptions / Billing</Typography.Title>}>
      <Table
        rowKey="id"
        dataSource={Array.isArray(rows) ? rows : []}
        columns={columns}
        loading={loading}
        pagination={{ pageSize: 10 }}
      />

      <Modal
        open={modalVisible}
        title={activeTenant ? `Update Subscription • ${activeTenant.name}` : 'Update Subscription'}
        onCancel={() => setModalVisible(false)}
        onOk={handleSubmit}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="plan" label="Plan">
            <Input placeholder="pro, enterprise, trial, etc." />
          </Form.Item>
          <Form.Item name="status" label="Status">
            <Select allowClear>
              <Select.Option value="trialing">Trialing</Select.Option>
              <Select.Option value="active">Active</Select.Option>
              <Select.Option value="past_due">Past Due</Select.Option>
              <Select.Option value="canceled">Canceled</Select.Option>
              <Select.Option value="suspended">Suspended</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="seats" label="Seats">
            <InputNumber min={1} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="current_period_start" label="Current Period Start">
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="current_period_end" label="Current Period End">
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="renewal_at" label="Renewal At">
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="last_payment_at" label="Last Payment At">
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="payment_provider" label="Payment Provider">
            <Input />
          </Form.Item>
          <Form.Item name="notes" label="Notes">
            <Input.TextArea rows={3} />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};

export default SubscriptionsPage;
