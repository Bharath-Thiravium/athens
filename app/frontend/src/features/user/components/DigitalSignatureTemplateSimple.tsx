import React, { useState, useEffect } from 'react';
import { Card, Spin, Image } from 'antd';
import { FileImageOutlined } from '@ant-design/icons';
import api from '@common/utils/axiosetup';
import { fetchSignaturePreviewUrl } from '@common/utils/signaturePreview';

const DigitalSignatureTemplate: React.FC = () => {
  const [templateUrl, setTemplateUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    return () => {
      if (templateUrl && templateUrl.startsWith('blob:')) {
        URL.revokeObjectURL(templateUrl);
      }
    };
  }, [templateUrl]);

  useEffect(() => {
    const fetchTemplate = async () => {
      try {
        // First get template data
        const dataResponse = await api.get('/authentication/signature/template/data/');
        
        // If template exists, get the preview URL
        if (dataResponse.data.has_existing_template) {
          const previewUrl = await fetchSignaturePreviewUrl();
          setTemplateUrl(previewUrl);
        }
      } catch (error) {
        console.error('Error fetching template:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTemplate();
  }, []);

  if (loading) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: '20px' }}>
          <Spin size="large" />
        </div>
      </Card>
    );
  }

  return (
    <Card 
      title={
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <FileImageOutlined />
          <span>Digital Signature Template</span>
        </div>
      }
    >
      {templateUrl ? (
        <div className="ds-preview-wrap">
          <Image
            wrapperClassName="ds-preview-wrapper"
            className="ds-preview-img"
            src={templateUrl}
            alt="Digital Signature Template"
            style={{ 
              maxWidth: '100%', 
              maxHeight: '200px',
              height: 'auto',
              border: '1px solid #d9d9d9',
              borderRadius: '6px'
            }}
            preview={false}
          />
        </div>
      ) : (
        <div style={{ textAlign: 'center', padding: '20px', color: '#666' }}>
          Template will be generated automatically
        </div>
      )}
    </Card>
  );
};

export default DigitalSignatureTemplate;
