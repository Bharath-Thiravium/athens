import React, { useEffect, useState } from 'react';
import { Modal, Form, Input, DatePicker, Select, Button, App, Space, Row, Col, Typography } from 'antd';
import { EditOutlined } from '@ant-design/icons';
import api from '@common/utils/axiosetup';
import dayjs, { Dayjs } from 'dayjs';

const { Option } = Select;

interface Project {
  key: string;
  id: number;
  name: string;
  category: string;
  capacity: string;
  location: string;
  policeStation: string;
  policeContact: string;
  hospital: string;
  hospitalContact: string;
  commencementDate: string;
  deadlineDate?: string;
  latitude?: number;
  longitude?: number;
}

interface ProjectEditProps {
  project: Project;
  visible: boolean;
  onSave: (updatedProject: Project) => void;
  onCancel: () => void;
}

const ProjectEdit: React.FC<ProjectEditProps> = ({ project, visible, onSave, onCancel }) => {
  // =============================================================================
  // ALL ORIGINAL LOGIC IS 100% PRESERVED AS REQUESTED
  // =============================================================================
  const { message } = App.useApp();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [position, setPosition] = useState<[number, number] | null>(null);

  useEffect(() => {
    if (project && visible) {
      form.setFieldsValue({
        projectName: project.name,
        projectCategory: project.category,
        capacity: project.capacity,
        location: project.location,
        nearestPoliceStation: project.policeStation,
        nearestPoliceStationContact: project.policeContact,
        nearestHospital: project.hospital,
        nearestHospitalContact: project.hospitalContact,
        commencementDate: project.commencementDate ? dayjs(project.commencementDate) : null,
        deadlineDate: project.deadlineDate ? dayjs(project.deadlineDate) : null,
      });
      if (project.latitude && project.longitude) {
        setPosition([project.latitude, project.longitude]);
      }
    }
  }, [project, visible, form]);

  const onFinish = async (values: any) => {
    if (!project?.id) {
      message.error('Project ID is missing.');
      return;
    }
    const apiData = {
      name: values.projectName,
      category: values.projectCategory,
      capacity: values.capacity,
      location: values.location,
      policeStation: values.nearestPoliceStation,
      policeContact: values.nearestPoliceStationContact,
      hospital: values.nearestHospital,
      hospitalContact: values.nearestHospitalContact,
      commencementDate: values.commencementDate ? values.commencementDate.format('YYYY-MM-DD') : null,
      deadlineDate: values.deadlineDate ? values.deadlineDate.format('YYYY-MM-DD') : null,
      latitude: position ? position[0] : undefined,
      longitude: position ? position[1] : undefined,
    };
    setLoading(true);
    try {
      await api.put(`/authentication/project/update/${project.id}/`, apiData);
      onSave({ ...project, ...apiData });
      message.success('Project updated successfully'); // Fix: Ensure the message text is correct for update operation
    } catch (error: any) {
      message.error(error.response?.data?.error || 'Failed to update project.');
    } finally {
      setLoading(false);
    }
  };

  const handleLetterOnlyInput = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!/^[A-Za-z\s]$/.test(e.key)) e.preventDefault();
  };
  
  const handleNumberOnlyInput = (e: React.KeyboardEvent<HTMLInputElement>, maxLength: number) => {
    if (['Backspace', 'ArrowLeft', 'ArrowRight', 'Tab', 'Delete'].includes(e.key)) {
      return;
    }
    if (!/^[0-9]$/.test(e.key) || e.currentTarget.value.length >= maxLength) {
      e.preventDefault();
    }
  };

  // =============================================================================
  // UPDATED JSX: ALIGNED WITH THE DESIGN SYSTEM
  // - No logic changes, only visual enhancements and consistency improvements.
  // =============================================================================
  return (
    <Modal
      open={visible}
      title={
        <Space align="center">
          <EditOutlined className="text-xl" />
          <span className="font-semibold text-text-base text-lg">Edit Project Details</span>
        </Space>
      }
      onCancel={onCancel}
      width={800} // Increased width for better two-column layout
      centered
      destroyOnClose // Ensures form fields are reset when modal is closed and reopened
      footer={[
        <Button key="back" onClick={onCancel} size="large">
          Cancel
        </Button>,
        <Button key="submit" type="primary" loading={loading} onClick={() => form.submit()} size="large">
          Save Changes
        </Button>,
      ]}
    >
      <Form form={form} layout="vertical" onFinish={onFinish} size="large" className="!pt-6" requiredMark="optional">
        <Row gutter={24}>
          <Col span={12}>
            <Form.Item label={<span className="font-semibold text-text-base">Project Name</span>} name="projectName" rules={[{ required: true }]}>
              <Input placeholder="e.g., Western Solar Farm" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item label={<span className="font-semibold text-text-base">Project Category</span>} name="projectCategory" rules={[{ required: true }]}>
              <Select placeholder="Select project category" allowClear>
                <Option value="governments">Governments</Option>
                <Option value="manufacturing">Manufacturing</Option>
                <Option value="construction">Construction</Option>
                <Option value="chemical">Chemical</Option>
                <Option value="port_and_maritime">Port and Maritime</Option>
                <Option value="power_and_energy">Power and Energy</Option>
                <Option value="logistics">Logistics</Option>
                <Option value="schools">Schools</Option>
                <Option value="mining">Mining</Option>
                <Option value="oil_and_gas">Oil & Gas</Option>
                <Option value="shopping_mall">Shopping Mall</Option>
                <Option value="aviation">Aviation</Option>
              </Select>
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={24}>
          <Col span={12}>
            <Form.Item label={<span className="font-semibold text-text-base">Capacity / Size</span>} name="capacity" rules={[{ required: true }]}>
              <Input placeholder="e.g., 100 MW, 5000 sqft" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item label={<span className="font-semibold text-text-base">Location</span>} name="location" rules={[{ required: true }]}>
              <Input placeholder="e.g., Springfield, Illinois" onKeyPress={handleLetterOnlyInput} />
            </Form.Item>
          </Col>
        </Row>

        <Typography.Title level={5} className="!mt-2 !mb-4 !text-text-muted">Emergency Contacts</Typography.Title>
        
        <Row gutter={24}>
          <Col span={12}>
            <Form.Item label={<span className="font-semibold text-text-base">Nearest Police Station</span>} name="nearestPoliceStation" rules={[{ required: true }]}>
              <Input placeholder="Name of the police station" onKeyPress={handleLetterOnlyInput} />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item label={<span className="font-semibold text-text-base">Police Station Contact</span>} name="nearestPoliceStationContact" rules={[{ required: true }, { pattern: /^\d{10}$/, message: 'Must be a 10-digit number' }]}>
              <Input placeholder="Enter 10-digit phone number" onKeyPress={(e) => handleNumberOnlyInput(e, 10)} />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={24}>
          <Col span={12}>
            <Form.Item label={<span className="font-semibold text-text-base">Nearest Hospital</span>} name="nearestHospital" rules={[{ required: true }]}>
              <Input placeholder="Name of the hospital" onKeyPress={handleLetterOnlyInput} />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item label={<span className="font-semibold text-text-base">Hospital Contact</span>} name="nearestHospitalContact" rules={[{ required: true }, { pattern: /^\d{10}$/, message: 'Must be a 10-digit number' }]}>
              <Input placeholder="Enter 10-digit phone number" onKeyPress={(e) => handleNumberOnlyInput(e, 10)} />
            </Form.Item>
          </Col>
        </Row>
        
        <Typography.Title level={5} className="!mt-2 !mb-4 !text-text-muted">Project Timeline</Typography.Title>

        <Row gutter={24}>
          <Col span={12}>
            <Form.Item label={<span className="font-semibold text-text-base">Commencement Date</span>} name="commencementDate" rules={[{ required: true }]}>
              <DatePicker style={{ width: '100%' }} format="YYYY-MM-DD" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              label={<span className="font-semibold text-text-base">Deadline Date</span>}
              name="deadlineDate"
              rules={[
                { required: true, message: 'Please select project deadline date!' },
                {
                  validator: (_, value: Dayjs) => {
                    const commencementDate = form.getFieldValue('commencementDate');
                    if (value && commencementDate && value.isBefore(commencementDate)) {
                      return Promise.reject(new Error('Deadline date must be after commencement date'));
                    }
                    return Promise.resolve();
                  },
                },
              ]}
            >
              <DatePicker
                style={{ width: '100%' }}
                format="YYYY-MM-DD"
                placeholder="Select project deadline"
                disabledDate={(current) => {
                  const commencementDate = form.getFieldValue('commencementDate');
                  if (commencementDate) {
                    return current && current.isBefore(commencementDate);
                  }
                  return false;
                }}
              />
            </Form.Item>
          </Col>
        </Row>
      </Form>
    </Modal>
  );
};

export default ProjectEdit;
