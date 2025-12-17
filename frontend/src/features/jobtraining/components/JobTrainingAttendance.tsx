
import React, { useState, useRef, useEffect } from 'react';
import { Modal, Button, List, Avatar, App, Space, Input, Spin, Result, Typography, Tag, Empty } from 'antd';
import { CheckCircleOutlined, CloseCircleOutlined, CameraOutlined, SearchOutlined, UserOutlined } from '@ant-design/icons';
import Webcam from 'react-webcam';
import api from '@common/utils/axiosetup';
import type { JobTrainingData, JobTrainingAttendanceData } from '../types';
import type { WorkerData } from '@features/worker/types';

const { Title, Text } = Typography;
const { Search } = Input;

interface JobTrainingAttendanceProps {
  jobTraining: JobTrainingData;
  visible: boolean;
  onClose: () => void;
}

const JobTrainingAttendance: React.FC<JobTrainingAttendanceProps> = ({ jobTraining, visible, onClose }) => {
  const {message} = App.useApp();
  const [workers, setWorkers] = useState<WorkerData[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [cameraOpen, setCameraOpen] = useState<boolean>(false);
  const [currentWorker, setCurrentWorker] = useState<WorkerData | null>(null);
  const [photoSrc, setPhotoSrc] = useState<string | null>(null);
  const [matchResult, setMatchResult] = useState<{ matched: boolean; score: number } | null>(null);
  const [attendanceList, setAttendanceList] = useState<JobTrainingAttendanceData[]>([]);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [completed, setCompleted] = useState<boolean>(false);
  const [evidencePhotoSrc, setEvidencePhotoSrc] = useState<string>('');
  const [evidenceCameraOpen, setEvidenceCameraOpen] = useState<boolean>(false);
  const webcamRef = useRef<Webcam>(null);
  const evidenceWebcamRef = useRef<Webcam>(null);

  // Fetch workers when component mounts
  useEffect(() => {
    const fetchWorkers = async () => {
      setLoading(true);
      try {
        // Only fetch workers with "deployed" employment status
        const response = await api.get('/worker/by_employment_status/?status=deployed');
        if (Array.isArray(response.data)) {
          const fetchedWorkers = response.data.map((worker: any) => ({
            key: String(worker.id),
            id: worker.id,
            name: worker.name,
            worker_id: worker.worker_id,
            surname: worker.surname || '',
            photo: worker.photo,
            department: worker.department,
            designation: worker.designation,
            status: worker.status,
            phone_number: worker.phone_number || '',
            email: worker.email || '',
            address: worker.address || '',
            joining_date: worker.joining_date || worker.date_of_joining || '',
            employment_status: worker.employment_status || 'deployed',
            // Add any other required fields from WorkerData
          })) as WorkerData[];
          setWorkers(fetchedWorkers);
        }
      } catch (error) {
        message.error('Failed to fetch workers');
      } finally {
        setLoading(false);
      }
    };

    // Check if there's already attendance data for this Job Training
    const checkExistingAttendance = async () => {
      try {
        const response = await api.get(`/jobtraining/${jobTraining.id}/attendance/`);
        if (response.data && response.data.length > 0) {
          setAttendanceList(response.data);
          if (response.data.some((a: any) => a.status === 'present')) {
            message.info('Some attendance records already exist for this job training.');
          }
        }
      } catch (error) {
      }
    };

    if (visible) {
      fetchWorkers();
      checkExistingAttendance();
    }
  }, [visible, jobTraining.id]);

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  };

  const filteredWorkers = workers.filter(worker => 
    worker.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
    worker.worker_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (worker.surname && worker.surname.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const handleCameraOpen = (worker: WorkerData) => {
    setCurrentWorker(worker);
    setCameraOpen(true);
    setPhotoSrc(null);
    setMatchResult(null);
  };

  const handleCameraClose = () => {
    setCameraOpen(false);
    setCurrentWorker(null);
    setPhotoSrc(null);
    setMatchResult(null);
  };

  const handleEvidenceCameraOpen = () => {
    setEvidenceCameraOpen(true);
  };

  const handleEvidenceCameraClose = () => {
    setEvidenceCameraOpen(false);
  };

  const capturePhoto = () => {
    if (webcamRef.current) {
      const imageSrc = webcamRef.current.getScreenshot();
      setPhotoSrc(imageSrc || '');
      
      // If we have both photos, compare them
      if (imageSrc && currentWorker?.photo) {
        comparePhotos(imageSrc, currentWorker.photo);
      } else {
        message.warning('Reference photo not available for comparison');
        // Still allow marking attendance
        setMatchResult({ matched: false, score: 0 });
      }
    }
  };

  const captureEvidencePhoto = () => {
    if (evidenceWebcamRef.current) {
      const imageSrc = evidenceWebcamRef.current.getScreenshot();
      setEvidencePhotoSrc(imageSrc || '');
      setEvidenceCameraOpen(false);
    }
  };

  const comparePhotos = async (_capturedPhoto: string, _referencePhoto: string) => {
    try {
      // In a real implementation, you would send both photos to your backend API
      // for comparison using a facial recognition service
      // For this example, we'll simulate a response
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Simulate a match result (random score between 70-100)
      const simulatedScore = Math.floor(Math.random() * 31) + 70;
      const matched = simulatedScore > 80;
      
      setMatchResult({ matched, score: simulatedScore });
      
      if (matched) {
        message.success(`Match confirmed! Confidence: ${simulatedScore}%`);
      } else {
        message.error(`Match failed. Confidence: ${simulatedScore}%`);
      }
    } catch (error) {
      message.error('Failed to compare photos');
      setMatchResult({ matched: false, score: 0 });
    }
  };

  const markAttendance = (worker: WorkerData, present: boolean) => {
    // Create a new attendance record
    const newAttendance: JobTrainingAttendanceData = {
      id: 0, // Will be assigned by backend
      key: `temp-${worker.id}`,
      job_training_id: jobTraining.id,
      worker_id: worker.id,
      worker_name: `${worker.name} ${worker.surname || ''}`,
      worker_photo: worker.photo || '',
      attendance_photo: photoSrc || '',
      status: present ? 'present' : 'absent',
      timestamp: new Date().toISOString(),
      match_score: matchResult?.score || 0
    };
    
    // Update local state
    setAttendanceList(prev => {
      // Remove any existing record for this worker
      const filtered = prev.filter(a => a.worker_id !== worker.id);
      // Add the new record
      return [...filtered, newAttendance];
    });
    
    // Close the camera modal
    setCameraOpen(false);
    setCurrentWorker(null);
    setPhotoSrc(null);
    setMatchResult(null);
    
    message.success(`${worker.name} marked as ${present ? 'present' : 'absent'}`);
  };

  const getAttendanceStatus = (workerId: number) => {
    const record = attendanceList.find(a => a.worker_id === workerId);
    return record ? record.status : null;
  };

  const handleSubmit = async () => {
    if (attendanceList.length === 0) {
      message.error('Please mark attendance for at least one worker');
      return;
    }
    
    setSubmitting(true);
    
    try {
      // Submit all attendance records to the backend
      await api.post(`/jobtraining/${jobTraining.id}/attendance/`, {
        job_training_id: jobTraining.id,
        attendance_records: attendanceList,
        evidence_photo: evidencePhotoSrc
      });
      
      // The backend will update the status to completed automatically
      // No need for a separate PUT request
      
      message.success('Attendance submitted successfully');
      setCompleted(true);
    } catch (error) {
      message.error('Failed to submit attendance');
    } finally {
      setSubmitting(false);
    }
  };

  const isWorkerMarked = (workerId: number) => {
    return attendanceList.some(a => a.worker_id === workerId);
  };

  // Render the evidence camera modal
  const renderEvidenceCameraModal = () => (
    <Modal
      open={evidenceCameraOpen}
      title="Take Group Photo for Evidence"
      onCancel={handleEvidenceCameraClose}
      footer={[
        <Button key="back" onClick={handleEvidenceCameraClose}>
          Cancel
        </Button>,
        <Button key="submit" type="primary" onClick={captureEvidencePhoto}>
          Capture
        </Button>,
      ]}
      width={650}
    >
      <div style={{ textAlign: 'center' }}>
        <Webcam
          audio={false}
          ref={evidenceWebcamRef}
          screenshotFormat="image/jpeg"
          width={600}
          height={450}
          videoConstraints={{
            width: 600,
            height: 450,
            facingMode: "user"
          }}
          style={{ marginBottom: 16 }}
        />
      </div>
    </Modal>
  );

  return (
    <Modal
      open={visible}
      title={`Take Attendance: ${jobTraining.title}`}
      onCancel={onClose}
      footer={[
        <Button key="cancel" onClick={onClose} disabled={submitting}>
          {completed ? 'Close' : 'Cancel'}
        </Button>,
        !completed && (
          <Button 
            key="submit" 
            type="primary" 
            onClick={handleSubmit}
            loading={submitting}
            disabled={attendanceList.length === 0}
          >
            Submit Attendance
          </Button>
        )
      ]}
      width={800}
      destroyOnClose
    >
      {completed ? (
        <Result
          status="success"
          title="Attendance Submitted Successfully"
          subTitle={`All attendance records for "${jobTraining.title}" have been saved.`}
        />
      ) : (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Search
            placeholder="Search workers by name or ID"
            allowClear
            enterButton={<SearchOutlined />}
            size="large"
            onSearch={value => setSearchTerm(value)}
            onChange={handleSearch}
          />
          
          <div style={{ marginBottom: 16 }}>
            <Title level={5}>Attendance Summary</Title>
            <Text>
              Total Workers: {workers.length} | 
              Present: {attendanceList.filter(a => a.status === 'present').length} | 
              Absent: {attendanceList.filter(a => a.status === 'absent').length} | 
              Unmarked: {workers.length - attendanceList.length}
            </Text>
          </div>
          
          <List
            loading={loading}
            dataSource={filteredWorkers}
            renderItem={worker => {
              const isMarked = isWorkerMarked(worker.id);
              const status = getAttendanceStatus(worker.id);
              
              return (
                <List.Item
                  actions={[
                    isMarked ? (
                      status === 'present' ? (
                        <Tag color="success" icon={<CheckCircleOutlined />}>Present</Tag>
                      ) : (
                        <Tag color="error" icon={<CloseCircleOutlined />}>Absent</Tag>
                      )
                    ) : (
                      <Button 
                        type="primary" 
                        icon={<CameraOutlined />} 
                        onClick={() => handleCameraOpen(worker)}
                      >
                        Take Photo
                      </Button>
                    )
                  ]}
                >
                  <List.Item.Meta
                    avatar={
                      worker.photo ? (
                        <Avatar src={worker.photo} size={48} />
                      ) : (
                        <Avatar icon={<UserOutlined />} size={48} />
                      )
                    }
                    title={`${worker.name} ${worker.surname || ''}`}
                    description={
                      <Space direction="vertical" size={0}>
                        <Text type="secondary">ID: {worker.worker_id}</Text>
                        <Text type="secondary">{worker.designation}, {worker.department}</Text>
                      </Space>
                    }
                  />
                </List.Item>
              );
            }}
            pagination={{
              pageSize: 10,
              size: 'small',
              showSizeChanger: false
            }}
          />
          
          {/* Camera Modal for taking attendance photos */}
          <Modal
            open={cameraOpen}
            title={`Take Photo of ${currentWorker?.name || 'Worker'}`}
            onCancel={handleCameraClose}
            footer={[
              <Button key="back" onClick={handleCameraClose}>
                Cancel
              </Button>,
              photoSrc ? (
                <Button key="retake" onClick={() => setPhotoSrc(null)}>
                  Retake Photo
                </Button>
              ) : (
                <Button key="capture" type="primary" onClick={capturePhoto}>
                  Capture
                </Button>
              ),
            ]}
            width={650}
          >
            <div style={{ textAlign: 'center' }}>
              {!photoSrc ? (
                <Webcam
                  audio={false}
                  ref={webcamRef}
                  screenshotFormat="image/jpeg"
                  width={600}
                  height={450}
                  videoConstraints={{
                    width: 600,
                    height: 450,
                    facingMode: "user"
                  }}
                />
              ) : (
                <>
                  {matchResult ? (
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
                        <div style={{ textAlign: 'center', flex: 1 }}>
                          <Title level={5}>Reference Photo</Title>
                          <Avatar 
                            src={currentWorker?.photo} 
                            size={200} 
                            icon={<UserOutlined />}
                            style={{ marginBottom: 8 }}
                          />
                          <div>
                            <Text>{currentWorker?.name} {currentWorker?.surname}</Text>
                          </div>
                        </div>
                        <div style={{ textAlign: 'center', flex: 1 }}>
                          <Title level={5}>Captured Photo</Title>
                          <Avatar 
                            src={photoSrc} 
                            size={200}
                            style={{ marginBottom: 8 }}
                          />
                        </div>
                      </div>
                      
                      <div style={{ marginTop: 16, textAlign: 'center' }}>
                        <Title level={4}>
                          Match Result: {matchResult.matched ? 'Success' : 'Failed'}
                        </Title>
                        <Text>Confidence Score: {matchResult.score}%</Text>
                        
                        <div style={{ marginTop: 16 }}>
                          <Space>
                            <Button 
                              type="primary" 
                              icon={<CheckCircleOutlined />} 
                              onClick={() => currentWorker && markAttendance(currentWorker, true)}
                              style={{ backgroundColor: '#52c41a', borderColor: '#52c41a' }}
                            >
                              Mark Present
                            </Button>
                            <Button 
                              danger 
                              icon={<CloseCircleOutlined />} 
                              onClick={() => currentWorker && markAttendance(currentWorker, false)}
                            >
                              Mark Absent
                            </Button>
                            <Button onClick={() => setPhotoSrc(null)}>Retake Photo</Button>
                          </Space>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <Spin tip="Comparing photos...">
                      <div style={{ height: 100 }} />
                    </Spin>
                  )}
                </>
              )}
            </div>
          </Modal>
          
          {renderEvidenceCameraModal()}
          
          {/* Evidence Photo Section */}
          <div style={{ marginTop: 24, marginBottom: 24, border: '1px solid #f0f0f0', padding: 16, borderRadius: 8 }}>
            <Title level={5}>Evidence Photo</Title>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              {evidencePhotoSrc ? (
                <div style={{ marginBottom: 16 }}>
                  <img 
                    src={evidencePhotoSrc} 
                    alt="Group Evidence" 
                    style={{ width: '100%', maxWidth: 600, objectFit: 'cover', borderRadius: 4 }} 
                  />
                </div>
              ) : (
                <div style={{ marginBottom: 16 }}>
                  <Empty description="No evidence photo taken" />
                </div>
              )}
              <Button 
                type="primary" 
                icon={<CameraOutlined />} 
                onClick={handleEvidenceCameraOpen}
              >
                {evidencePhotoSrc ? 'Retake Evidence Photo' : 'Take Evidence Photo'}
              </Button>
            </div>
          </div>
        </Space>
      )}
    </Modal>
  );
};

export default JobTrainingAttendance;
