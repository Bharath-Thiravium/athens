import React, { useState, useEffect } from 'react';
import { Card, Form, Input, Button, Switch, Select, message, Spin, Divider, Row, Col, Typography, Space } from 'antd';
import { SaveOutlined, ReloadOutlined, SettingOutlined } from '@ant-design/icons';
import PageLayout from '@common/components/PageLayout';
import { getSystemSettings, updateSystemSettings } from '../api';

const { Option } = Select;
const { Title } = Typography;

interface SystemSettingsData {
  siteName: string;
  siteDescription: string;
  maintenanceMode: boolean;
  allowRegistration: boolean;
  defaultUserRole: string;
  sessionTimeout: number;
  maxFileSize: number;
  emailNotifications: boolean;
  smsNotifications: boolean;
  backupFrequency: string;
  logLevel: string;
}

const SystemSettings: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [settings, setSettings] = useState<SystemSettingsData>({
    siteName: 'EHS Management System',
    siteDescription: 'Comprehensive Environmental, Health & Safety Management Platform',
    maintenanceMode: false,
    allowRegistration: false,
    defaultUserRole: 'clientuser',
    sessionTimeout: 60,
    maxFileSize: 10,
    emailNotifications: true,
    smsNotifications: false,
    backupFrequency: 'daily',
    logLevel: 'INFO'
  });

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    setLoading(true);
    try {
      const { data } = await getSystemSettings();
      setSettings(data);
      form.setFieldsValue(data);
      // Settings loaded successfully - no need for success message on initial load
    } catch (error: any) {
      message.error(error.response?.data?.error || 'Failed to load settings');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (values: SystemSettingsData) => {
    setLoading(true);
    try {
      await updateSystemSettings(values);
      setSettings(values);
      message.success('Settings saved successfully');
    } catch (error: any) {
      message.error(error.response?.data?.error || 'Failed to save settings');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    form.setFieldsValue(settings);
    message.info('Settings reset to last saved values');
  };

  return (
    <PageLayout
      title="System Settings"
      subtitle="Configure system-wide settings and preferences"
      icon={<SettingOutlined />}
      breadcrumbs={[
        { title: 'System' },
        { title: 'Settings' }
      ]}
      actions={
        <Space>
          <Button
            icon={<ReloadOutlined />}
            onClick={handleReset}
          >
            Reset
          </Button>
          <Button
            type="primary"
            htmlType="submit"
            icon={<SaveOutlined />}
            loading={loading}
            form="settings-form"
          >
            Save Settings
          </Button>
        </Space>
      }
    >
      
      <Card variant="borderless">
        <Spin spinning={loading}>
        <Form
          id="settings-form"
          form={form}
          layout="vertical"
          onFinish={handleSave}
          initialValues={settings}
        >
          <Row gutter={24}>
            <Col span={12}>
              <Card title="General Settings" className="mb-6">
                <Form.Item
                  label="Site Name"
                  name="siteName"
                  rules={[{ required: true, message: 'Site name is required' }]}
                >
                  <Input placeholder="Enter site name" />
                </Form.Item>

                <Form.Item
                  label="Site Description"
                  name="siteDescription"
                >
                  <Input.TextArea
                    rows={3}
                    placeholder="Enter site description"
                  />
                </Form.Item>

                <Form.Item
                  label="Maintenance Mode"
                  name="maintenanceMode"
                  valuePropName="checked"
                >
                  <Switch />
                </Form.Item>

                <Form.Item
                  label="Allow User Registration"
                  name="allowRegistration"
                  valuePropName="checked"
                >
                  <Switch />
                </Form.Item>

                <Form.Item
                  label="Default User Role"
                  name="defaultUserRole"
                >
                  <Select>
                    <Option value="clientuser">Client User</Option>
                    <Option value="epcuser">EPC User</Option>
                    <Option value="contractoruser">Contractor User</Option>
                  </Select>
                </Form.Item>
              </Card>
            </Col>

            <Col span={12}>
              <Card title="Security & Performance" className="mb-6">
                <Form.Item
                  label="Session Timeout (minutes)"
                  name="sessionTimeout"
                  rules={[{ required: true, type: 'number', min: 5, max: 480 }]}
                >
                  <Input type="number" placeholder="60" />
                </Form.Item>

                <Form.Item
                  label="Max File Size (MB)"
                  name="maxFileSize"
                  rules={[{ required: true, type: 'number', min: 1, max: 100 }]}
                >
                  <Input type="number" placeholder="10" />
                </Form.Item>

                <Form.Item
                  label="Log Level"
                  name="logLevel"
                >
                  <Select>
                    <Option value="DEBUG">Debug</Option>
                    <Option value="INFO">Info</Option>
                    <Option value="WARNING">Warning</Option>
                    <Option value="ERROR">Error</Option>
                    <Option value="CRITICAL">Critical</Option>
                  </Select>
                </Form.Item>
              </Card>

              <Card title="Notifications & Backup">
                <Form.Item
                  label="Email Notifications"
                  name="emailNotifications"
                  valuePropName="checked"
                >
                  <Switch />
                </Form.Item>

                <Form.Item
                  label="SMS Notifications"
                  name="smsNotifications"
                  valuePropName="checked"
                >
                  <Switch />
                </Form.Item>

                <Form.Item
                  label="Backup Frequency"
                  name="backupFrequency"
                >
                  <Select>
                    <Option value="hourly">Hourly</Option>
                    <Option value="daily">Daily</Option>
                    <Option value="weekly">Weekly</Option>
                    <Option value="monthly">Monthly</Option>
                  </Select>
                </Form.Item>
              </Card>
            </Col>
          </Row>

          <Divider />
        </Form>
      </Spin>
      </Card>
    </PageLayout>
  );
};

export default SystemSettings;
