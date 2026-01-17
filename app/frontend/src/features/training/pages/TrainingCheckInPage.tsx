import React, { useEffect, useMemo, useRef, useState } from 'react';
import { App, Button, Card, Input, Space, Tag, Typography } from 'antd';
import { Html5QrcodeScanner } from 'html5-qrcode';
import { useSearchParams } from 'react-router-dom';
import PageLayout from '@common/components/PageLayout';

import {
  enqueueAttendanceEvent,
  generateClientEventId,
  getAttendanceDeviceId,
} from '../../../shared/offline/attendanceQueue';

const { Text, Title } = Typography;

type TrainingType = 'INDUCTION' | 'JOB';

type ParsedQr = {
  trainingId?: string;
  token?: string;
  trainingType?: TrainingType;
};

const TrainingCheckInPage: React.FC = () => {
  const { message } = App.useApp();
  const [searchParams] = useSearchParams();
  const [trainingId, setTrainingId] = useState('');
  const [qrToken, setQrToken] = useState('');
  const [pin, setPin] = useState('');
  const [scanning, setScanning] = useState(false);
  const scannerRef = useRef<Html5QrcodeScanner | null>(null);

  const qrReaderId = useMemo(() => 'training-checkin-qr', []);

  useEffect(() => {
    const id = searchParams.get('id');
    if (id) {
      setTrainingId(id);
    }
  }, [searchParams]);

  const clearScanner = () => {
    if (scannerRef.current) {
      scannerRef.current.clear();
      scannerRef.current = null;
    }
  };

  const parseQrData = (data: string): ParsedQr => {
    if (!data) return {};
    try {
      const decoded = JSON.parse(data);
      const rawType = decoded.training_type || decoded.trainingType;
      const normalizedType = typeof rawType === 'string' ? rawType.trim().toUpperCase() : '';
      return {
        trainingId: decoded.training_id || decoded.trainingId || decoded.id ? String(decoded.training_id || decoded.trainingId || decoded.id) : undefined,
        token: decoded.qr_token || decoded.qrToken || decoded.token || decoded.code,
        trainingType: normalizedType === 'INDUCTION' || normalizedType === 'JOB' ? (normalizedType as TrainingType) : undefined,
      };
    } catch {
      return { token: data };
    }
  };

  const submitCheckIn = async (
    method: 'QR' | 'PIN',
    token: string,
    selectedId: string,
    overrideType?: TrainingType
  ) => {
    if (!selectedId) {
      message.error('Enter a training ID first.');
      return;
    }
    if (!token) {
      message.error('Provide a valid QR token or PIN.');
      return;
    }

    const normalizedId = Number(selectedId);
    if (!Number.isFinite(normalizedId) || normalizedId <= 0) {
      message.error('Training ID must be a valid number.');
      return;
    }

    await enqueueAttendanceEvent({
      client_event_id: generateClientEventId(),
      module: 'TRAINING',
      module_ref_id: String(normalizedId),
      event_type: 'CHECK_IN',
      occurred_at: new Date().toISOString(),
      device_id: getAttendanceDeviceId(),
      offline: !navigator.onLine,
      method,
      payload: {
        ...(overrideType ? { training_type: overrideType } : {}),
        ...(method === 'QR' ? { qr_token: token } : { pin: token }),
      },
    });

    message.info(navigator.onLine
      ? 'Check-in queued for sync'
      : 'Recorded offline; will validate when synced');
    setPin('');
  };

  const handleStartScan = () => {
    setScanning(true);
  };

  const handleStopScan = () => {
    setScanning(false);
    clearScanner();
  };

  useEffect(() => {
    if (!scanning) {
      clearScanner();
      return;
    }

    setTimeout(() => {
      clearScanner();
      scannerRef.current = new Html5QrcodeScanner(
        qrReaderId,
        { 
          fps: 10, 
          qrbox: { width: 250, height: 250 },
          rememberLastUsedCamera: true,
          useBarCodeDetectorIfSupported: true
        },
        false
      );

      scannerRef.current.render(
        (decodedText) => {
          const parsed = parseQrData(decodedText);
          if (parsed.trainingId) {
            setTrainingId(parsed.trainingId);
          }
          if (parsed.token) {
            setQrToken(parsed.token);
            const resolvedId = parsed.trainingId || trainingId;
            if (resolvedId) {
              submitCheckIn('QR', parsed.token, resolvedId, parsed.trainingType);
            } else {
              message.info('Enter training ID to submit QR.');
            }
          } else {
            message.error('Invalid QR code');
          }
          setScanning(false);
          clearScanner();
        },
        (error) => {
          if (error.includes('Permission') || error.includes('NotAllowed') || error.includes('NotFound')) {
            message.error('Camera access denied or not available. Please check permissions.');
            setScanning(false);
            clearScanner();
          }
        }
      );
    }, 200);

    return () => clearScanner();
  }, [scanning, qrReaderId, trainingId]);

  useEffect(() => {
    return () => clearScanner();
  }, []);

  return (
    <PageLayout
      title="Training Check-in"
      subtitle="Enter Training ID + PIN or scan a QR code to mark attendance"
      breadcrumbs={[{ title: 'Training' }, { title: 'Check-in' }]}
    >
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {!navigator.onLine && <Tag color="orange">Offline mode - will sync when online</Tag>}

        <Card>
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            <Title level={5}>Training ID + PIN</Title>
            <div>
              <Text strong>Training ID:</Text>
              <Input
                placeholder="Enter Training ID"
                value={trainingId}
                onChange={(e) => setTrainingId(e.target.value)}
                style={{ marginTop: 4 }}
              />
              <Text type="secondary" style={{ fontSize: '12px', display: 'block', marginTop: 4 }}>Training ID is required for attendance validation.</Text>
            </div>
            <div>
              <Text strong>PIN:</Text>
              <Input
                placeholder="Enter PIN"
                value={pin}
                onChange={(e) => setPin(e.target.value)}
                style={{ marginTop: 4 }}
              />
            </div>
            <Button type="primary" onClick={() => submitCheckIn('PIN', pin, trainingId)}>
              Submit PIN
            </Button>
          </Space>
        </Card>

        <Card>
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            <Title level={5}>Scan QR Code</Title>
            <div id={qrReaderId} style={{ width: '100%', minHeight: 260 }} />
            <Space>
              <Button type="primary" onClick={handleStartScan} disabled={scanning}>
                {scanning ? 'Scanning...' : 'Start Camera Scan'}
              </Button>
              <Button onClick={handleStopScan} disabled={!scanning}>
                Stop Scan
              </Button>
            </Space>
            {scanning && (
              <Text type="secondary" style={{ fontSize: '12px' }}>
                📷 Allow camera access when prompted. Point camera at QR code to scan.
              </Text>
            )}
            {qrToken && <Text type="secondary">Last QR token: {qrToken}</Text>}
            {qrToken && trainingId && (
              <Button onClick={() => submitCheckIn('QR', qrToken, trainingId)}>
                Submit QR Token
              </Button>
            )}
          </Space>
        </Card>
      </Space>
    </PageLayout>
  );
};

export default TrainingCheckInPage;
