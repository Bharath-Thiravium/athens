import React, { useEffect, useMemo, useState } from 'react';
import {
  Card,
  Descriptions,
  Divider,
  Space,
  Tag,
  Typography,
  Form,
  Input,
  Switch,
  Select,
  Button,
  Row,
  Col,
  InputNumber,
  message,
  Spin,
} from 'antd';
import api from '@common/utils/axiosetup';
import useAuthStore from '@common/store/authStore';
import { fetchSaasSettings, updateSaasSettings, SaaSSettingsPayload } from '../services/saasApi';

const SuperadminSettings: React.FC = () => {
  const { username, usertype, userId, tokenExpiry } = useAuthStore();
  const [healthStatus, setHealthStatus] = useState<'ok' | 'error' | 'loading'>('loading');
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [settings, setSettings] = useState<SaaSSettingsPayload>({
    platform_name: 'Athens',
    platform_url: '',
    support_email: '',
    support_phone: '',
    logo_url: '',
    primary_color: '',
    email_from_name: '',
    email_from_address: '',
    email_reply_to: '',
    billing_provider: '',
    billing_mode: '',
    invoice_footer: '',
    session_timeout_minutes: 60,
    audit_retention_days: 365,
    allow_self_signup: false,
    require_mfa: false,
    maintenance_mode: false,
  });

  useEffect(() => {
    let isMounted = true;
    const checkHealth = async () => {
      try {
        await api.get('/health/');
        if (isMounted) setHealthStatus('ok');
      } catch (error) {
        if (isMounted) setHealthStatus('error');
      }
    };
    checkHealth();
    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    const loadSettings = async () => {
      setLoading(true);
      try {
        const data = await fetchSaasSettings();
        setSettings(data);
        form.setFieldsValue(data);
      } catch (error: any) {
        message.error(error?.response?.data?.detail || 'Failed to load SaaS settings');
      } finally {
        setLoading(false);
      }
    };
    loadSettings();
  }, [form]);

  const expiryLabel = useMemo(() => {
    if (!tokenExpiry) return 'Unknown';
    return new Date(tokenExpiry).toLocaleString();
  }, [tokenExpiry]);

  const updatedAtLabel = useMemo(() => {
    if (!settings.updated_at) return 'Unknown';
    return new Date(settings.updated_at).toLocaleString();
  }, [settings.updated_at]);

  const healthTag = healthStatus === 'ok'
    ? <Tag color="green">Healthy</Tag>
    : healthStatus === 'error'
      ? <Tag color="red">Unreachable</Tag>
      : <Tag>Checking</Tag>;

  const handleSave = async (values: SaaSSettingsPayload) => {
    setLoading(true);
    try {
      const updated = await updateSaasSettings(values);
      setSettings(updated);
      form.setFieldsValue(updated);
      message.success('SaaS settings updated');
    } catch (error: any) {
      message.error(error?.response?.data?.detail || 'Failed to update settings');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    form.setFieldsValue(settings);
    message.info('Changes reverted');
  };

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Card>
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div>
            <Typography.Title level={4}>SaaS Control Plane Settings</Typography.Title>
            <Typography.Paragraph className="text-color-text-muted">
              Configure platform-wide branding, billing metadata, and security policies. Tenant-level settings are not exposed here.
            </Typography.Paragraph>
          </div>
          <Space>
            <Button onClick={handleReset}>Reset</Button>
            <Button type="primary" loading={loading} onClick={() => form.submit()}>
              Save Changes
            </Button>
          </Space>
        </div>
      </Card>

      <Spin spinning={loading}>
        <Form form={form} layout="vertical" onFinish={handleSave} initialValues={settings}>
          <Row gutter={24}>
            <Col xs={24} lg={12}>
              <Card title="Platform Identity" className="mb-4">
                <Form.Item label="Platform Name" name="platform_name" rules={[{ required: true, message: 'Platform name is required' }]}>
                  <Input placeholder="Athens" />
                </Form.Item>
                <Form.Item label="Platform URL" name="platform_url">
                  <Input placeholder="https://app.athenas.co.in" />
                </Form.Item>
                <Form.Item label="Support Email" name="support_email">
                  <Input placeholder="support@athenas.co.in" />
                </Form.Item>
                <Form.Item label="Support Phone" name="support_phone">
                  <Input placeholder="+91 99999 99999" />
                </Form.Item>
                <Form.Item label="Logo URL" name="logo_url">
                  <Input placeholder="https://cdn.athenas.co.in/logo.png" />
                </Form.Item>
                <Form.Item label="Primary Brand Color" name="primary_color">
                  <Input placeholder="#0f172a" />
                </Form.Item>
                <Typography.Text type="secondary">
                  Uploads and API keys are managed in infrastructure secrets. Use a public logo URL if required.
                </Typography.Text>
              </Card>
            </Col>

            <Col xs={24} lg={12}>
              <Card title="Billing Configuration" className="mb-4">
                <Form.Item label="Billing Provider" name="billing_provider">
                  <Select placeholder="Select provider">
                    <Select.Option value="manual">Manual</Select.Option>
                    <Select.Option value="stripe">Stripe</Select.Option>
                    <Select.Option value="razorpay">Razorpay</Select.Option>
                    <Select.Option value="other">Other</Select.Option>
                  </Select>
                </Form.Item>
                <Form.Item label="Billing Mode" name="billing_mode">
                  <Select placeholder="Select billing mode">
                    <Select.Option value="manual">Manual</Select.Option>
                    <Select.Option value="automatic">Automatic</Select.Option>
                  </Select>
                </Form.Item>
                <Form.Item label="Invoice Footer" name="invoice_footer">
                  <Input.TextArea rows={4} placeholder="Invoice footer or legal text" />
                </Form.Item>
                <Typography.Text type="secondary">
                  Payment provider credentials remain in server secrets and are never exposed here.
                </Typography.Text>
              </Card>
            </Col>
          </Row>

          <Row gutter={24}>
            <Col xs={24} lg={12}>
              <Card title="Email & Notifications" className="mb-4">
                <Form.Item label="From Name" name="email_from_name">
                  <Input placeholder="Athens SaaS" />
                </Form.Item>
                <Form.Item label="From Address" name="email_from_address">
                  <Input placeholder="no-reply@athenas.co.in" />
                </Form.Item>
                <Form.Item label="Reply-To Address" name="email_reply_to">
                  <Input placeholder="support@athenas.co.in" />
                </Form.Item>
              </Card>
            </Col>

            <Col xs={24} lg={12}>
              <Card title="Security & Compliance" className="mb-4">
                <Row gutter={16}>
                  <Col span={12}>
                    <Form.Item label="Session Timeout (minutes)" name="session_timeout_minutes">
                      <InputNumber min={5} max={480} style={{ width: '100%' }} />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item label="Audit Retention (days)" name="audit_retention_days">
                      <InputNumber min={30} max={3650} style={{ width: '100%' }} />
                    </Form.Item>
                  </Col>
                </Row>
                <Form.Item label="Require MFA for Superadmins" name="require_mfa" valuePropName="checked">
                  <Switch />
                </Form.Item>
                <Form.Item label="Maintenance Mode" name="maintenance_mode" valuePropName="checked">
                  <Switch />
                </Form.Item>
                <Form.Item label="Allow Self Signup" name="allow_self_signup" valuePropName="checked">
                  <Switch />
                </Form.Item>
              </Card>
            </Col>
          </Row>

          <Divider />
        </Form>
      </Spin>

      <Card title="Superadmin Profile">
        <Descriptions bordered column={1} size="small">
          <Descriptions.Item label="Username">{username || '-'}</Descriptions.Item>
          <Descriptions.Item label="User Type">{usertype || 'superadmin'}</Descriptions.Item>
          <Descriptions.Item label="User ID">{userId || '-'}</Descriptions.Item>
          <Descriptions.Item label="Token Expiry">{expiryLabel}</Descriptions.Item>
          <Descriptions.Item label="Settings Updated">{updatedAtLabel}</Descriptions.Item>
        </Descriptions>
      </Card>

      <Card title="System Status">
        <Descriptions bordered column={1} size="small">
          <Descriptions.Item label="API Health">{healthTag}</Descriptions.Item>
          <Descriptions.Item label="WebSocket">
            <Tag color="blue">Notifications Enabled</Tag>
          </Descriptions.Item>
        </Descriptions>
      </Card>
    </Space>
  );
};

export default SuperadminSettings;
