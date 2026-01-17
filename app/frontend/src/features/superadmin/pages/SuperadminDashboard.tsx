import React, { useEffect, useState } from 'react';
import { Card, Col, Row, Typography, List, Tag, Alert } from 'antd';
import { fetchAuditLogs, fetchMasters, fetchTenants } from '../services/saasApi';

interface Tenant {
  id: number;
  name: string;
  status: string;
  slug?: string;
}

interface Master {
  id: number;
  email: string;
  username?: string;
  athens_tenant?: number;
  athens_tenant_name?: string;
}

const SuperadminDashboard: React.FC = () => {
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [masters, setMasters] = useState<Master[]>([]);
  const [recentAudit, setRecentAudit] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  const normalizeList = (data: any) => {
    if (Array.isArray(data)) return data;
    if (Array.isArray(data?.results)) return data.results;
    return [];
  };

  useEffect(() => {
    const load = async () => {
      try {
        const [tenantData, masterData, auditData] = await Promise.all([
          fetchTenants(),
          fetchMasters(),
          fetchAuditLogs({}),
        ]);
        setTenants(normalizeList(tenantData));
        setMasters(normalizeList(masterData));
        setRecentAudit(normalizeList(auditData).slice(0, 8));
      } catch (err: any) {
        setError('Failed to load SaaS metrics');
      }
    };
    load();
  }, []);

  const totalTenants = tenants.length;
  const activeTenants = tenants.filter((t) => t.status === 'active').length;
  const trialTenants = tenants.filter((t) => t.status === 'trialing' || t.status === 'trial').length;
  const suspendedTenants = tenants.filter((t) => t.status === 'disabled' || t.status === 'suspended').length;

  return (
    <div>
      <Typography.Title level={3}>SaaS Control Dashboard</Typography.Title>
      {error && <Alert type="error" message={error} style={{ marginBottom: 16 }} />}
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} md={6}>
          <Card title="Total Tenants" bordered>
            <Typography.Title level={2}>{totalTenants}</Typography.Title>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card title="Active Tenants" bordered>
            <Typography.Title level={2}>{activeTenants}</Typography.Title>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card title="Trialing Tenants" bordered>
            <Typography.Title level={2}>{trialTenants}</Typography.Title>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card title="Suspended Tenants" bordered>
            <Typography.Title level={2}>{suspendedTenants}</Typography.Title>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card title="Master Users" bordered>
            <Typography.Title level={2}>{masters.length}</Typography.Title>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col xs={24} md={12}>
          <Card title="Recent SaaS Activity (Audit)">
            <List
              dataSource={recentAudit}
              renderItem={(item) => (
                <List.Item>
                  <List.Item.Meta
                    title={`${item.action} • ${item.entity_type} ${item.entity_id ?? ''}`}
                    description={item.created_at}
                  />
                  <Tag>{item.actor?.email || item.actor || 'System'}</Tag>
                </List.Item>
              )}
              locale={{ emptyText: 'No recent actions' }}
            />
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card title="Tenant Status Breakdown">
            <List
              dataSource={[
                { label: 'Active', value: activeTenants, color: 'green' },
                { label: 'Trialing', value: trialTenants, color: 'blue' },
                { label: 'Suspended', value: suspendedTenants, color: 'red' },
              ]}
              renderItem={(item) => (
                <List.Item>
                  <List.Item.Meta title={item.label} />
                  <Tag color={item.color}>{item.value}</Tag>
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default SuperadminDashboard;
