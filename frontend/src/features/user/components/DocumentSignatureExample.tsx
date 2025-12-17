import React, { useState } from 'react';
import { Card, Button, Space, Image, Typography, DatePicker, Alert, Divider } from 'antd';
import { FileTextOutlined, EditOutlined, DownloadOutlined } from '@ant-design/icons';
import { useDigitalSignature, downloadSignature } from '../hooks/useDigitalSignature';
import moment from 'moment';

const { Title, Text, Paragraph } = Typography;

/**
 * Example component showing how to use digital signatures in documents
 * This can be used as a reference for implementing signatures in other features
 * like Safety Observations, PTW, MOM, etc.
 */
const DocumentSignatureExample: React.FC = () => {
  const { generateSignature, loading } = useDigitalSignature();
  const [signatureUrl, setSignatureUrl] = useState<string | null>(null);
  const [customDateTime, setCustomDateTime] = useState<moment.Moment | null>(null);

  const handleGenerateSignature = async () => {
    const options = customDateTime ? {
      customDateTime: customDateTime.toISOString()
    } : undefined;

    const signature = await generateSignature(options);
    if (signature) {
      setSignatureUrl(signature);
    }
  };

  const handleDownload = () => {
    if (signatureUrl) {
      const timestamp = moment().format('YYYYMMDD_HHmmss');
      downloadSignature(signatureUrl, `signature_${timestamp}.png`);
    }
  };

  return (
    <Card 
      title={
        <Space>
          <FileTextOutlined />
          <span>Digital Signature Example</span>
        </Space>
      }
    >
      <Alert
        message="Digital Signature Demo"
        description="This demonstrates how digital signatures work in the system. The signature includes your name, designation, company logo, and timestamp."
        type="info"
        style={{ marginBottom: 16 }}
      />

      {/* Document Content Simulation */}
      <Card 
        size="small" 
        title="Sample Document" 
        style={{ marginBottom: 16, backgroundColor: '#fafafa' }}
      >
        <Paragraph>
          <Title level={4}>Safety Observation Report</Title>
          <Text>Date: {moment().format('YYYY-MM-DD')}</Text><br />
          <Text>Location: Construction Site A</Text><br />
          <Text>Observer: John Doe</Text>
        </Paragraph>
        
        <Paragraph>
          This is a sample document that would typically require a signature. 
          In the actual system, this could be a Safety Observation, Permit to Work, 
          Meeting Minutes, or any other document requiring authorization.
        </Paragraph>

        <Divider />

        {/* Signature Section */}
        <div style={{ marginTop: 20 }}>
          <Text strong>Digital Signature:</Text>
          {signatureUrl ? (
            <div style={{ marginTop: 10 }}>
              <Image
                src={signatureUrl}
                alt="Digital Signature"
                style={{ 
                  border: '1px solid #d9d9d9',
                  borderRadius: '4px',
                  maxWidth: '300px'
                }}
              />
              <div style={{ marginTop: 8 }}>
                <Button 
                  size="small" 
                  icon={<DownloadOutlined />}
                  onClick={handleDownload}
                >
                  Download Signature
                </Button>
              </div>
            </div>
          ) : (
            <div style={{ 
              marginTop: 10, 
              padding: '20px', 
              border: '2px dashed #d9d9d9',
              borderRadius: '4px',
              textAlign: 'center',
              color: '#999'
            }}>
              Signature will appear here
            </div>
          )}
        </div>
      </Card>

      {/* Signature Controls */}
      <Card size="small" title="Signature Controls">
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <Text>Custom Date/Time (optional):</Text>
            <DatePicker
              showTime
              value={customDateTime}
              onChange={setCustomDateTime}
              style={{ marginLeft: 8, width: 200 }}
              placeholder="Use current time"
            />
          </div>

          <Space>
            <Button
              type="primary"
              icon={<EditOutlined />}
              loading={loading}
              onClick={handleGenerateSignature}
            >
              Generate Digital Signature
            </Button>
            
            {signatureUrl && (
              <Button
                onClick={() => setSignatureUrl(null)}
              >
                Clear Signature
              </Button>
            )}
          </Space>
        </Space>
      </Card>

      {/* Implementation Notes */}
      <Card size="small" title="Implementation Notes" style={{ marginTop: 16 }}>
        <Paragraph>
          <Text strong>For Developers:</Text>
        </Paragraph>
        <ul>
          <li>Use the <code>useDigitalSignature</code> hook in any component that needs signatures</li>
          <li>The signature automatically includes current date/time unless specified</li>
          <li>Signatures can be downloaded or converted to File objects for form uploads</li>
          <li>Each signature is unique with timestamp and user details</li>
          <li>No need to store signature images - they're generated on-demand</li>
        </ul>

        <Paragraph style={{ marginTop: 16 }}>
          <Text strong>Integration Examples:</Text>
        </Paragraph>
        <ul>
          <li><strong>Safety Observations:</strong> Sign off on corrective actions</li>
          <li><strong>Permit to Work:</strong> Approver signatures with timestamps</li>
          <li><strong>Meeting Minutes:</strong> Participant acknowledgments</li>
          <li><strong>Training Records:</strong> Completion certificates</li>
          <li><strong>Incident Reports:</strong> Investigation sign-offs</li>
        </ul>
      </Card>
    </Card>
  );
};

export default DocumentSignatureExample;
