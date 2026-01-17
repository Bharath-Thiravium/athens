import React, { useEffect, useState } from 'react';
import { Card, Form, Input, Button, Space, Table, Typography, Tag, message } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { fetchAuditLogs } from '../services/saasApi';

interface AuditRow {
  id: number;
  actor?: any;
  action: string;
  entity_type: string;
  entity_id: string;
  created_at: string;
}

const AuditLogsPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();

  const load = async (filters?: any) => {
    setLoading(true);
    try {
      const data = await fetchAuditLogs(filters);
      setLogs(data?.results ?? data ?? []);
    } catch (err: any) {
      message.error('Failed to load audit logs');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleFilter = async () => {
    const values = await form.validateFields();
    load(values);
  };

  const columns: ColumnsType<AuditRow> = [
    { title: 'When', dataIndex: 'created_at', key: 'created_at' },
    { title: 'Actor', dataIndex: ['actor', 'email'], key: 'actor', render: (_, record) => record.actor?.email || record.actor || 'System' },
    { title: 'Action', dataIndex: 'action', key: 'action', render: (action: string) => <Tag>{action}</Tag> },
    { title: 'Entity', dataIndex: 'entity_type', key: 'entity_type', render: (val, record) => `${val} #${record.entity_id}` },
  ];

  return (
    <Card
      title={
        <Space align="center">
          <Typography.Title level={4} style={{ margin: 0 }}>
            Audit Logs
          </Typography.Title>
          <Button onClick={() => load()} size="small">
            Refresh
          </Button>
        </Space>
      }
    >
      <Form layout="inline" form={form} onFinish={handleFilter} style={{ marginBottom: 16 }}>
        <Form.Item name="tenant_id" label="Tenant ID">
          <Input placeholder="Tenant ID" />
        </Form.Item>
        <Form.Item name="actor_id" label="Actor ID">
          <Input placeholder="User ID" />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit">
            Filter
          </Button>
        </Form.Item>
      </Form>
      <Table rowKey="id" dataSource={logs} columns={columns} loading={loading} pagination={{ pageSize: 10 }} />
    </Card>
  );
};

export default AuditLogsPage;
