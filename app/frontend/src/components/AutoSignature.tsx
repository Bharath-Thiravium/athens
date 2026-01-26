import React, { useState, useEffect } from 'react';
import { Button, Space, Alert, Spin } from 'antd';
import { FileImageOutlined, ReloadOutlined } from '@ant-design/icons';
import { useDigitalSignature } from '../features/user/hooks/useDigitalSignature';
import DigitalSignature from './DigitalSignature';
import api from '@common/utils/axiosetup';

interface AutoSignatureProps {
  onSignatureGenerated?: (signatureUrl: string) => void;
  onSignatureFile?: (file: File) => void;
  disabled?: boolean;
  buttonText?: string;
  showPreview?: boolean;
}

/**
 * Component that automatically uses digital signature templates instead of manual uploads
 * Replaces all signature upload functionality with template-generated signatures
 */
const AutoSignature: React.FC<AutoSignatureProps> = ({
  onSignatureGenerated,
  onSignatureFile,
  disabled = false,
  buttonText = "Generate Digital Signature",
  showPreview = true
}) => {
  const { generateSignature, loading } = useDigitalSignature();
  const [hasTemplate, setHasTemplate] = useState<boolean | null>(null);
  const [signatureData, setSignatureData] = useState<any>(null);
  const [checkingTemplate, setCheckingTemplate] = useState(true);

  // Check if user has a signature template
  useEffect(() => {
    const checkTemplate = async () => {
      try {
        const response = await api.get('/authentication/signature/template/data/');
        setHasTemplate(response.data.has_existing_template);
      } catch (error) {
        setHasTemplate(false);
      } finally {
        setCheckingTemplate(false);
      }
    };

    checkTemplate();
  }, []);

  const handleGenerateSignature = async () => {
    const url = await generateSignature();
    if (url) {
      // Get signature metadata from backend
      try {
        const response = await api.get('/authentication/signature/get/');
        if (response.data.has_signature) {
          setSignatureData({
            signatureImageUrl: url,
            signerName: response.data.signer_name,
            employeeId: response.data.employee_id,
            designation: response.data.designation,
            department: response.data.department,
            companyLogoUrl: response.data.company_logo_url,
            signedAt: new Date().toISOString()
          });
        }
      } catch (error) {
        console.error('Failed to get signature metadata:', error);
      }
      
      onSignatureGenerated?.(url);
      
      // Convert to File if callback provided
      if (onSignatureFile) {
        try {
          const response = await api.get(url, { responseType: 'blob' });
          const blob = response.data;
          const file = new File([blob], 'signature.png', { type: 'image/png' });
          onSignatureFile(file);
        } catch (error) {
          console.error('Failed to convert signature to file:', error);
        }
      }
    }
  };

  if (checkingTemplate) {
    return (
      <div style={{ textAlign: 'center', padding: '20px' }}>
        <Spin size="small" />
        <div style={{ marginTop: 8, fontSize: '12px', color: '#666' }}>
          Checking signature template...
        </div>
      </div>
    );
  }

  if (!hasTemplate) {
    return (
      <Alert
        message="No Digital Signature Template"
        description="Please create your digital signature template in your profile first."
        type="warning"
        showIcon
        action={
          <Button size="small" onClick={() => window.location.href = '/dashboard/profile'}>
            Go to Profile
          </Button>
        }
      />
    );
  }

  return (
    <div>
      <Space direction="vertical" style={{ width: '100%' }}>
        <Button
          type="primary"
          icon={<FileImageOutlined />}
          loading={loading}
          disabled={disabled}
          onClick={handleGenerateSignature}
        >
          {buttonText}
        </Button>
        
        {signatureData && showPreview && (
          <div style={{ 
            border: '1px solid #d9d9d9', 
            borderRadius: '6px', 
            padding: '8px',
            backgroundColor: '#fafafa'
          }}>
            <DigitalSignature
              signerName={signatureData.signerName}
              employeeId={signatureData.employeeId}
              designation={signatureData.designation}
              department={signatureData.department}
              signedAt={signatureData.signedAt}
              companyLogoUrl={signatureData.companyLogoUrl}
              signatureImageUrl={signatureData.signatureImageUrl}
            />
            <div style={{ marginTop: 4, fontSize: '12px', color: '#666', textAlign: 'center' }}>
              Digital signature generated with current date/time
            </div>
          </div>
        )}
        
        {signatureData && (
          <Button
            size="small"
            icon={<ReloadOutlined />}
            onClick={handleGenerateSignature}
            disabled={loading}
          >
            Regenerate
          </Button>
        )}
      </Space>
    </div>
  );
};

export default AutoSignature;