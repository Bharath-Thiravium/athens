import React, { useEffect, useMemo, useRef, useState } from 'react';
import { App, Button, Input, Modal, Space, Tabs, Typography } from 'antd';
import { Html5QrcodeScanner } from 'html5-qrcode';

import {
  enqueueAttendanceEvent,
  generateClientEventId,
  getAttendanceDeviceId,
} from '../../../shared/offline/attendanceQueue';

const { Text } = Typography;

type TrainingType = 'INDUCTION' | 'JOB';

interface TrainingCheckInModalProps {
  open: boolean;
  trainingId: number;
  trainingType: TrainingType;
  trainingTitle?: string;
  onClose: () => void;
}

const TrainingCheckInModal: React.FC<TrainingCheckInModalProps> = ({
  open,
  trainingId,
  trainingType,
  trainingTitle,
  onClose,
}) => {
  const { message } = App.useApp();
  const [activeTab, setActiveTab] = useState<'qr' | 'pin'>('qr');
  const [pin, setPin] = useState('');
  const scannerRef = useRef<Html5QrcodeScanner | null>(null);
  const qrReaderId = useMemo(() => `training-qr-reader-${trainingType}-${trainingId}`, [trainingType, trainingId]);

  const stopScanner = () => {
    if (scannerRef.current) {
      scannerRef.current.clear();
      scannerRef.current = null;
    }
  };

  const parseQrToken = (data: string) => {
    if (!data) return null;
    try {
      const decoded = JSON.parse(data);
      return decoded.qr_token || decoded.qrToken || decoded.token || null;
    } catch {
      return data;
    }
  };

  const submitCheckIn = async (method: 'QR' | 'PIN', token: string) => {
    if (!token) {
      message.error('Please provide a valid code.');
      return;
    }

    const event = {
      client_event_id: generateClientEventId(),
      module: 'TRAINING',
      module_ref_id: String(trainingId),
      event_type: 'CHECK_IN',
      occurred_at: new Date().toISOString(),
      device_id: getAttendanceDeviceId(),
      offline: !navigator.onLine,
      method,
      payload: {
        training_type: trainingType,
        ...(method === 'QR' ? { qr_token: token } : { pin: token }),
      },
    };

    await enqueueAttendanceEvent(event);
    message.info(navigator.onLine
      ? 'Check-in queued for sync'
      : 'Recorded offline; will validate when synced');
    setPin('');
    onClose();
  };

  useEffect(() => {
    if (!open || activeTab !== 'qr') {
      stopScanner();
      return;
    }

    setTimeout(() => {
      stopScanner();
      scannerRef.current = new Html5QrcodeScanner(
        qrReaderId,
        { fps: 10, qrbox: { width: 220, height: 220 } },
        false
      );

      scannerRef.current.render(
        (decodedText) => {
          const token = parseQrToken(decodedText);
          if (token) {
            submitCheckIn('QR', token);
          } else {
            message.error('Invalid QR code');
          }
          stopScanner();
        },
        () => {}
      );
    }, 100);

    return () => stopScanner();
  }, [open, activeTab, qrReaderId]);

  useEffect(() => {
    if (!open) {
      stopScanner();
    }
  }, [open]);

  return (
    <Modal
      open={open}
      title={`Training Check-in${trainingTitle ? `: ${trainingTitle}` : ''}`}
      onCancel={onClose}
      footer={null}
      destroyOnClose
    >
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        <Text type="secondary">Check-in via QR code or PIN. No check-out required.</Text>
        <Tabs
          activeKey={activeTab}
          onChange={(key) => setActiveTab(key as 'qr' | 'pin')}
          items={[
            {
              key: 'qr',
              label: 'Scan QR',
              children: (
                <div>
                  <div id={qrReaderId} style={{ width: '100%', minHeight: 260 }} />
                </div>
              ),
            },
            {
              key: 'pin',
              label: 'Enter PIN',
              children: (
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Input
                    placeholder="Enter training PIN"
                    value={pin}
                    onChange={(e) => setPin(e.target.value)}
                  />
                  <Button type="primary" onClick={() => submitCheckIn('PIN', pin)}>
                    Submit PIN
                  </Button>
                </Space>
              ),
            },
          ]}
        />
      </Space>
    </Modal>
  );
};

export default TrainingCheckInModal;
