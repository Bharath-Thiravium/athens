import React, { useState, useEffect } from 'react';
// CORRECT: Using App for the hook
import { Button, App, Card, Typography, Spin, Tag, Upload, Modal, Breadcrumb } from 'antd';
import { EnvironmentOutlined, CheckCircleOutlined, ClockCircleOutlined, UploadOutlined, HomeOutlined } from '@ant-design/icons';
import api from '@common/utils/axiosetup';
import useAuthStore from '@common/store/authStore';
import PageLayout from '@common/components/PageLayout';
import { enqueueAttendanceEvent, generateClientEventId, getAttendanceDeviceId } from '../../../shared/offline/attendanceQueue';

const { Title, Text } = Typography;

const ProjectAttendance: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [attendanceStatus, setAttendanceStatus] = useState<string>('Not Checked In');
  const [lastActionTime, setLastActionTime] = useState<string | null>(null);
  const [checkedIn, setCheckedIn] = useState<boolean>(false);
  const [photoModalVisible, setPhotoModalVisible] = useState(false);
  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
  const [actionType, setActionType] = useState<'check-in' | 'check-out' | null>(null);
  const [gpsAccuracy, setGpsAccuracy] = useState<number | null>(null);

  const { message } = App.useApp();
  const projectId = useAuthStore((state) => state.projectId);

  // Function to check current attendance status from server
  const checkAttendanceStatus = async () => {
    if (!projectId) return;

    try {
      const response = await api.get(`authentication/api/attendance/status/${projectId}/`);
      const serverStatus = response.data;

      if (serverStatus.status === 'checked_in') {
        setCheckedIn(true);
        setAttendanceStatus('Checked In');
        if (serverStatus.check_in_time) {
          const time = new Date(serverStatus.check_in_time).toLocaleTimeString('en-US', {
            hour12: true,
            hour: 'numeric',
            minute: '2-digit'
          });
          setLastActionTime(time);
        }
      } else if (serverStatus.status === 'checked_out') {
        setCheckedIn(false);
        setAttendanceStatus('Checked Out');
        if (serverStatus.check_out_time) {
          const time = new Date(serverStatus.check_out_time).toLocaleTimeString('en-US', {
            hour12: true,
            hour: 'numeric',
            minute: '2-digit'
          });
          setLastActionTime(time);
        }
      } else {
        setCheckedIn(false);
        setAttendanceStatus('Not Checked In');
        setLastActionTime(null);
      }
    } catch (error) {
      // If no attendance found for today, reset to default state
      setCheckedIn(false);
      setAttendanceStatus('Not Checked In');
      setLastActionTime(null);
    }
  };

  const applyLocalAttendanceStatus = (status: 'checked_in' | 'checked_out') => {
    const time = new Date().toLocaleTimeString('en-US', {
      hour12: true,
      hour: 'numeric',
      minute: '2-digit',
      second: '2-digit'
    });
    const currentDate = new Date().toDateString();

    setAttendanceStatus(status === 'checked_in' ? 'Checked In' : 'Checked Out');
    setLastActionTime(time);
    setCheckedIn(status === 'checked_in');
    localStorage.setItem('attendanceStatus', status);
    localStorage.setItem('attendanceTime', time);
    localStorage.setItem('attendanceDate', currentDate);
  };

  const buildAttendanceEvent = (params: {
    latitude: number;
    longitude: number;
    accuracy?: number;
    method: 'FACE' | 'SELF_CONFIRM';
    payload?: Record<string, any>;
  }) => {
    if (!actionType) return null;
    return {
      client_event_id: generateClientEventId(),
      module: 'REGULAR',
      module_ref_id: projectId ? String(projectId) : null,
      event_type: actionType === 'check-in' ? 'CHECK_IN' : 'CHECK_OUT',
      occurred_at: new Date().toISOString(),
      device_id: getAttendanceDeviceId(),
      offline: !navigator.onLine,
      method: params.method,
      location: {
        lat: params.latitude,
        lng: params.longitude,
        accuracy: params.accuracy,
        source: 'gps'
      },
      payload: params.payload || {}
    };
  };

  useEffect(() => {
    // Load attendance status from localStorage with date validation
    const storedStatus = localStorage.getItem('attendanceStatus');
    const storedTime = localStorage.getItem('attendanceTime');
    const storedDate = localStorage.getItem('attendanceDate');
    const currentDate = new Date().toDateString(); // Get current date string

    // Check if stored data is from today
    if (storedDate === currentDate) {
      if (storedStatus === 'checked_in') {
        setCheckedIn(true);
        setAttendanceStatus('Checked In');
        if (storedTime) setLastActionTime(storedTime);
      } else if (storedStatus === 'checked_out') {
        setCheckedIn(false);
        setAttendanceStatus('Checked Out');
        if (storedTime) setLastActionTime(storedTime);
      } else {
        setCheckedIn(false);
        setAttendanceStatus('Not Checked In');
        setLastActionTime(null);
      }
    } else {
      // Clear old data if it's from a previous day (reset at midnight)
      localStorage.removeItem('attendanceStatus');
      localStorage.removeItem('attendanceTime');
      localStorage.removeItem('attendanceDate');
      setCheckedIn(false);
      setAttendanceStatus('Not Checked In');
      setLastActionTime(null);
    }

    // Also check server status to ensure synchronization
    checkAttendanceStatus();
  }, [projectId]);

  // Reset only the camera/photo (for retaking photo)
  const resetCamera = () => {

    // Show loading state while restarting camera
    setLoading(true);

    // Clear photo states first
    setPhotoFile(null);
    setPhotoPreview(null);

    // Check if camera is supported
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      message.error('Camera not supported on this device or browser.');
      setLoading(false);
      return;
    }

    // Function to restart camera
    const restartCamera = () => {
      const video = document.getElementById('video') as HTMLVideoElement | null;

      if (!video) {
        // Retry after a short delay in case the DOM is updating
        setTimeout(restartCamera, 200);
        return;
      }


      // Stop current stream if exists
      if (video.srcObject) {
        const stream = video.srcObject as MediaStream;
        const tracks = stream.getTracks();
        tracks.forEach(track => {
          track.stop();
        });
        video.srcObject = null;
      }


      // Start new camera stream
      navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user' // Use front camera by default
        }
      })
        .then((stream) => {
          video.srcObject = stream;

          // Ensure video plays after stream is set
          video.onloadedmetadata = () => {
            video.play()
              .then(() => {
                setLoading(false);
              })
              .catch(err => {
                message.error('Failed to start camera preview.');
                setLoading(false);
              });
          };
        })
        .catch((err) => {

          // Provide specific error messages
          let errorMessage = 'Failed to restart camera. Please try again.';
          if (err.name === 'NotAllowedError') {
            errorMessage = 'Camera access denied. Please allow camera permissions and try again.';
          } else if (err.name === 'NotFoundError') {
            errorMessage = 'No camera found on this device.';
          } else if (err.name === 'NotReadableError') {
            errorMessage = 'Camera is already in use by another application.';
          }

          message.error(errorMessage);
          setLoading(false);
        });
    };

    // Start the restart process with a small delay to ensure DOM is ready
    setTimeout(restartCamera, 100);
  };

  // Close the entire modal (cancel attendance action)
  const resetPhotoModal = () => {
    setPhotoFile(null);
    setPhotoPreview(null);
    setPhotoModalVisible(false);
    setActionType(null);
  };

  const capturePhoto = () => {
    const video = document.getElementById('video') as HTMLVideoElement | null;
    if (!video) {
      message.error('Video element not found');
      return;
    }

    // Check if video is actually playing and has dimensions
    if (video.videoWidth === 0 || video.videoHeight === 0) {
      message.error('Camera not ready. Please wait for the camera to load.');
      return;
    }

    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    if (!ctx) {
      message.error('Cannot create canvas context');
      return;
    }

    try {
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      canvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], `attendance-photo-${Date.now()}.jpg`, { type: 'image/jpeg' });
          setPhotoFile(file);
          const reader = new FileReader();
          reader.onload = (e) => {
            setPhotoPreview(e.target?.result as string);
          };
          reader.readAsDataURL(file);
          message.success('Photo captured successfully!');
        } else {
          message.error('Failed to capture photo');
        }
      }, 'image/jpeg', 0.8); // Add quality parameter
    } catch (error) {
      message.error('Failed to capture photo');
    }
  };

  const handleCheckInOut = () => {
    if (!projectId) {
      message.error("No project assigned to your account. Cannot mark attendance.");
      return;
    }
    if (!navigator.geolocation) {
      message.error('Geolocation is not supported by your browser.');
      return;
    }
    setLoading(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLoading(false);
        setGpsAccuracy(position.coords.accuracy);
        setActionType(checkedIn ? 'check-out' : 'check-in');
        setPhotoModalVisible(true);

        // Show GPS accuracy info
        if (position.coords.accuracy > 50) {
          message.warning(`GPS accuracy is ${position.coords.accuracy.toFixed(0)}m. For better accuracy, move to an open area.`);
        }
      },
      (error) => {
        setLoading(false);
        let locationError = 'Unable to retrieve your location.';

        switch (error.code) {
          case error.PERMISSION_DENIED:
            locationError = '📍 Location Permission Denied: Please allow location access and try again.';
            break;
          case error.POSITION_UNAVAILABLE:
            locationError = '📍 Location Unavailable: Your location information is unavailable. Please check your GPS settings.';
            break;
          case error.TIMEOUT:
            locationError = '📍 Location Timeout: Location request timed out. Please try again.';
            break;
          default:
            locationError = `📍 Location Error: ${error.message}`;
            break;
        }

        message.error(locationError);
      },
      {
        enableHighAccuracy: true,
        timeout: 20000,
        maximumAge: 60000 // Allow 1 minute old location to reduce GPS variations
      }
    );
  };

  const submitAttendance = async () => {
    if (!photoFile) {
      message.error('📸 Photo Required: Please capture a photo before submitting attendance.');
      return;
    }

    if (!projectId) {
      message.error('🏗️ Project Required: No project assigned to your account. Please contact administrator.');
      return;
    }
    
    setLoading(true);

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        try {
          const { latitude, longitude, accuracy } = position.coords;
          const payload = {
            photo_data_url: photoPreview,
            action: actionType,
          };

          if (!navigator.onLine) {
            const offlineEvent = buildAttendanceEvent({
              latitude,
              longitude,
              accuracy,
              method: 'FACE',
              payload: { ...payload, offline_reason: 'no_network' }
            });

            if (offlineEvent) {
              await enqueueAttendanceEvent(offlineEvent);
            }

            if (actionType) {
              applyLocalAttendanceStatus(actionType === 'check-in' ? 'checked_in' : 'checked_out');
            }
            message.info('Saved offline — will sync when online');
            resetPhotoModal();
            return;
          }

          const formData = new FormData();
          
          formData.append('project_id', projectId.toString());
          formData.append('latitude', latitude.toString());
          formData.append('longitude', longitude.toString());
          formData.append('photo', photoFile);

          const endpoint = actionType === 'check-in' ? 'authentication/api/attendance/check-in/' : 'authentication/api/attendance/check-out/';
          const response = await api.post(endpoint, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
          });

          const status = response.data.status;
          if (status === 'checked_in' || status === 'checked_out') {
            applyLocalAttendanceStatus(status);
          }
          const onlineEvent = buildAttendanceEvent({
            latitude,
            longitude,
            accuracy,
            method: 'FACE',
            payload: { ...payload, server_status: status }
          });
          if (onlineEvent) {
            await enqueueAttendanceEvent(onlineEvent);
          }
          message.success(`${status === 'checked_in' ? 'Check-in' : 'Check-out'} successful!`);
          resetPhotoModal();
        } catch (error: any) {
          let errorMsg = 'Failed to mark attendance.';
          let faceMismatch = false;

          if (error.response?.data?.error) {
            const serverError = error.response.data.error;

            // Check for specific error types and provide user-friendly messages
            if (serverError.includes('Face not matched') || serverError.includes('face not recognized')) {
              errorMsg = '❌ Face Recognition Failed: Your face does not match our records. Please ensure good lighting and try again.';
              faceMismatch = true;
            } else if (serverError.includes('Location Error') || serverError.includes('300 meters')) {
              errorMsg = '📍 Location Error: You are too far from the project site. Please move closer (within 300 meters) and try again.';
            } else if (serverError.includes('Project location not configured')) {
              errorMsg = '🏗️ Project Setup Error: Project location coordinates are not configured. Please contact administrator.';
            } else if (serverError.includes('No user photo found') || serverError.includes('No admin photo found')) {
              errorMsg = '📷 Profile Photo Missing: Please update your profile photo first before marking attendance.';
            } else if (serverError.includes('Admin profile not found') || serverError.includes('User profile not found')) {
              errorMsg = '👤 Profile Missing: Please complete your profile first before marking attendance.';
            } else if (serverError.includes('Camera') || serverError.includes('photo')) {
              errorMsg = '📸 Photo Error: ' + serverError;
            } else {
              errorMsg = serverError;
            }
          }

          if (faceMismatch) {
            Modal.confirm({
              title: 'Face match failed',
              content: 'Mark attendance anyway? This will be saved as self-confirmed and synced later.',
              okText: 'Mark attendance',
              cancelText: 'Try again',
              onOk: async () => {
                const fallbackEvent = buildAttendanceEvent({
                  latitude,
                  longitude,
                  accuracy,
                  method: 'SELF_CONFIRM',
                  payload: { fallback_reason: 'face_mismatch' }
                });
                if (fallbackEvent) {
                  await enqueueAttendanceEvent(fallbackEvent);
                }
                if (actionType) {
                  applyLocalAttendanceStatus(actionType === 'check-in' ? 'checked_in' : 'checked_out');
                }
                message.info('Saved as self-confirmed attendance; will sync when online');
                resetPhotoModal();
              }
            });
            return;
          }

          message.error(errorMsg);
        } finally {
          setLoading(false);
        }
      },
      (error) => {
        let locationError = 'Unable to retrieve your location.';

        switch (error.code) {
          case error.PERMISSION_DENIED:
            locationError = '📍 Location Permission Denied: Please allow location access and try again.';
            break;
          case error.POSITION_UNAVAILABLE:
            locationError = '📍 Location Unavailable: Your location information is unavailable. Please check your GPS settings.';
            break;
          case error.TIMEOUT:
            locationError = '📍 Location Timeout: Location request timed out. Please try again.';
            break;
          default:
            locationError = `📍 Location Error: ${error.message}`;
            break;
        }

        message.error(locationError);
        setLoading(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 20000,
        maximumAge: 60000 // Allow 1 minute old location to reduce GPS variations
      }
    );
  };

  useEffect(() => {
    if (photoModalVisible) {
      // Add a small delay to ensure the video element is rendered
      const timer = setTimeout(() => {
        const video = document.getElementById('video') as HTMLVideoElement | null;
        if (video && navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
          navigator.mediaDevices.getUserMedia({
            video: {
              width: { ideal: 640 },
              height: { ideal: 480 },
              facingMode: 'user' // Use front camera by default
            }
          })
            .then((stream) => {
              video.srcObject = stream;
              // Ensure video plays after stream is set
              video.onloadedmetadata = () => {
                video.play().catch(err => {
                  message.error('Failed to start camera preview.');
                });
              };
            })
            .catch((err) => {
              let errorMessage = 'Cannot access camera. Please allow camera permissions.';

              // Provide more specific error messages
              if (err.name === 'NotAllowedError') {
                errorMessage = 'Camera access denied. Please allow camera permissions and try again.';
              } else if (err.name === 'NotFoundError') {
                errorMessage = 'No camera found on this device.';
              } else if (err.name === 'NotReadableError') {
                errorMessage = 'Camera is already in use by another application.';
              }

              message.error(errorMessage);
              resetPhotoModal();
            });
        } else {
          message.error('Camera not supported on this device or browser.');
          resetPhotoModal();
        }
      }, 100); // Small delay to ensure DOM is ready

      return () => clearTimeout(timer);
    } else {
      const video = document.getElementById('video') as HTMLVideoElement | null;
      if (video && video.srcObject) {
        const stream = video.srcObject as MediaStream;
        const tracks = stream.getTracks();
        tracks.forEach(track => track.stop());
        video.srcObject = null;
      }
    }
  }, [photoModalVisible, message]);

  return (
    <div className="space-y-6" style={{ paddingTop: 80 }}>
      <Breadcrumb 
        style={{ marginBottom: 16 }}
        items={[
          {
            title: (
              <a href="/dashboard" style={{ color: 'inherit', textDecoration: 'none' }}>
                <HomeOutlined />
              </a>
            )
          },
          {
            title: 'Attendance'
          }
        ]}
      />
      <div className="flex flex-wrap justify-between items-center gap-4">
        <Title level={3} className="!mb-0 !text-color-text-base">Project Site Attendance</Title>
      </div>
      <Card variant="borderless">
        <div className="text-center">

        <div className="my-8 p-6 bg-gray-100 dark:bg-gray-800 rounded-lg inline-block">
          <Text strong className="text-lg mr-2">Current Status:</Text>
          <Tag
            icon={checkedIn ? <CheckCircleOutlined /> : <ClockCircleOutlined />}
            color={checkedIn ? 'success' : 'warning'}
            className="text-lg px-3 py-1"
          >
            {attendanceStatus}
          </Tag>
          {lastActionTime && <Text type="secondary" className="block mt-2">Last action at {lastActionTime}</Text>}
        </div>

        <div>
          <Button
            type="primary"
            size="large"
            icon={loading ? <Spin /> : <EnvironmentOutlined />}
            loading={loading}
            onClick={handleCheckInOut}
            className="min-w-[220px] h-14 text-lg"
          >
            {checkedIn ? 'Check Out' : 'Check In'}
          </Button>
        </div>

        <Modal
          open={photoModalVisible} // Use 'open' instead of 'visible' for modern Antd
          title={
            <div>
              <div>{actionType === 'check-in' ? '📸 Take Check-In Photo' : '📸 Take Check-Out Photo'}</div>
              {gpsAccuracy && (
                <div style={{ fontSize: '12px', color: '#666', fontWeight: 'normal' }}>
                  📍 GPS Accuracy: ±{gpsAccuracy.toFixed(0)}m
                </div>
              )}
            </div>
          }
          onCancel={resetPhotoModal}
          footer={[
            <Button key="cancel" onClick={resetPhotoModal}>
              ❌ Cancel Attendance
            </Button>,
            <Button
              key="submit"
              type="primary"
              onClick={submitAttendance}
              loading={loading}
              disabled={!photoPreview} // Only enable when photo is taken
            >
              ✅ {actionType === 'check-in' ? 'Submit Check In' : 'Submit Check Out'}
            </Button>
          ]}
          destroyOnHidden
          width={600}
        >
          <div>
            {!photoPreview && (
              <div style={{ position: 'relative', backgroundColor: '#f0f0f0', borderRadius: 8, minHeight: 300 }}>
                <video
                  id="video"
                  width="100%"
                  height="auto"
                  autoPlay
                  playsInline
                  muted // Add muted to prevent autoplay issues
                  style={{
                    borderRadius: 8,
                    backgroundColor: '#000',
                    minHeight: 300,
                    objectFit: 'cover'
                  }}
                />
                <div style={{
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  transform: 'translate(-50%, -50%)',
                  color: '#666',
                  display: photoPreview ? 'none' : 'block',
                  textAlign: 'center',
                  padding: '20px'
                }}>
                  {loading ? (
                    <div>
                      <div>📸 {photoPreview ? 'Restarting camera...' : 'Starting camera...'}</div>
                      <div style={{ fontSize: '12px', marginTop: '5px' }}>
                        {photoPreview ? 'Please wait while camera restarts' : 'Please allow camera access'}
                      </div>
                    </div>
                  ) : (
                    <div>
                      <div>📷 Position yourself in the camera</div>
                      <div style={{ fontSize: '12px', marginTop: '5px' }}>Camera preview will appear here</div>
                    </div>
                  )}
                </div>
              </div>
            )}
            {photoPreview && (
              <div style={{ textAlign: 'center', marginTop: 16 }}>
                <div style={{ marginBottom: '10px', color: '#52c41a', fontWeight: 'bold' }}>
                  ✅ Photo captured successfully!
                </div>
                <img src={photoPreview} alt="Preview" style={{ maxWidth: '100%', borderRadius: 8, border: '2px solid #52c41a' }} />
                <div style={{ marginTop: '10px', color: '#666', fontSize: '14px' }}>
                  If you're not satisfied with this photo, click "Retake Photo" below
                </div>
              </div>
            )}
            <div style={{ marginTop: 16, display: 'flex', justifyContent: 'center' }}>
              {!photoPreview ? (
                // Show capture button when no photo taken
                <Button onClick={capturePhoto} type="primary" disabled={loading} size="large">
                  📸 Capture Photo
                </Button>
              ) : (
                // Show retake button when photo is taken
                <Button onClick={resetCamera} type="default" size="large" loading={loading}>
                  {loading ? '🔄 Restarting Camera...' : '🔄 Retake Photo'}
                </Button>
              )}
            </div>
          </div>
        </Modal>
      </div>
      </Card>
    </div>
  );
};

export default ProjectAttendance;

