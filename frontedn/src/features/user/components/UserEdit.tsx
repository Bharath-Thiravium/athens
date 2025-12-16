import React, { useEffect, useState, useCallback } from 'react';
import { Form, Input, Button, App, Typography, Modal, Row, Col, Select } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import styled from 'styled-components';
import type { UserData } from '../types';

const { Title } = Typography;
const { Option } = Select;


// --- Type Definitions (Unchanged, already good practice) ---
interface UserEditProps {
  user: UserData | null;
  open: boolean;
  onSave: (updatedUser: UserData) => void;
  onCancel: () => void;
}

type UserEditFormData = Omit<UserData, 'id' | 'key' | 'username'>;

// --- Styled Components for Themed UI ---
const DropdownFooter = styled.div`
  padding: 8px;
  border-top: 1px solid var(--color-border);
`;

// --- Component Definition ---

const UserEdit: React.FC<UserEditProps> = ({ user, open, onSave, onCancel }) => {
  
  const { message } = App.useApp();
  // --- State and Hooks ---
  const [form] = Form.useForm<UserEditFormData>();
  const [loading, setLoading] = useState(false);
  const [customDesignationModalVisible, setCustomDesignationModalVisible] = useState(false);
  const [customDesignation, setCustomDesignation] = useState('');
  const [designations, setDesignations] = useState([
    'SiteIncharge', 'TeamLeader', 'Manager', 'Engineer', 'Supervisor', 'Technician', 'Assistant'
  ]);

  // --- Effects ---
  // Effect to populate the form when the modal opens with a valid user.
  useEffect(() => {
    if (user && open) {
      form.resetFields(); // Clear stale data from previous edits.

      let suggestedGrade = user.grade;
      if (!user.grade) { // Auto-suggest grade if missing
          suggestedGrade = 'C';
          if (user.designation?.toLowerCase() === 'siteincharge') suggestedGrade = 'A';
          else if (['teamleader', 'manager'].includes(user.designation?.toLowerCase())) suggestedGrade = 'B';
      }
      
      form.setFieldsValue({ ...user, grade: suggestedGrade });
    }
  }, [user, open, form]);

  // --- Handlers (Memoized with useCallback) ---
  const handleDesignationChange = useCallback((value: string) => {
    let suggestedGrade = 'C';
    if (value.toLowerCase() === 'siteincharge') suggestedGrade = 'A';
    else if (['teamleader', 'manager'].includes(value.toLowerCase())) suggestedGrade = 'B';
    form.setFieldsValue({ grade: suggestedGrade });
  }, [form]);

  const showAddDesignationModal = useCallback(() => setCustomDesignationModalVisible(true), []);
  const closeAddDesignationModal = useCallback(() => setCustomDesignationModalVisible(false), []);
  
  const handleCustomDesignationInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setCustomDesignation(e.target.value);
  }, []);

  const handleAddDesignation = useCallback(() => {
    if (customDesignation && !designations.includes(customDesignation)) {
      setDesignations(prev => [...prev, customDesignation]);
      form.setFieldsValue({ designation: customDesignation });
      handleDesignationChange(customDesignation);
      setCustomDesignation('');
    }
    closeAddDesignationModal();
  }, [customDesignation, designations, form, handleDesignationChange, closeAddDesignationModal]);

  // Programmatically trigger the form's onFinish handler.
  const handleOk = useCallback(() => {
    form.submit();
  }, [form]);

  // Main submission logic, called after form validation succeeds.
  const handleFormFinish = useCallback((values: Partial<UserEditFormData>) => {
    if (!user) return; // Safeguard

    setLoading(true);
    // Combine original user data with form values to preserve ID and other non-editable fields.
    const updatedUser: UserData = { ...user, ...values };

    // IMPORTANT: If password is an empty string, remove it from the payload
    // to prevent accidentally clearing the user's password on the backend.
    if (!updatedUser.password) {
      delete updatedUser.password;
    }

    // FIX: Clean up object fields that should be IDs for backend compatibility
    const cleanedUser = { ...updatedUser };

    // Handle project field - ensure it's an ID, not an object
    if (cleanedUser.project && typeof cleanedUser.project === 'object') {
      const projectId = (cleanedUser.project as any).id || (cleanedUser.project as any).value || (cleanedUser.project as any).key;
      cleanedUser.project = projectId;
    }

    // Handle any other potential object fields that should be IDs
    ['department', 'designation', 'grade'].forEach(field => {
      if (cleanedUser[field] && typeof cleanedUser[field] === 'object') {
        const fieldValue = (cleanedUser[field] as any).id || (cleanedUser[field] as any).value || (cleanedUser[field] as any).key;
        cleanedUser[field] = fieldValue;
      }
    });


    try {
      // Pass the final, clean data to the parent component for the API call.
      onSave(cleanedUser);
    } catch (error: any) {
      message.error('Failed to update user. Please try again.');
      setLoading(false);
      return;
    }

    setLoading(false); // The parent will close the modal, so we can reset loading here.

  }, [user, onSave]);

  // --- Render ---
  return (
    <>
      <Modal
        title={<Title level={4} style={{color: 'var(--color-text-base)'}}>Edit User Information</Title>}
        open={open}
        onOk={handleOk}
        onCancel={onCancel}
        width={700}
        // The modal is now themed by the global antd ConfigProvider, no className needed.
        footer={[
          <Button key="back" onClick={onCancel}>Cancel</Button>,
          <Button key="submit" type="primary" loading={loading} onClick={handleOk}>Save Changes</Button>,
        ]}
      >
        <Form form={form} layout="vertical" onFinish={handleFormFinish}>
          <Row gutter={24}>
            <Col xs={24} md={12}>
              <Form.Item label="Email" name="email" rules={[{ required: true, message: 'Email is required' }, { type: 'email', message: 'Enter a valid email' }]}>
                <Input placeholder="Enter email" />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item label="Username">
                <Input value={user?.username} placeholder="Username" disabled />
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={24}>
            <Col xs={24} md={12}>
              <Form.Item label="Name" name="name" rules={[{ required: true, message: 'Name is required' }, { pattern: /^[A-Za-z\s]+$/, message: 'Name can only contain letters and spaces' }]}>
                <Input placeholder="Enter name" />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item label="Surname" name="surname" rules={[{ required: true, message: 'Surname is required' }, { pattern: /^[A-Za-z\s]+$/, message: 'Surname can only contain letters and spaces' }]}>
                <Input placeholder="Enter surname" />
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={24}>
            <Col xs={24} md={12}>
              <Form.Item label="Department" name="department" rules={[{ required: true, message: 'Department is required' }]}>
                <Select placeholder="Select department">
                  <Option value="Quality">Quality</Option>
                  <Option value="Safety">Safety</Option>
                  <Option value="Inventory">Inventory</Option>
                  <Option value="Project/Execution">Project/Execution</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item label="Designation" name="designation" rules={[{ required: true, message: 'Designation is required' }]}>
                <Select
                  placeholder="Select designation"
                  onChange={handleDesignationChange}
                  dropdownRender={(menu) => (
                    <>
                      {menu}
                      <DropdownFooter>
                        <Button type="text" icon={<PlusOutlined />} onClick={showAddDesignationModal} style={{ width: '100%', textAlign: 'left' }}>
                          Add Custom Designation
                        </Button>
                      </DropdownFooter>
                    </>
                  )}
                >
                  {designations.map(d => <Option key={d} value={d}>{d}</Option>)}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={24}>
            <Col xs={24} md={12}>
              <Form.Item label="Grade" name="grade" rules={[{ required: true, message: 'Grade is required' }]} tooltip="Grade auto-suggested based on Designation">
                <Select placeholder="Select grade">
                  <Option value="A">Grade A</Option>
                  <Option value="B">Grade B</Option>
                  <Option value="C">Grade C</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item label="Phone Number" name="phone_number" rules={[{ required: true, message: 'Phone number is required' }, { pattern: /^\d{10}$/, message: 'Must be 10 digits' }]}>
                <Input placeholder="Enter 10-digit phone number" maxLength={10} />
              </Form.Item>
            </Col>
          </Row>
          
          <Form.Item label="New Password" name="password" extra="Leave blank to keep the current password.">
            <Input.Password placeholder="Enter new password (optional)" />
          </Form.Item>
        </Form>
      </Modal>

      {/* Nested Modal for adding a custom designation */}
      <Modal
        title="Add Custom Designation"
        open={customDesignationModalVisible}
        onOk={handleAddDesignation}
        onCancel={closeAddDesignationModal}
        okText="Add"
        destroyOnClose
      >
        <Input
          placeholder="Enter custom designation"
          value={customDesignation}
          onChange={handleCustomDesignationInputChange}
          onPressEnter={handleAddDesignation}
        />
      </Modal>
    </>
  );
};

export default UserEdit;