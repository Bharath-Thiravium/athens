// src/features/admin/components/UserList.tsx

import React, { useEffect, useState, useCallback, useMemo } from 'react';
// We still need Modal for the component version, but we use the App hook for confirmation.
import { Table, Button, Space, Modal, App, Card, Typography, Popconfirm } from 'antd';
import { EditOutlined, DeleteOutlined, EyeOutlined, PlusOutlined, StopOutlined } from '@ant-design/icons';
import styled from 'styled-components';
import UserCreation from './UserCreation';
import UserEdit from './UserEdit';
import UserView from './UserView';
import api from '../../../common/utils/axiosetup';
import type { UserData } from '../types';
import useAuthStore from '@common/store/authStore';
import PageLayout from '@common/components/PageLayout';

const { Title, Text } = Typography;

// --- Styled Components (Unchanged) ---
const UserListPageContainer = styled.div`
  width: 100%;
`;

const UserListCard = styled.div`
  background-color: var(--color-ui-base);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-lg);
  padding: 24px;
  box-shadow: var(--shadow-md);
  transition: background-color 0.3s ease, border-color 0.3s ease;
`;

const CardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
`;

const PermissionDeniedContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: calc(100vh - 200px);
  background-color: var(--color-ui-base);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-border);
  text-align: center;
  padding: 40px;
`;

// --- Component Definition ---

type ModalState = {
  type: 'view' | 'edit' | 'add' | null;
  data: UserData | null;
};

const UserList: React.FC = () => {
  // --- State and Hooks ---
  const djangoUserType = useAuthStore((state) => state.django_user_type);
  const [users, setUsers] = useState<UserData[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalState, setModalState] = useState<ModalState>({ type: null, data: null });
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  // ========= FIX STEP 1: Get the 'modal' instance from the hook =========
  const { message, modal } = App.useApp();

  // --- Auto-Navigation Logic ---
  const handlePaginationChange = useCallback((page: number, size: number) => {
    setCurrentPage(page);
    setPageSize(size);
  }, []);

  // Auto-advance to next page when current page is filled
  useEffect(() => {
    const totalPages = Math.ceil(users.length / pageSize);
    const currentPageStartIndex = (currentPage - 1) * pageSize;
    const currentPageEndIndex = currentPageStartIndex + pageSize;
    const usersOnCurrentPage = users.slice(currentPageStartIndex, currentPageEndIndex);

    // If current page is full and there are more pages, auto-advance
    if (usersOnCurrentPage.length === pageSize && currentPage < totalPages) {
      // Small delay to make the transition smooth
      setTimeout(() => {
        setCurrentPage(currentPage + 1);
        message.info(`Page ${currentPage} is full. Automatically moved to page ${currentPage + 1}.`);
      }, 500);
    }
  }, [users.length, pageSize, currentPage, message]);

  // --- Data Fetching (Unchanged) ---
  const fetchUsers = useCallback(async () => {
    setLoading(true);
    try {
      const response = await api.get('/authentication/projectadminuser/list/');
      const fetchedUsers: UserData[] = response.data.map((user: any) => ({
        ...user,
        key: String(user.id),
      }));
      setUsers(fetchedUsers);
    } catch (error) {
      message.error('Failed to fetch users.');
    } finally {
      setLoading(false);
    }
  }, [message]);

  useEffect(() => {
    if (djangoUserType !== 'adminuser') {
      fetchUsers();
    }
  }, [djangoUserType, fetchUsers]);

  // --- Modal Handlers (Unchanged) ---
  const handleOpenModal = useCallback((type: 'view' | 'edit' | 'add', data: UserData | null = null) => {
    setModalState({ type, data });
  }, []);

  const handleCancelModal = useCallback(() => {
    setModalState({ type: null, data: null });
  }, []);

  // --- CRUD Handlers ---

  const handleDeleteUser = useCallback(async (userToDelete: UserData) => {
    try {
      await api.delete(`/authentication/projectadminuser/delete/${userToDelete.id}/`);
      setUsers((prev) => prev.filter((user) => user.id !== userToDelete.id));
      message.success('User deleted successfully.');
    } catch (error: any) {
      const errorMsg = error.response?.data?.message || 'Failed to delete user.';
      message.error(errorMsg);
    }
  }, [message, setUsers]);

  const handleSaveNewUser = useCallback((newUserFromApi: UserData) => {
    setUsers((prev) => {
      const newUsers = [...prev, { ...newUserFromApi, key: String(newUserFromApi.id) }];
      // Calculate which page the new user will be on
      const newUserPage = Math.ceil(newUsers.length / pageSize);
      setCurrentPage(newUserPage);
      return newUsers;
    });
    handleCancelModal();
    message.success(`User created successfully and moved to page ${Math.ceil((users.length + 1) / pageSize)}.`);
  }, [handleCancelModal, message, pageSize, users.length]);

  const handleSaveEditedUser = useCallback(async (updatedUser: UserData) => {
    try {
      const response = await api.put(`/authentication/projectadminuser/update/${updatedUser.id}/`, updatedUser);
      const freshlyUpdatedUser = { ...response.data, key: String(response.data.id) };
      setUsers((prev) => prev.map((user) => (user.id === freshlyUpdatedUser.id ? freshlyUpdatedUser : user)));
      message.success('User updated successfully.');
      handleCancelModal();
    } catch (error) {
      message.error('Failed to update user.');
    }
  }, [handleCancelModal, message, setUsers]);

  const columns = useMemo(() => [
    { title: 'Name', dataIndex: 'name', key: 'name', render: (text: string, record: UserData) => `${record.name} ${record.surname}` },
    { title: 'Email', dataIndex: 'email', key: 'email', ellipsis: true },
    { title: 'Username', dataIndex: 'username', key: 'username', ellipsis: true },
    { title: 'Department', dataIndex: 'department', key: 'department' },
    { title: 'Designation', dataIndex: 'designation', key: 'designation' },
    {
      title: 'Actions',
      key: 'actions',
      align: 'center' as const,
      width: 150,
      render: (_: any, record: UserData) => (
        <Space size="small">
          <Button type="text" icon={<EyeOutlined />} onClick={() => handleOpenModal('view', record)} aria-label={`View ${record.name}`} />
          <Button type="text" icon={<EditOutlined />} onClick={() => handleOpenModal('edit', record)} aria-label={`Edit ${record.name}`} />
          <Popconfirm
            title="Delete User"
            description={`Are you sure you want to delete ${record.name} ${record.surname}? This action cannot be undone.`}
            onConfirm={() => handleDeleteUser(record)}
            okText="Yes, Delete"
            cancelText="Cancel"
            okType="danger"
            placement="topRight"
          >
            <Button type="text" danger icon={<DeleteOutlined />} aria-label={`Delete ${record.name}`} />
          </Popconfirm>
        </Space>
      ),
    },
  ], [handleOpenModal, handleDeleteUser]);

  // --- Render Logic (Unchanged) ---
  if (djangoUserType === 'adminuser') {
    return (
      <PageLayout title="User Management" subtitle="Access denied">
        <PermissionDeniedContainer>
          <StopOutlined style={{ fontSize: '48px', color: 'var(--color-text-muted)', marginBottom: '24px' }}/>
          <Title level={4} style={{ color: 'var(--color-text-base)', marginBottom: '8px' }}>Permission Denied</Title>
          <Text type="secondary">Your user role does not have permission to view this page.</Text>
        </PermissionDeniedContainer>
      </PageLayout>
    );
  }

  return (
    <PageLayout
      title="User Management"
      subtitle="Manage users and their permissions"
      breadcrumbs={[
        { title: 'Users' }
      ]}
      actions={
        <Button type="primary" icon={<PlusOutlined />} onClick={() => handleOpenModal('add')}>
          Add User
        </Button>
      }
    >
      <UserListPageContainer>
        <UserListCard>
        <Table
          columns={columns}
          dataSource={users}
          loading={loading}
          rowKey="key"
          pagination={{
            current: currentPage,
            pageSize: pageSize,
            total: users.length,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} users`,
            position: ['bottomRight'],
            onChange: handlePaginationChange,
            onShowSizeChange: handlePaginationChange,
            pageSizeOptions: ['10', '20', '50', '100'],
          }}
          scroll={{ x: 'max-content' }}
        />
      </UserListCard>
      
      <UserView user={modalState.data} open={modalState.type === 'view'} onClose={handleCancelModal} />
      <UserEdit user={modalState.data} open={modalState.type === 'edit'} onSave={handleSaveEditedUser} onCancel={handleCancelModal} />
      
      <Modal open={modalState.type === 'add'} title="Add New User" footer={null} onCancel={handleCancelModal} width={700} destroyOnClose>
        <UserCreation onFinish={handleSaveNewUser} />
      </Modal>
    </UserListPageContainer>
    </PageLayout>
  );
};

export default UserList;