import React, { useEffect, useMemo, useState } from 'react';
import { App, Divider, Modal, QRCode, Space, Typography } from 'antd';
import api from '@common/utils/axiosetup';

const { Text } = Typography;

type TrainingType = 'INDUCTION' | 'JOB' | 'TBT';

interface TrainingCheckInModalProps {
  open: boolean;
  trainingId: number;
  trainingType: TrainingType;
  trainingTitle?: string;
  onClose: () => void;
}

type TrainingDetails = {
  id: number;
  join_code?: string;
  qr_token?: string;
  qr_expires_at?: string;
};

const TrainingCheckInModal: React.FC<TrainingCheckInModalProps> = ({
  open,
  trainingId,
  trainingType,
  trainingTitle,
  onClose,
}) => {
  const { message } = App.useApp();
  const [trainingDetails, setTrainingDetails] = useState<TrainingDetails | null>(null);

  useEffect(() => {
    if (!open) {
      setTrainingDetails(null);
      return;
    }

    const endpoint = trainingType === 'INDUCTION'
      ? `/induction/${trainingId}/`
      : trainingType === 'JOB'
      ? `/jobtraining/${trainingId}/`
      : `/tbt/${trainingId}/`;

    console.log('Fetching training details from:', endpoint);
    api.get(endpoint)
      .then((response) => {
        console.log('Training details response:', response.data);
        setTrainingDetails(response.data);
      })
      .catch((error) => {
        console.error('Error loading training details:', error);
        message.error('Unable to load training check-in codes.');
      });
  }, [open, trainingId, trainingType, message]);

  const qrValue = useMemo(() => {
    if (!trainingDetails?.qr_token) return '';
    return JSON.stringify({
      training_id: trainingId,
      qr_token: trainingDetails.qr_token,
      training_type: trainingType,
    });
  }, [trainingDetails?.qr_token, trainingId, trainingType]);

  return (
    <Modal
      open={open}
      title={`Training Check-in Codes${trainingTitle ? `: ${trainingTitle}` : ''}`}
      onCancel={onClose}
      footer={null}
      destroyOnClose
      width={400}
    >
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        <div>
          <Text strong>Session Details</Text>
          <div style={{ marginTop: 8 }}>
            <Text>Training Type: <Text code>{trainingType === 'TBT' ? 'Toolbox Talk' : trainingType === 'JOB' ? 'Job Training' : 'Induction Training'}</Text></Text>
          </div>
          <div style={{ marginTop: 4 }}>
            <Text>Training ID: <Text code>{trainingId}</Text></Text>
          </div>
          {trainingDetails?.join_code && (
            <div style={{ marginTop: 4 }}>
              <Text>PIN: <Text code>{trainingDetails.join_code}</Text></Text>
            </div>
          )}
        </div>
        
        {trainingDetails?.qr_token && (
          <>
            <Divider />
            <div style={{ textAlign: 'center' }}>
              <Text type="secondary" style={{ display: 'block', marginBottom: 12 }}>Scan QR Code to Check In</Text>
              <QRCode value={qrValue} size={200} color="#000000" bgColor="#ffffff" />
              {trainingDetails?.qr_expires_at && (
                <Text type="secondary" style={{ display: 'block', marginTop: 8, fontSize: '12px' }}>
                  QR expires: {new Date(trainingDetails.qr_expires_at).toLocaleString()}
                </Text>
              )}
            </div>
          </>
        )}
      </Space>
    </Modal>
  );
};

export default TrainingCheckInModal;
