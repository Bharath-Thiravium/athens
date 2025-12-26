// src/features/project/components/ProjectsList.tsx

import React, { useState, useEffect, useCallback } from 'react';
// Imports are already correct - great job!
import { Table, Button, Space, App, Typography, Card, Tag, Modal as AntdModal, Modal } from 'antd';
import { EditOutlined, DeleteOutlined, EyeOutlined, PlusOutlined } from '@ant-design/icons';
import ProjectCreation from '@features/project/components/ProjectCreation';
import ProjectEdit from '@features/project/components/ProjectEdit';
import ProjectView from '@features/project/components/ProjectView';
import api from '@common/utils/axiosetup';
import PageLayout from '@common/components/PageLayout';

const { Title, Text } = Typography;

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
}

const ProjectsList: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [viewingProject, setViewingProject] = useState<Project | null>(null);
  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const [addingProject, setAddingProject] = useState(false);
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  // Hook usage is perfect.
  const { modal, message } = App.useApp();

  // --- Auto-Navigation Logic ---
  const handlePaginationChange = useCallback((page: number, size: number) => {
    setCurrentPage(page);
    setPageSize(size);
  }, []);


  const fetchProjects = useCallback(async () => {
    setLoading(true);
    try {
      const response = await api.get('/authentication/project/list/');
      const fetchedProjects: Project[] = Array.isArray(response.data)
        ? response.data.filter((p: any) => p.id != null).map((p: any) => ({ ...p, key: String(p.id) }))
        : [];
      setProjects(fetchedProjects);
    } catch (error) {
      message.error('Failed to fetch projects');
    } finally {
      setLoading(false);
    }
  }, [message]);

  useEffect(() => { fetchProjects(); }, [fetchProjects]);

  const handleView = (project: Project) => setViewingProject(project);
  const handleEdit = (project: Project) => setEditingProject(project);
  const handleAddProject = () => setAddingProject(true);
  const handleCancel = () => {
    setViewingProject(null);
    setEditingProject(null);
    setAddingProject(false);
  };
  
  // Enhanced delete handler with fallback for modal context issues
  const handleDelete = (id: number) => {

    // Use the modal from App context if available, otherwise use static Modal
    const modalToUse = modal || Modal;

    modalToUse.confirm({
      title: 'Are you sure you want to delete this project?',
      content: 'This action cannot be undone.',
      okText: 'Delete',
      okType: 'danger',
      onOk: async () => {
        try {
          await api.delete(`/authentication/project/delete/${id}/`);
          setProjects(prev => prev.filter(proj => proj.id !== id));
          message.success('Project deleted successfully');
        } catch (error: any) {
          const errorMessage = error.response?.data?.error || error.message || 'Failed to delete project';
          message.error(errorMessage);
        }
      },
    });
  };

  // ==================== FIX STARTS HERE ====================
  
  // 1. Create a dedicated handler for project CREATION success.
  const handleCreateSuccess = () => {
    // Calculate which page the new project will be on
    const newProjectPage = Math.ceil((projects.length + 1) / pageSize);
    setCurrentPage(newProjectPage);

    message.success(`Project created successfully and moved to page ${newProjectPage}.`);
    handleCancel(); // Close the modal
    fetchProjects(); // Refresh the list
  };

  // 2. Create a dedicated handler for project UPDATE success.
  const handleUpdateSuccess = () => {
    message.success('Project updated successfully!');
    handleCancel(); // Close the modal
    fetchProjects(); // Refresh the list
    // Stay on current page after update
  };
  
  // 3. The old `handleSave` function is no longer needed.

  // ===================== FIX ENDS HERE =====================

  const columns = [
    { title: 'Project Name', dataIndex: 'name', key: 'name', render: (text: string) => <Text strong className="text-text-base">{text}</Text> },
    { title: 'Category', dataIndex: 'category', key: 'category', render: (text: string) => <Tag>{text.charAt(0).toUpperCase() + text.slice(1).replace(/_/g, ' ')}</Tag> },
    { title: 'Capacity / Size', dataIndex: 'capacity', key: 'capacity' },
    { title: 'Location', dataIndex: 'location', key: 'location' },
    {
      title: 'Actions',
      key: 'actions',
      width: 150,
      align: 'center' as const,
      render: (_: any, record: Project) => (
        <Space size="small">
          <Button type="text" icon={<EyeOutlined className="text-lg" />} onClick={() => handleView(record)} />
          <Button type="text" icon={<EditOutlined className="text-lg" />} onClick={() => handleEdit(record)} />
          <Button type="text" danger icon={<DeleteOutlined className="text-lg" />} onClick={() => handleDelete(record.id)} />
        </Space>
      ),
    },
  ];

  return (
    <PageLayout
      title="Projects Management"
      subtitle="View, create, edit, and manage all company projects"
      breadcrumbs={[
        { title: 'Projects' }
      ]}
      actions={
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={handleAddProject}
          size="large"
          className="!font-semibold"
        >
          Add New Project
        </Button>
      }
    >

      <Card bordered={false}>
        <Table
          columns={columns}
          dataSource={projects}
          loading={loading}
          pagination={{
            current: currentPage,
            pageSize: pageSize,
            total: projects.length,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} projects`,
            position: ['bottomRight'],
            onChange: handlePaginationChange,
            onShowSizeChange: handlePaginationChange,
            pageSizeOptions: ['10', '20', '50', '100'],
          }}
          scroll={{ x: 800 }}
        />
      </Card>

      {viewingProject && ( <ProjectView project={viewingProject} visible={!!viewingProject} onClose={handleCancel} /> )}
      
      {/* Pass the correct update handler to the Edit component */}
      {editingProject && ( <ProjectEdit project={editingProject} visible={!!editingProject} onSave={handleUpdateSuccess} onCancel={handleCancel} /> )}
      
      <AntdModal
        open={addingProject}
        title={<Space align="center"><PlusOutlined className="text-xl" /><span className="font-semibold text-text-base text-lg">Add New Project</span></Space>}
        onCancel={handleCancel}
        width={1000}
        centered
        destroyOnClose
        footer={null}
      >
        {/* Pass the correct creation handler to the Creation component */}
        <ProjectCreation onSuccess={handleCreateSuccess} />
      </AntdModal>
    </PageLayout>
  );
};

export default ProjectsList;