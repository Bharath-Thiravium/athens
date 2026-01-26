import React, { useState, useEffect, useRef } from 'react';
import { Card, Alert, Descriptions, Spin, Button, Modal, message } from 'antd';
import { FileImageOutlined, CheckCircleOutlined, ExclamationCircleOutlined, ReloadOutlined, EyeOutlined, DownloadOutlined } from '@ant-design/icons';
import api from '@common/utils/axiosetup';
import DigitalSignatureBlock from './DigitalSignatureBlock';
import html2canvas from 'html2canvas';
import './StandardSignatureTemplate.css';

interface TemplateData {
  success: boolean;
  can_create_template: boolean;
  has_existing_template: boolean;
  missing_fields: string[];
  user_data: {
    full_name: string;
    designation: string;
    company_name: string;
    has_company_logo: boolean;
    employee_id: string;
  };
}

interface SignatureData {
  success: boolean;
  signer_name: string;
  employee_id: string;
  designation: string;
  department: string;
  company_name: string;
  company_logo_url?: string;
  signed_at: string;
  verification_token: string;
  is_preview?: boolean;
}

const StandardSignatureTemplate: React.FC = () => {
  const [templateData, setTemplateData] = useState<TemplateData | null>(null);
  const [signatureData, setSignatureData] = useState<SignatureData | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [previewVisible, setPreviewVisible] = useState(false);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const signatureRef = useRef<HTMLDivElement>(null);

  const fetchTemplateData = async () => {
    try {
      setLoading(true);
      const response = await api.get('/authentication/signature/template-data/');
      setTemplateData(response.data);
    } catch (error) {
      console.error('Failed to fetch template data:', error);
      message.error('Failed to load template information');
    } finally {
      setLoading(false);
    }
  };

  const generateTemplate = async () => {
    try {
      setGenerating(true);
      const response = await api.get('/authentication/signature/json-data/');
      
      if (response.data.success) {
        message.success('Digital signature template generated successfully!');
        await fetchTemplateData();
      } else {
        message.error(response.data.error || 'Failed to generate template');
      }
    } catch (error: any) {
      console.error('Template generation error:', error);
      message.error(error.response?.data?.error || 'Failed to generate template');
    } finally {
      setGenerating(false);
    }
  };

  const previewTemplate = async () => {
    try {
      setPreviewLoading(true);
      const response = await api.get('/authentication/signature/preview-json/');
      
      if (response.data.success) {
        setSignatureData(response.data);
        setPreviewVisible(true);
      } else {
        message.error('No template available for preview');
      }
    } catch (error) {
      console.error('Preview error:', error);
      message.error('Failed to load template preview');
    } finally {
      setPreviewLoading(false);
    }
  };

  const downloadSignature = async () => {
    if (!signatureData || !signatureRef.current) return;
    
    try {
      setDownloading(true);
      // Target ONLY the ds-card element using the ref
      const canvas = await html2canvas(signatureRef.current, {
        backgroundColor: '#ffffff',
        scale: 2,
        useCORS: true,
        allowTaint: true
      });
      
      const link = document.createElement('a');
      link.download = `signature-${signatureData.signer_name.replace(/\s+/g, '-')}.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();
    } catch (error) {
      console.error('Download error:', error);
      message.error('Failed to download signature');
    } finally {
      setDownloading(false);
    }
  };

  const handleModalClose = () => {
    setPreviewVisible(false);
    setSignatureData(null);
  };

  useEffect(() => {
    fetchTemplateData();
  }, []);

  if (loading) {
    return (
      <Card className="signature-template-card">
        <div className="loading-container">
          <Spin size="large" />
          <div className="loading-text">Loading template information...</div>
        </div>
      </Card>
    );
  }

  if (!templateData) {
    return (
      <Card className="signature-template-card">
        <Alert
          message="Failed to Load"
          description="Unable to load template information. Please refresh the page."
          type="error"
          showIcon
        />
      </Card>
    );
  }

  return (
    <div className="signature-template-container">
      <Card 
        title={
          <div className="card-title">
            <FileImageOutlined />
            <span>Digital Signature Template</span>
          </div>
        }
        extra={
          <Button 
            icon={<ReloadOutlined />} 
            onClick={fetchTemplateData}
            size="small"
          >
            Refresh
          </Button>
        }
        className="signature-template-card"
      >
        {/* Template Status */}
        {templateData.has_existing_template ? (
          <div className="status-ready">
            <div className="status-content">
              <CheckCircleOutlined className="status-icon success" />
              <span className="status-text success">Digital Signature Ready</span>
            </div>
            <div style={{ display: 'flex', gap: '8px' }}>
              <Button 
                size="small" 
                icon={<EyeOutlined />} 
                onClick={previewTemplate}
                loading={previewLoading}
              >
                View Template
              </Button>
              {templateData.can_create_template && (
                <Button 
                  size="small" 
                  type="primary" 
                  onClick={generateTemplate}
                  loading={generating}
                >
                  Generate JSON
                </Button>
              )}
            </div>
          </div>
        ) : templateData.can_create_template ? (
          <Alert
            message="Template Can Be Created"
            description="Your profile information is complete. Click below to generate your digital signature template."
            type="info"
            icon={<ExclamationCircleOutlined />}
            className="status-alert"
            action={
              <Button 
                size="small" 
                type="primary" 
                onClick={generateTemplate}
                loading={generating}
              >
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
            className="status-alert"
          />
        )}

        {/* Template Information */}
        <Descriptions 
          title="Signature Information" 
          size="small" 
          column={1} 
          bordered
          className="template-info"
        >
          <Descriptions.Item label="Full Name">
            <span className="info-value">{templateData.user_data.full_name}</span>
          </Descriptions.Item>
          <Descriptions.Item label="Employee ID">
            <span className="info-value">{templateData.user_data.employee_id || 'Not set'}</span>
          </Descriptions.Item>
          <Descriptions.Item label="Designation">
            <span className="info-value">{templateData.user_data.designation || 'Not set'}</span>
          </Descriptions.Item>
          <Descriptions.Item label="Company">
            <span className="info-value">{templateData.user_data.company_name || 'Not set'}</span>
          </Descriptions.Item>
          <Descriptions.Item label="Company Logo">
            <span className={`info-value ${templateData.user_data.has_company_logo ? 'success' : 'warning'}`}>
              {templateData.user_data.has_company_logo ? 'Available' : 'Not available'}
            </span>
          </Descriptions.Item>
        </Descriptions>

        {/* Missing Fields Warning */}
        {templateData.missing_fields.length > 0 && (
          <Alert
            message="Missing Required Information"
            description={
              <div>
                <p>Complete the following information to enable digital signature:</p>
                <ul className="missing-fields-list">
                  {templateData.missing_fields.map((field, index) => (
                    <li key={index}>{field}</li>
                  ))}
                </ul>
              </div>
            }
            type="warning"
            className="missing-fields-alert"
          />
        )}

        {/* Information Note */}
        <div className="info-note">
          <strong>Template Format:</strong> Company logo watermark (50% transparency), 
          left partition with name and employee ID, right partition with "Digitally signed by [Name]" 
          and signing details.
        </div>
      </Card>

      {/* Preview Modal */}
      <Modal
        title="Digital Signature Template Preview"
        open={previewVisible}
        onCancel={handleModalClose}
        footer={null}
        width={700}
        centered
        className="preview-modal"
      >
        {previewLoading ? (
          <div className="preview-loading">
            <Spin size="large" />
            <div>Loading preview...</div>
          </div>
        ) : previewLoading ? (
          <div className="preview-loading">
            <Spin size="large" />
            <div>Loading preview...</div>
          </div>
        ) : signatureData ? (
          <div className="signature-preview-container">
            <DigitalSignatureBlock
              ref={signatureRef}
              signerName={signatureData.signer_name}
              employeeId={signatureData.employee_id}
              designation={signatureData.designation}
              department={signatureData.department}
              companyName={signatureData.company_name}
              companyLogoUrl={signatureData.company_logo_url}
              signedAt={signatureData.signed_at}
              verificationToken={signatureData.verification_token}
              isPreview={signatureData.is_preview}
            />
            <div className="preview-actions">
              <Button 
                icon={<DownloadOutlined />}
                onClick={downloadSignature}
                loading={downloading}
              >
                Download PNG
              </Button>
            </div>
          </div>
        ) : (
          <div className="preview-error">
            <Alert
              message="Preview Not Available"
              description="Unable to load template preview."
              type="warning"
              showIcon
            />
          </div>
        )}
      </Modal>
    </div>
  );
};

export default StandardSignatureTemplate;