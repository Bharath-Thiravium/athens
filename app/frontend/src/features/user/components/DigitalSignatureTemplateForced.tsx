import React, { useState, useEffect } from 'react';
import { Card, Spin, Image, Button, Modal } from 'antd';
import { FileImageOutlined, ReloadOutlined, EyeOutlined } from '@ant-design/icons';
import api from '@common/utils/axiosetup';

const DigitalSignatureTemplate: React.FC = () => {
  const [templateUrl, setTemplateUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [previewVisible, setPreviewVisible] = useState(false);

  const fetchTemplate = async () => {
    try {
      const dataResponse = await api.get('/authentication/signature/template/data/');
      
      if (dataResponse.data.has_existing_template) {
        const previewResponse = await api.get('/authentication/signature/template/preview/');
        if (previewResponse.data.success) {
          setTemplateUrl(previewResponse.data.template_url + '?t=' + Date.now());
        }
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
        <div style={{ textAlign: 'center' }}>
          <Image
            src={templateUrl}
            alt="Digital Signature Template"
            style={{ 
              maxWidth: '100%', 
              maxHeight: '200px',
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
          <div style={{ textAlign: 'center', padding: '20px' }}>
            <Image
              src={templateUrl}
              alt="Digital Signature Template"
              style={{ 
                maxWidth: '100%',
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