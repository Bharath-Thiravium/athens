import React, { useState, useEffect } from 'react';
import { Card, Alert, Descriptions, Spin, Button, Modal, Image, message } from 'antd';
import { FileImageOutlined, CheckCircleOutlined, ExclamationCircleOutlined, ReloadOutlined, EyeOutlined } from '@ant-design/icons';
import api from '@common/utils/axiosetup';

interface TemplateInfo {
  can_create_template: boolean;
  missing_fields: string[];
  user_data: {
    full_name: string;
    designation: string;
    company_name: string;
    has_company_logo: boolean;
    employee_id?: string;
  };
  has_existing_template: boolean;
  template_data?: any;
}

const DigitalSignatureTemplate: React.FC = () => {
  const [templateInfo, setTemplateInfo] = useState<TemplateInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [previewVisible, setPreviewVisible] = useState(false);
  const [templateUrl, setTemplateUrl] = useState<string>('');

  const fetchTemplateInfo = async () => {
    try {
      const response = await api.get('/authentication/signature/template/data/');
      setTemplateInfo(response.data);
    } catch (error) {
      setTemplateInfo({
        can_create_template: false,
        missing_fields: ['Error loading data'],
        user_data: {
          full_name: 'Not available',
          designation: 'Not available', 
          company_name: 'Not available',
          has_company_logo: false
        },
        has_existing_template: false
      });
    } finally {
      setLoading(false);
    }
  };

  const handleViewTemplate = async () => {
    try {
      // Get template info first to get the correct URL
      const response = await api.get('/authentication/signature/template/data/');
      if (response.data.has_existing_template && response.data.template_data?.signature_url) {
        setTemplateUrl(response.data.template_data.signature_url);
        setPreviewVisible(true);
      } else {
        // Fallback: try to construct URL from user detail
        const userResponse = await api.get('/authentication/userdetail/');
        if (userResponse.data.signature_template) {
          setTemplateUrl(userResponse.data.signature_template);
          setPreviewVisible(true);
        } else {
          message.error('No signature template found');
        }
      }
    } catch (error) {
      console.error('Failed to load template:', error);
      message.error('Failed to load template');
    }
  };

  const handleCreateTemplate = async () => {
    try {
      setLoading(true);
      const response = await api.post('/authentication/signature/template/generate/');
      
      // Verify template was actually created
      if (!response.data.template_url) {
        message.error('Template generation failed - no image created');
        return;
      }
      
      message.success('Digital signature template generated successfully!');
      fetchTemplateInfo();
    } catch (error: any) {
      console.error('Template generation error:', error);
      message.error(error.response?.data?.error || 'Failed to create template');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTemplateInfo();
  }, []);

  if (loading) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: '20px' }}>
          <Spin size="large" />
          <div style={{ marginTop: 16 }}>Loading template information...</div>
        </div>
      </Card>
    );
  }

  if (!templateInfo) return null;

  return (
    <div style={{ padding: '0 48px', margin: '0 auto' }}>
      <Card 
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FileImageOutlined />
            <span>Digital Signature Template</span>
          </div>
        }
        extra={
          <Button 
            icon={<ReloadOutlined />} 
            onClick={fetchTemplateInfo}
            size="small"
          >
            Refresh
          </Button>
        }
        style={{ wordWrap: 'break-word', overflowWrap: 'break-word' }}
      >
      {/* Template Status */}
      {templateInfo.has_existing_template ? (
        <div style={{ 
          padding: '16px', 
          backgroundColor: '#f6ffed', 
          border: '1px solid #b7eb8f',
          borderRadius: '6px',
          marginBottom: 16,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <CheckCircleOutlined style={{ color: '#52c41a', fontSize: '16px' }} />
            <span style={{ color: '#52c41a', fontWeight: 500 }}>Digital Signature Ready</span>
          </div>
          <Button 
            size="small" 
            icon={<EyeOutlined />} 
            onClick={handleViewTemplate}
          >
            View Template
          </Button>
        </div>
      ) : templateInfo.can_create_template ? (
        <Alert
          message="Template Can Be Created"
          description="Your profile information is complete. Click below to generate your digital signature template."
          type="info"
          icon={<ExclamationCircleOutlined />}
          style={{ marginBottom: 16 }}
          action={
            <Button size="small" type="primary" onClick={handleCreateTemplate}>
              Generate Template
            </Button>
          }
        />
      ) : (
        <Alert
          message="Complete Profile Required"
          description="Please complete your profile information to enable digital signature template creation."
          type="warning"
          icon={<ExclamationCircleOutlined />}
          style={{ marginBottom: 16 }}
        />
      )}

      {/* Template Information */}
      <Descriptions title="Signature Information" size="small" column={1} bordered>
        <Descriptions.Item label="Full Name">
          <span style={{ fontWeight: 500 }}>{templateInfo.user_data.full_name}</span>
        </Descriptions.Item>
        <Descriptions.Item label="Employee ID">
          <span style={{ fontWeight: 500 }}>{templateInfo.user_data.employee_id || 'Not set'}</span>
        </Descriptions.Item>
        <Descriptions.Item label="Designation">
          <span style={{ fontWeight: 500 }}>{templateInfo.user_data.designation}</span>
        </Descriptions.Item>
        <Descriptions.Item label="Company">
          <span style={{ fontWeight: 500 }}>{templateInfo.user_data.company_name}</span>
        </Descriptions.Item>
        <Descriptions.Item label="Company Logo">
          <span style={{ 
            fontWeight: 500,
            color: templateInfo.user_data.has_company_logo ? '#52c41a' : '#faad14'
          }}>
            {templateInfo.user_data.has_company_logo ? 'Available' : 'Not available'}
          </span>
        </Descriptions.Item>
      </Descriptions>

      {/* Missing Fields Warning */}
      {templateInfo.missing_fields.length > 0 && (
        <Alert
          message="Missing Required Information"
          description={
            <div>
              <p>Complete the following information to enable digital signature:</p>
              <ul style={{ margin: 0, paddingLeft: 20 }}>
                {templateInfo.missing_fields.map((field, index) => (
                  <li key={index}>{field}</li>
                ))}
              </ul>
            </div>
          }
          type="warning"
          style={{ marginTop: 16 }}
        />
      )}

      {/* Information Note */}
      <div style={{ 
        marginTop: 16, 
        padding: '12px', 
        backgroundColor: '#f6f8fa', 
        borderRadius: '6px',
        fontSize: '12px',
        color: '#666'
      }}>
        <strong>Template Format:</strong> Company logo (50% transparency background), 
        left side with name and employee ID, right side with "Digitally signed by [Name]" 
        with designation and company name.
      </div>

      {/* Template Preview Modal */}
      <Modal
        title="Digital Signature Template Preview"
        open={previewVisible}
        onCancel={() => setPreviewVisible(false)}
        footer={null}
        width={600}
      >
        {templateUrl && (
          <div style={{ textAlign: 'center' }}>
            <Image
              src={templateUrl}
              alt="Digital Signature Template"
              style={{ maxWidth: '100%' }}
            />
          </div>
        )}
      </Modal>
      </Card>
    </div>
  );
};

export default DigitalSignatureTemplate;