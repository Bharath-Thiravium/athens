import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Switch,
  Select,
  Button,
  message,
  Space,
  Typography,
  Divider,
  Tag,
  Modal,
  Form,
  Input,
  Spin,
  Row,
  Col,
  Statistic,
  Progress,
  Collapse,
  Checkbox
} from 'antd';
import {
  SettingOutlined,
  SaveOutlined,
  ReloadOutlined,
  ProjectOutlined,
  MenuOutlined,
  CheckCircleOutlined,
  BarChartOutlined
} from '@ant-design/icons';
import PageLayout from '@common/components/PageLayout';
import api from '@common/utils/axiosetup';
import { getSidebarLabelForModuleKey } from '@features/dashboard/config/projectMenuConfig';

const { Title, Text } = Typography;
const { Option } = Select;

interface MenuModule {
  id: number;
  name: string;
  key: string;
  icon: string;
  description: string;
  is_active: boolean;
}

interface MenuCategory {
  id: number | string;
  name: string;
  key: string;
  icon?: string;
  order?: number;
  is_active?: boolean;
  modules: MenuModule[];
}

interface Project {
  id: number;
  projectName: string;
  projectCategory: string;
  location: string;
}

interface ProjectMenuAccess {
  id: number;
  project: number;
  menu_module: number;
  is_enabled: boolean;
  menu_module_name: string;
  menu_module_key: string;
  project_name: string;
}

interface CompanyMenuAccess {
  id: number;
  module: {
    id: number;
  };
  is_enabled: boolean;
}

interface MenuStats {
  kpis: Array<{
    title: string;
    value: number;
    icon: string;
    color: string;
    trend: string;
  }>;
  statistics: {
    total_projects: number;
    total_modules: number;
    total_configurations: number;
    enabled_configurations: number;
    configuration_rate: number;
    activation_rate: number;
  };
  project_stats: Array<{
    project_id: number;
    project_name: string;
    total_configs: number;
    enabled_configs: number;
    coverage_percentage: number;
  }>;
}

const MenuManagement: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [menuModules, setMenuModules] = useState<MenuModule[]>([]);
  const [menuCategories, setMenuCategories] = useState<MenuCategory[]>([]);
  const [selectedProject, setSelectedProject] = useState<number | null>(null);
  const [projectMenuAccess, setProjectMenuAccess] = useState<ProjectMenuAccess[]>([]);
  const [menuStats, setMenuStats] = useState<MenuStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [statsLoading, setStatsLoading] = useState(false);

  const getProjectName = (project: Project | null) =>
    project?.projectName || (project as any)?.name || 'Unknown Project';

  const getProjectCategory = (project: Project | null) =>
    project?.projectCategory || (project as any)?.category || 'N/A';

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setLoading(true);
    setStatsLoading(true);
    try {
      const [projectsRes, modulesRes, statsRes, companyAccessRes] = await Promise.all([
        api.get('/authentication/project/list/'),
        api.get('/api/menu/categories/'),
        api.get('/authentication/menu/dashboard/stats/'),
        api.get('/api/menu/company-access/')
      ]);
      
      const normalizedProjects = (projectsRes.data || []).map((project: any) => ({
        ...project,
        projectName: project.projectName || project.name || 'Unknown Project',
        projectCategory: project.projectCategory || project.category || 'N/A',
      }));

      const companyAccess: CompanyMenuAccess[] = Array.isArray(companyAccessRes.data) ? companyAccessRes.data : [];
      const enabledCompanyModules = companyAccess
        .filter(access => access.is_enabled && access.module?.id != null)
        .map(access => access.module.id);
      const allowedModuleIds = new Set(enabledCompanyModules);

      const categories = Array.isArray(modulesRes.data) ? modulesRes.data : [];
      const hasCategories = categories.some((category: any) => Array.isArray(category.modules));
      const flattenedModules = hasCategories
        ? categories.flatMap((category: any) => category.modules || [])
        : categories;
      const normalizeModule = (module: any) => ({
        ...module,
        description: module.description || '',
      });
      const normalizedModules = flattenedModules.map(normalizeModule);
      const filteredModules = normalizedModules.filter((module: any) => allowedModuleIds.has(module.id));
      const normalizedCategories: MenuCategory[] = hasCategories
        ? categories
            .map((category: any) => ({
              ...category,
              modules: (category.modules || []).map(normalizeModule).filter((module: any) => allowedModuleIds.has(module.id)),
            }))
            .filter((category: any) => category.modules.length > 0)
        : [
            {
              id: 'modules',
              name: 'Modules',
              key: 'modules',
              modules: filteredModules,
            },
          ];

      setProjects(normalizedProjects);
      setMenuModules(filteredModules);
      setMenuCategories(normalizedCategories);
      setMenuStats(statsRes.data);
    } catch (error) {
      message.error('Failed to load data');
    } finally {
      setLoading(false);
      setStatsLoading(false);
    }
  };

  const loadProjectMenuAccess = async (projectId: number) => {
    setLoading(true);
    try {
      const response = await api.get(`/api/menu/project-menu-access/by_project/?project_id=${projectId}`);
      const accessData = Array.isArray(response.data) ? response.data : (response.data?.menu || []);
      const normalizedAccess = (accessData || []).map((item: any) => {
        if (item.menu_module) {
          return item;
        }
        if (item.module) {
          return {
            id: item.id,
            project: projectId,
            menu_module: item.module.id,
            is_enabled: item.is_enabled,
            menu_module_name: item.module.name,
            menu_module_key: item.module.key,
            project_name: '',
          };
        }
        return null;
      }).filter(Boolean);
      setProjectMenuAccess(normalizedAccess);
    } catch (error) {
      message.error('Failed to load project menu access');
    } finally {
      setLoading(false);
    }
  };

  const handleProjectChange = (projectId: number) => {
    setSelectedProject(projectId);
    loadProjectMenuAccess(projectId);
  };

  const handleMenuToggle = (moduleId: number, enabled: boolean) => {
    setProjectMenuAccess(prev => {
      const existing = prev.find(access => access.menu_module === moduleId);
      if (existing) {
        return prev.map(access =>
          access.menu_module === moduleId
            ? { ...access, is_enabled: enabled }
            : access
        );
      }
      const module = menuModules.find(m => m.id === moduleId);
      const project = projects.find(p => p.id === selectedProject);
      if (module && project) {
        return [
          ...prev,
          {
            id: 0,
            project: selectedProject!,
            menu_module: moduleId,
            is_enabled: enabled,
            menu_module_name: module.name,
            menu_module_key: module.key,
            project_name: project.projectName
          }
        ];
      }
      return prev;
    });
  };

  const handleCategoryToggle = (category: MenuCategory, enabled: boolean) => {
    if (!selectedProject) return;
    const moduleIds = category.modules.map(module => module.id);
    setProjectMenuAccess(prev => {
      const next = [...prev];
      moduleIds.forEach(moduleId => {
        const existingIndex = next.findIndex(access => access.menu_module === moduleId);
        if (existingIndex >= 0) {
          next[existingIndex] = { ...next[existingIndex], is_enabled: enabled };
        } else {
          const module = menuModules.find(m => m.id === moduleId);
          const project = projects.find(p => p.id === selectedProject);
          if (module && project) {
            next.push({
              id: 0,
              project: selectedProject,
              menu_module: moduleId,
              is_enabled: enabled,
              menu_module_name: module.name,
              menu_module_key: module.key,
              project_name: project.projectName
            });
          }
        }
      });
      return next;
    });
  };

  const saveMenuConfiguration = async () => {
    if (!selectedProject) {
      message.error('Please select a project');
      return;
    }

    setSaving(true);
    try {
      const menuModulesData = menuModules.map(module => {
        const access = projectMenuAccess.find(a => a.menu_module === module.id);
        return {
          module_id: module.id,
          is_enabled: access ? access.is_enabled : true // Default to enabled
        };
      });

      await api.post('/api/menu/project-menu-access/update_project_access/', {
        project_id: selectedProject,
        menu_modules: menuModulesData
      });

      message.success('Menu configuration saved successfully');
    } catch (error) {
      message.error('Failed to save menu configuration');
    } finally {
      setSaving(false);
    }
  };

  const getModuleStatus = (moduleId: number): boolean => {
    const access = projectMenuAccess.find(a => a.menu_module === moduleId);
    return access ? access.is_enabled : true; // Default to enabled
  };

  const getCategoryStatus = (category: MenuCategory) => {
    const enabledCount = category.modules.filter(module => getModuleStatus(module.id)).length;
    const total = category.modules.length;
    return {
      enabledCount,
      total,
      allEnabled: total > 0 && enabledCount === total,
      partiallyEnabled: enabledCount > 0 && enabledCount < total,
    };
  };

  const columns = [
    {
      title: 'Menu Module',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: MenuModule) => (
        <Space>
          <Text strong>{text}</Text>
          <Tag color="blue">{record.key}</Tag>
        </Space>
      ),
    },
    {
      title: 'Sidebar Label',
      key: 'sidebarLabel',
      render: (record: MenuModule) => {
        const label = getSidebarLabelForModuleKey(record.key);
        return <Text>{label || record.name}</Text>;
      },
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      render: (text: string) => text || 'No description available',
    },
    {
      title: 'Status',
      key: 'status',
      render: (record: MenuModule) => (
        <Tag color={record.is_active ? 'green' : 'red'}>
          {record.is_active ? 'Active' : 'Inactive'}
        </Tag>
      ),
    },
    {
      title: 'Access',
      key: 'access',
      render: (record: MenuModule) => (
        <Switch
          checked={getModuleStatus(record.id)}
          onChange={(checked) => handleMenuToggle(record.id, checked)}
          disabled={!selectedProject || !record.is_active}
        />
      ),
    },
  ];

  return (
    <PageLayout
      title="Menu Management"
      subtitle="Configure project-wise access to menu modules"
      icon={<MenuOutlined />}
      breadcrumbs={[
        { title: 'Admin' },
        { title: 'Menu Management' }
      ]}
    >

      {/* KPI Dashboard Section */}
      <Card style={{ marginBottom: '24px' }}>
        <Title level={5} className="!mb-4 !text-color-text-base">
          <BarChartOutlined /> Menu Management Overview
        </Title>
        <Text type="secondary">
          Consolidated statistics and KPIs for menu configuration across all projects
        </Text>
        
        <Divider />
        
        <Spin spinning={statsLoading}>
          {menuStats && (
            <>
              {/* KPI Cards */}
              <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
                <Col xs={24} sm={12} md={6}>
                  <Card>
                    <Statistic
                      title="Total Projects"
                      value={menuStats.kpis[0]?.value || 0}
                      prefix={<ProjectOutlined style={{ color: '#1890ff' }} />}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} md={6}>
                  <Card>
                    <Statistic
                      title="Menu Modules"
                      value={menuStats.kpis[1]?.value || 0}
                      prefix={<MenuOutlined style={{ color: '#52c41a' }} />}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} md={6}>
                  <Card>
                    <Statistic
                      title="Total Configurations"
                      value={menuStats.kpis[2]?.value || 0}
                      prefix={<SettingOutlined style={{ color: '#faad14' }} />}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} md={6}>
                  <Card>
                    <Statistic
                      title="Active Configurations"
                      value={menuStats.kpis[3]?.value || 0}
                      prefix={<CheckCircleOutlined style={{ color: '#13c2c2' }} />}
                    />
                  </Card>
                </Col>
              </Row>
              
              {/* Statistics Cards */}
              <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
                <Col xs={24} md={12}>
                  <Card title="Configuration Rate" size="small">
                    <Progress
                      percent={menuStats.statistics.configuration_rate}
                      status="active"
                      strokeColor="#1890ff"
                    />
                    <Text type="secondary">
                      {menuStats.statistics.total_configurations} of {menuStats.statistics.total_projects * menuStats.statistics.total_modules} possible configurations
                    </Text>
                  </Card>
                </Col>
                <Col xs={24} md={12}>
                  <Card title="Activation Rate" size="small">
                    <Progress
                      percent={menuStats.statistics.activation_rate}
                      status="active"
                      strokeColor="#52c41a"
                    />
                    <Text type="secondary">
                      {menuStats.statistics.enabled_configurations} of {menuStats.statistics.total_configurations} configurations enabled
                    </Text>
                  </Card>
                </Col>
              </Row>
            </>
          )}
        </Spin>
      </Card>

      {/* Menu Configuration Section */}
      <Card>
        <div style={{ marginBottom: '24px' }}>
          <Title level={5} className="!mb-4 !text-color-text-base">
            <SettingOutlined /> Project Menu Configuration
          </Title>
          <Text type="secondary">
            Control project-wise access to menu modules in the user portal
          </Text>
        </div>

        <Divider />

        <div style={{ marginBottom: '24px' }}>
          <Space size="large" align="center">
            <div>
              <Text strong>Select Project:</Text>
              <Select
                style={{ width: 300, marginLeft: 8 }}
                placeholder="Choose a project to configure"
                value={selectedProject}
                onChange={handleProjectChange}
                loading={loading}
              >
                {projects.map(project => (
                  <Option key={project.id} value={project.id}>
                    <Space>
                      <ProjectOutlined />
                      {getProjectName(project)}
                      <Tag size="small">{getProjectCategory(project)}</Tag>
                    </Space>
                  </Option>
                ))}
              </Select>
            </div>

            <Button
              type="primary"
              icon={<SaveOutlined />}
              onClick={saveMenuConfiguration}
              disabled={!selectedProject}
              loading={saving}
            >
              Save Configuration
            </Button>

            <Button
              icon={<ReloadOutlined />}
              onClick={() => selectedProject && loadProjectMenuAccess(selectedProject)}
              disabled={!selectedProject}
            >
              Refresh
            </Button>
          </Space>
        </div>

        {selectedProject && (
          <Card 
            title={`Menu Configuration for: ${getProjectName(projects.find(p => p.id === selectedProject) || null)}`}
            size="small"
          >
            <Spin spinning={loading}>
              <Collapse
                defaultActiveKey={menuCategories.map(category => String(category.id))}
                items={menuCategories.map(category => {
                  const status = getCategoryStatus(category);
                  return {
                    key: String(category.id),
                    label: (
                      <div
                        style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}
                      >
                        <Space>
                          <Text strong>{category.name}</Text>
                          <Tag color="blue">{category.modules.length} modules</Tag>
                          <Tag color={status.allEnabled ? 'green' : status.partiallyEnabled ? 'gold' : 'red'}>
                            {status.allEnabled ? 'All enabled' : status.partiallyEnabled ? 'Partially enabled' : 'All disabled'}
                          </Tag>
                        </Space>
                        <Checkbox
                          checked={status.allEnabled}
                          indeterminate={status.partiallyEnabled}
                          disabled={!selectedProject}
                          onClick={(event) => event.stopPropagation()}
                          onChange={(event) => handleCategoryToggle(category, event.target.checked)}
                        >
                          Enable all
                        </Checkbox>
                      </div>
                    ),
                    children: (
                      <Table
                        columns={columns}
                        dataSource={category.modules}
                        rowKey="id"
                        pagination={false}
                        size="middle"
                      />
                    ),
                  };
                })}
              />
            </Spin>
          </Card>
        )}

        {!selectedProject && (
          <div style={{ textAlign: 'center', padding: '60px 0' }}>
            <ProjectOutlined style={{ fontSize: '48px', color: '#d9d9d9' }} />
            <div style={{ marginTop: '16px' }}>
              <Text type="secondary">Select a project to configure menu access</Text>
            </div>
          </div>
        )}
      </Card>
    </PageLayout>
  );
};

export default MenuManagement;
