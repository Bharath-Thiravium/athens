import React, { useState, useEffect } from 'react';
import { Card, Spin, Image, Button, Modal } from 'antd';
import { FileImageOutlined, ReloadOutlined, EyeOutlined } from '@ant-design/icons';
import api from '@common/utils/axiosetup';
import { fetchSignaturePreviewUrl } from '@common/utils/signaturePreview';

const DigitalSignatureTemplate: React.FC = () => {
  const [templateUrl, setTemplateUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [previewVisible, setPreviewVisible] = useState(false);

  useEffect(() => {
    return () => {
      if (templateUrl && templateUrl.startsWith('blob:')) {
        URL.revokeObjectURL(templateUrl);
      }
    };
  }, [templateUrl]);

  const fetchTemplate = async () => {
    try {
      const dataResponse = await api.get('/authentication/signature/template/data/');
      
      if (dataResponse.data.has_existing_template) {
        const previewUrl = await fetchSignaturePreviewUrl();
        setTemplateUrl(previewUrl);
      } else {
        setTemplateUrl(null);
      }
    } catch (error) {
      console.error('Error fetching template:', error);
    } finally {
      setLoading(false);
    }
  };

  const createTemplate = async () => {
    setCreating(true);
    try {
      await api.post('/authentication/signature/template/create/');
      await fetchTemplate();
    } catch (error) {
      console.error('Error creating template:', error);
    } finally {
      setCreating(false);
    }
  };

  useEffect(() => {
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
      extra={
        <div style={{ display: 'flex', gap: '8px' }}>
          {templateUrl && (
            <Button 
              icon={<EyeOutlined />} 
              onClick={() => setPreviewVisible(true)}
            >
              Preview
            </Button>
          )}
          <Button 
            icon={<ReloadOutlined />} 
            onClick={fetchTemplate}
            loading={creating}
          >
            Refresh
          </Button>
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
        <div style={{ textAlign: 'center', padding: '20px' }}>
          <div style={{ color: '#666', marginBottom: '16px' }}>
            No template found
          </div>
          <Button 
            type="primary" 
            onClick={createTemplate}
            loading={creating}
          >
            Generate Template
          </Button>
        </div>
      )}

      <Modal
        title="Signature Template Preview"
        open={previewVisible}
        onCancel={() => setPreviewVisible(false)}
        footer={[
          <Button key="close" onClick={() => setPreviewVisible(false)}>
            Close
          </Button>
        ]}
        width={600}
        centered
      >
        {templateUrl && (
          <div className="ds-preview-wrap">
            <Image
              wrapperClassName="ds-preview-wrapper"
              className="ds-preview-img"
              src={templateUrl}
              alt="Digital Signature Template"
              style={{ 
                maxWidth: '100%',
                height: 'auto',
                border: '1px solid #d9d9d9',
                borderRadius: '6px'
              }}
              preview={false}
            />
          </div>
        )}
      </Modal>
    </Card>
  );
};

export default DigitalSignatureTemplate;
