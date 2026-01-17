import React from 'react';
import { authService } from '../../../services/authService';
import {
  DashboardOutlined,
  UserOutlined,
  TeamOutlined,
  SafetyOutlined,
  FormOutlined,
  FileTextOutlined,
  PlusOutlined,
  ClockCircleOutlined,
  BarChartOutlined,
  AuditOutlined,
  ReadOutlined,
  MessageOutlined,
  ProjectOutlined,
  ExperimentOutlined,
  SettingOutlined,
  CalendarOutlined,
  BookOutlined,
  EnvironmentOutlined,
  CheckCircleOutlined,
  SoundOutlined,
  ThunderboltOutlined,
  DeleteOutlined,
  BugOutlined,
  GlobalOutlined,
  TrophyOutlined,
  AlertOutlined,
  LineChartOutlined,
  DatabaseOutlined,
  MenuOutlined,
  QrcodeOutlined
} from '@ant-design/icons';

export interface MenuItem {
  key: string;
  icon?: React.ReactNode;
  label: string;
  children?: MenuItem[];
  disabled?: boolean;
  danger?: boolean;
}

export interface MenuConfig {
  userType: string;
  djangoUserType?: string;
  menuItems: MenuItem[];
}

// Icon mapping for menu modules
const iconMap: { [key: string]: React.ReactNode } = {
  'DashboardOutlined': <DashboardOutlined />,
  'BarChartOutlined': <BarChartOutlined />,
  'ClockCircleOutlined': <ClockCircleOutlined />,
  'MessageOutlined': <MessageOutlined />,
  'SoundOutlined': <SoundOutlined />,
  'TeamOutlined': <TeamOutlined />,
  'AuditOutlined': <AuditOutlined />,
  'ReadOutlined': <ReadOutlined />,
  'BookOutlined': <BookOutlined />,
  'QrcodeOutlined': <QrcodeOutlined />,
  'SafetyOutlined': <SafetyOutlined />,
  'FormOutlined': <FormOutlined />,
  'ExperimentOutlined': <ExperimentOutlined />,
  'EnvironmentOutlined': <EnvironmentOutlined />,
  'CheckCircleOutlined': <CheckCircleOutlined />,
  'CalendarOutlined': <CalendarOutlined />,
  'MenuOutlined': <MenuOutlined />,
};

// Base menu structure with all possible items
const baseMenuStructure: { [key: string]: MenuItem } = {
  'dashboard': { key: '/dashboard', icon: <DashboardOutlined />, label: 'Overview' },
  'analytics': { key: '/dashboard/analytics', icon: <BarChartOutlined />, label: 'Analytics' },
  'attendance': { key: '/dashboard/attendance', icon: <ClockCircleOutlined />, label: 'Mark Attendance' },
  'chatbox': { key: '/dashboard/chatbox', icon: <MessageOutlined />, label: 'Chat Box' },
  'voice-translator': { key: '/dashboard/voice-translator', icon: <SoundOutlined />, label: 'Voice Translator' },
  'workers': { key: '/dashboard/workers', icon: <TeamOutlined />, label: 'Workers' },
  'manpower': { key: '/dashboard/manpower', icon: <TeamOutlined />, label: 'Manpower' },
  'training': {
    key: 'training',
    icon: <AuditOutlined />,
    label: 'Training',
    children: [
      { key: '/dashboard/training/check-in', icon: <QrcodeOutlined />, label: 'Training Check-in' },
      { key: '/dashboard/inductiontraining', icon: <ReadOutlined />, label: 'Induction Training' },
      { key: '/dashboard/jobtraining', icon: <ReadOutlined />, label: 'Job Training' },
      { key: '/dashboard/toolboxtalk', icon: <BookOutlined />, label: 'Toolbox Talk' },
    ]
  },
  'safetyobservation': {
    key: 'safetyobservation',
    icon: <SafetyOutlined />,
    label: 'Safety Observation',
    children: [
      { key: '/dashboard/safetyobservation/form', icon: <FormOutlined />, label: 'Observation Form' },
      { key: '/dashboard/safetyobservation/list', icon: <TeamOutlined />, label: 'Observation List' },
    ]
  },
  'incidentmanagement': {
    key: 'incidentmanagement',
    icon: <SafetyOutlined />,
    label: 'Incident Management',
    children: [
      { key: '/dashboard/incidentmanagement/incidents', icon: <FileTextOutlined />, label: 'All Incidents' },
      { key: '/dashboard/incidentmanagement/create', icon: <PlusOutlined />, label: 'Report Incident' },
      { key: '/dashboard/incidentmanagement', icon: <BarChartOutlined />, label: 'Dashboard' },
    ]
  },
  'ptw': {
    key: 'ptw',
    icon: <FormOutlined />,
    label: 'Permits to Work',
    children: [
      { key: '/dashboard/ptw', icon: <FileTextOutlined />, label: 'All Permits' },
      { key: '/dashboard/ptw/create', icon: <PlusOutlined />, label: 'Create Permit' },
      { key: '/dashboard/ptw/pending-approvals', icon: <ClockCircleOutlined />, label: 'Pending Approvals' },
      { key: '/dashboard/ptw/dashboard', icon: <BarChartOutlined />, label: 'Dashboard' }
    ]
  },
  'inspection': {
    key: 'inspection',
    icon: <ExperimentOutlined />,
    label: 'Inspections',
    children: [
      { key: '/dashboard/inspection', icon: <FileTextOutlined />, label: 'All Inspections' },
      { key: '/dashboard/inspection/create', icon: <PlusOutlined />, label: 'Create Inspection' },
      { key: '/dashboard/inspection/reports', icon: <BarChartOutlined />, label: 'Reports' }
    ]
  },
  'esg': {
    key: 'esg',
    icon: <EnvironmentOutlined />,
    label: 'ESG Management',
    children: [
      { key: '/dashboard/esg', icon: <DashboardOutlined />, label: 'ESG Overview' },
      { key: '/dashboard/esg/monitoring', icon: <ExperimentOutlined />, label: 'Environmental Monitoring' },
      { key: '/dashboard/esg/carbon-footprint', icon: <GlobalOutlined />, label: 'Carbon Footprint' },
      { key: '/dashboard/esg/sustainability-targets', icon: <TrophyOutlined />, label: 'Sustainability Targets' },
    ]
  },
  'quality': {
    key: 'quality',
    icon: <CheckCircleOutlined />,
    label: 'Quality Management',
    children: [
      { key: '/dashboard/quality', icon: <DashboardOutlined />, label: 'Executive Dashboard' },
      { key: '/dashboard/quality/enhanced', icon: <LineChartOutlined />, label: 'Analytics & KPIs' },
      { key: '/dashboard/quality/inspections', icon: <ExperimentOutlined />, label: 'Quality Inspections' },
      { key: '/dashboard/quality/defects', icon: <BugOutlined />, label: 'Defect Management' },
    ]
  },
  'mom': { key: '/dashboard/mom', icon: <CalendarOutlined />, label: 'Minutes of Meeting' },
};

// Master admin specific menu items
const masterAdminMenuItems: MenuItem[] = [
  { key: '/dashboard', icon: <DashboardOutlined />, label: 'Overview' },
  { key: '/dashboard/analytics', icon: <BarChartOutlined />, label: 'Analytics' },
  { key: '/dashboard/projects', icon: <ProjectOutlined />, label: 'Projects' },
  { key: '/dashboard/adminusers', icon: <TeamOutlined />, label: 'Admin Users' },
  { key: '/dashboard/menu-management', icon: <MenuOutlined />, label: 'Menu Management' },
  {
    key: 'system',
    icon: <SettingOutlined />,
    label: 'System Management',
    children: [
      { key: '/dashboard/system/settings', icon: <SettingOutlined />, label: 'Settings' },
      { key: '/dashboard/system/logs', icon: <FileTextOutlined />, label: 'System Logs' },
      { key: '/dashboard/system/backup', icon: <DatabaseOutlined />, label: 'Backup' },
    ]
  }
];

/**
 * Get project-specific menu items based on enabled modules
 */
const getProjectMenuItems = async (enabledModules: string[]): Promise<MenuItem[]> => {
  const menuItems: MenuItem[] = [];
  
  // Always include dashboard
  if (baseMenuStructure['dashboard']) {
    menuItems.push(baseMenuStructure['dashboard']);
  }
  
  // Add enabled modules
  enabledModules.forEach(moduleKey => {
    if (baseMenuStructure[moduleKey]) {
      menuItems.push(baseMenuStructure[moduleKey]);
    }
  });
  
  return menuItems;
};

/**
 * Restricted menu for unapproved users
 */
const getRestrictedMenuItems = (django_user_type: string, hasSubmittedDetails: boolean): MenuItem[] => {
  const baseItems: MenuItem[] = [
    { key: '/dashboard', icon: <DashboardOutlined />, label: 'Overview' },
  ];

  if (django_user_type === 'projectadmin') {
    baseItems.push({
      key: '/dashboard/admindetail',
      icon: <UserOutlined />,
      label: hasSubmittedDetails ? 'Admin Detail (Pending Approval)' : 'Admin Detail (Required)',
    });
  } else if (django_user_type === 'adminuser') {
    baseItems.push({
      key: '/dashboard/userdetail',
      icon: <UserOutlined />,
      label: hasSubmittedDetails ? 'User Detail (Pending Approval)' : 'User Detail (Required)',
    });
  }

  return baseItems;
};

/**
 * Enhanced menu configuration with project-wise access control
 */
export const getMenuItemsForUser = async (\n  usertype?: string | null,\n  django_user_type?: string | null,\n  isApproved: boolean = true,\n  hasSubmittedDetails: boolean = true,\n  department?: string | null\n): Promise<MenuItem[]> => {\n  \n  console.log('getMenuItemsForUser called with:', {\n    usertype,\n    django_user_type,\n    isApproved,\n    hasSubmittedDetails,\n    department\n  });\n  \n  const safeUsertype = usertype || null;\n  const safeDjangoUserType = django_user_type || null;\n  \n  // Basic fallback for no user type\n  if (!safeUsertype && !safeDjangoUserType) {\n    return [\n      { key: '/dashboard', icon: <DashboardOutlined />, label: 'Overview' },\n      { key: '/dashboard/profile', icon: <UserOutlined />, label: 'Profile' },\n    ];\n  }\n\n  // Restricted menu for unapproved users\n  if (!isApproved && (safeDjangoUserType === 'projectadmin' || safeDjangoUserType === 'adminuser')) {\n    return getRestrictedMenuItems(safeDjangoUserType, hasSubmittedDetails);\n  }\n\n  // Master admin - full system access\n  if (safeUsertype === 'masteradmin' || safeDjangoUserType === 'masteradmin' || \n      (safeDjangoUserType === 'projectadmin' && safeUsertype === 'masteradmin')) {\n    return masterAdminMenuItems;\n  }\n\n  // Project-based menu access for other users\n  try {\n    const response = await authService.get('/api/menu/project-menu-access/user_menu_access/');\n    const enabledModules = response.data.map((module: any) => module.menu_module__key);\n    return await getProjectMenuItems(enabledModules);\n  } catch (error) {\n    console.error('Failed to load user menu access:', error);\n    // Fallback to basic menu\n    return [\n      { key: '/dashboard', icon: <DashboardOutlined />, label: 'Overview' },\n      { key: '/dashboard/profile', icon: <UserOutlined />, label: 'Profile' },\n    ];\n  }\n};\n\n/**\n * Get menu configuration for specific user\n */\nexport const getMenuConfig = async (usertype?: string, django_user_type?: string): Promise<MenuConfig> => {\n  return {\n    userType: usertype || 'unknown',\n    djangoUserType: django_user_type,\n    menuItems: await getMenuItemsForUser(usertype, django_user_type)\n  };\n};\n\nexport default {\n  getMenuItemsForUser,\n  getMenuConfig\n};
