
import React, { useEffect, useState, useCallback, useMemo } from 'react';
import { Table, Button, Space, Modal, App, Tag, Tooltip, Typography } from 'antd';
import { EditOutlined, DeleteOutlined, EyeOutlined, PlusOutlined, StopOutlined } from '@ant-design/icons';
import styled from 'styled-components';
import WorkerCreation from '@features/worker/components/WorkerCreation';
import WorkerEdit from '@features/worker/components/WorkerEdit';
import WorkerView from '@features/worker/components/WorkerView';
import api from '@common/utils/axiosetup';
import useAuthStore from '@common/store/authStore';
import type { WorkerData } from '../types';

const { Title, Text } = Typography;

// --- Styled Components for a Themed UI ---
const PageContainer = styled.div`
  width: 100%;
`;

const ListCard = styled.div`
  background-color: var(--color-ui-base);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-lg);
  padding: 24px;
  box-shadow: var(--shadow-md);
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
  text-align: center;
  padding: 40px;
`;

// --- Component Definition ---
const WorkerList: React.FC = () => {
  const {message, modal} = App.useApp();
  // --- State and Hooks ---
  const [workers, setWorkers] = useState<WorkerData[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [viewingWorker, setViewingWorker] = useState<WorkerData | null>(null);
  const [editingWorker, setEditingWorker] = useState<WorkerData | null>(null);
  const [addingWorker, setAddingWorker] = useState<boolean>(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  
  const { usertype, userId, django_user_type } = useAuthStore();

  // Check if user can view workers (both adminuser and projectadmin can view)
  const canViewWorkers = ['clientuser', 'epcuser', 'contractoruser'].includes(usertype || '') ||
                         ['master', 'client', 'epc', 'contractor'].includes(usertype || '');

  // Check if user can create/edit workers (only adminuser can create/edit)
  const canManageWorkers = django_user_type === 'adminuser' &&
                          ['clientuser', 'epcuser', 'contractoruser'].includes(usertype || '');

  // Check if user is projectadmin (read-only access)
  const isProjectAdmin = django_user_type === 'projectadmin';

  // --- Auto-Navigation Logic ---
  const handlePaginationChange = useCallback((page: number, size: number) => {
    setCurrentPage(page);
    setPageSize(size);
  }, []);

  // Auto-advance to next page when current page is filled
  useEffect(() => {
    const totalPages = Math.ceil(workers.length / pageSize);
    const currentPageStartIndex = (currentPage - 1) * pageSize;
    const currentPageEndIndex = currentPageStartIndex + pageSize;
    const workersOnCurrentPage = workers.slice(currentPageStartIndex, currentPageEndIndex);

    // If current page is full and there are more pages, auto-advance
    if (workersOnCurrentPage.length === pageSize && currentPage < totalPages) {
      // Small delay to make the transition smooth
      setTimeout(() => {
        setCurrentPage(currentPage + 1);
        message.info(`Page ${currentPage} is full. Automatically moved to page ${currentPage + 1}.`);
      }, 500);
    }
  }, [workers.length, pageSize, currentPage, message]);

  // --- Data Fetching and Handlers (Memoized) ---
  const fetchWorkers = useCallback(async () => {
    if (!canViewWorkers) {
      console.log('DEBUG: User cannot view workers');
      return;
    }
    setLoading(true);
    try {
      const response = await api.get('/worker/');
      
      // Handle both paginated and non-paginated responses
      let workersData = [];
      if (Array.isArray(response.data)) {
        // Direct array response
        workersData = response.data;
      } else if (response.data && Array.isArray(response.data.results)) {
        // Paginated response
        workersData = response.data.results;
      } else {
        // Fallback
        workersData = [];
      }
      
      const workersWithKeys = workersData.map((w: any) => ({ ...w, key: String(w.id) }));
      setWorkers(workersWithKeys);
    } catch (error) {
      console.error('DEBUG: Error fetching workers:', error);
      message.error('Failed to fetch workers');
    } finally {
      setLoading(false);
    }
  }, [canViewWorkers, message]);

  useEffect(() => {
    fetchWorkers();
  }, [fetchWorkers]);

  const handleCancelModals = useCallback(() => {
    setViewingWorker(null);
    setEditingWorker(null);
    setAddingWorker(false);
  }, []);

  const handleDelete = useCallback((worker: WorkerData) => {
    modal.confirm({
      title: `Delete ${worker.name}?`,
      content: 'This action is permanent and cannot be undone.',
      okText: 'Yes, Delete',
      okType: 'danger',
      cancelText: 'Cancel',
      centered: true,
      maskClosable: false,
      keyboard: true,
      zIndex: 1005,
      async onOk() {
        try {
          await api.delete(`/worker/${worker.id}/`);
          setWorkers(prev => prev.filter(w => w.id !== worker.id));
          message.success('Worker deleted successfully');
        } catch (error: any) {
          const errorMsg = error.response?.data?.error || 'Failed to delete worker';
          message.error(errorMsg);
        }
      },
      onCancel() {
        // Optional: Add any cleanup logic here
      },
    });
  }, [message, modal]);

  const handleSaveNewWorker = useCallback((newWorker: WorkerData) => {
    // Calculate which page the new worker will be on
    const newWorkerPage = Math.ceil((workers.length + 1) / pageSize);
    setCurrentPage(newWorkerPage);

    // A fetch is better than optimistic update here to ensure all server-generated data is correct.
    message.success(`Worker added successfully and moved to page ${newWorkerPage}.`);
    setAddingWorker(false);
    fetchWorkers();
  }, [fetchWorkers, workers.length, pageSize]);

const handleSaveEditedWorker = useCallback(async (updatedWorker: WorkerData) => {
    try {
      const response = await api.put(`/worker/${updatedWorker.id}/`, updatedWorker);
      // Replace the old worker data with the complete, fresh data from the server
      setWorkers(prev => prev.map(w => w.id === updatedWorker.id ? { ...response.data, key: String(response.data.id) } : w));
      message.success('Worker updated successfully');
      setEditingWorker(null);
      // Stay on current page after update
    } catch (error) {
      message.error('Failed to update worker');
    }
  }, []);
  
  const getStatusTag = useCallback((status: string) => {
    switch (status?.toLowerCase()) {
      case 'active': return <Tag color="success">Active</Tag>;
      case 'inactive': return <Tag color="error">Inactive</Tag>;
      case 'on_leave': return <Tag color="orange">On Leave</Tag>;
      default: return <Tag>{status || 'Unknown'}</Tag>;
    }
  }, []);
  
  // --- Table Column Definition (Memoized) ---
  const columns = useMemo(() => [
    { title: 'Name', dataIndex: 'name', key: 'name', render: (text: string, record: WorkerData) => `${text} ${record.surname || ''}` },
    { title: 'Worker ID', dataIndex: 'worker_id', key: 'worker_id', width: 150 },
    { title: 'Designation', dataIndex: 'designation', key: 'designation', ellipsis: true },
    { title: 'Phone', dataIndex: 'phone_number', key: 'phone_number', width: 150 },
    { title: 'Status', dataIndex: 'status', key: 'status', width: 120, render: getStatusTag },
    {
      title: 'Actions', key: 'actions', align: 'center' as const, width: 150,
      render: (_: any, record: WorkerData) => (
        <Space size="small">
          <Tooltip title="View Details"><Button shape="circle" icon={<EyeOutlined />} onClick={() => setViewingWorker(record)} /></Tooltip>
          {/* Only show edit/delete buttons for adminuser who can manage workers */}
          {canManageWorkers && (
            <>
              <Tooltip title="Edit Worker"><Button shape="circle" icon={<EditOutlined />} onClick={() => setEditingWorker(record)} /></Tooltip>
              <Tooltip title="Delete Worker"><Button shape="circle" danger icon={<DeleteOutlined />} onClick={() => handleDelete(record)} /></Tooltip>
            </>
          )}
        </Space>
      ),
    },
  ], [getStatusTag, handleDelete, canManageWorkers]);

  // --- Render Logic ---
  if (!canViewWorkers) {
    return (
      <PermissionDeniedContainer>
        <StopOutlined style={{ fontSize: '48px', color: 'var(--color-text-muted)', marginBottom: '24px' }} />
        <Title level={4} style={{ color: 'var(--color-text-base)', marginBottom: '8px' }}>Permission Denied</Title>
        <Text type="secondary">Your user role does not have permission to view this page.</Text>
      </PermissionDeniedContainer>
    );
  }

  return (
    <PageContainer>
      <ListCard>
        <CardHeader>
          <Title level={4} style={{ margin: 0, color: 'var(--color-text-base)' }}>
            Worker Management
            {isProjectAdmin && <Text type="secondary" style={{ fontSize: '14px', marginLeft: '8px' }}>(View Only)</Text>}
          </Title>
          {/* Only show Add Worker button for adminuser who can manage workers */}
          {canManageWorkers && (
            <Button type="primary" icon={<PlusOutlined />} onClick={() => setAddingWorker(true)}>Add Worker</Button>
          )}
        </CardHeader>
        
        <Table
          columns={columns}
          dataSource={workers}
          loading={loading}
          rowKey="key"
          pagination={{
            current: currentPage,
            pageSize: pageSize,
            total: workers.length,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} workers`,
            position: ['bottomRight'],
            onChange: handlePaginationChange,
            onShowSizeChange: handlePaginationChange,
            pageSizeOptions: ['10', '20', '50', '100'],
          }}
          scroll={{ x: 'max-content' }}
        />
      </ListCard>

      {/* --- Modals --- */}
      {viewingWorker && <WorkerView worker={viewingWorker} visible={!!viewingWorker} onClose={handleCancelModals} />}
      {/* Only show edit modal for adminuser who can manage workers */}
      {editingWorker && canManageWorkers && <WorkerEdit worker={editingWorker} visible={!!editingWorker} onSave={handleSaveEditedWorker} onCancel={handleCancelModals} />}

      {/* Only show add worker modal for adminuser who can manage workers */}
      {canManageWorkers && (
        <Modal open={addingWorker} title={<Title level={4} style={{color: 'var(--color-text-base)'}}>Add New Worker</Title>} footer={null} onCancel={handleCancelModals} destroyOnClose width={900}>
          <WorkerCreation onFinish={handleSaveNewWorker} />
        </Modal>
      )}
    </PageContainer>
  );
};

export default WorkerList;