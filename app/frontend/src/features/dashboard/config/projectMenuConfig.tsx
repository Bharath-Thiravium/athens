import React from 'react';
import { MenuItem } from './menuConfig';
import {
  DashboardOutlined,
  BarChartOutlined,
  ClockCircleOutlined,
  MessageOutlined,
  SoundOutlined,
  TeamOutlined,
  UserOutlined,
  AuditOutlined,
  ReadOutlined,
  BookOutlined,
  SafetyOutlined,
  FormOutlined,
  PlusOutlined,
  FileTextOutlined,
  ExperimentOutlined,
  EnvironmentOutlined,
  CheckCircleOutlined,
  SettingOutlined,
  CalendarOutlined,
  ThunderboltOutlined,
  DeleteOutlined,
  BugOutlined,
  GlobalOutlined,
  DropboxOutlined,
  AlertOutlined,
  TrophyOutlined,
  LineChartOutlined,
  QrcodeOutlined,
} from '@ant-design/icons';
import api from '@common/utils/axiosetup';

interface ProjectMenuAccess {
  menu_module_key: string;
  menu_module_name: string;
  menu_module_icon: string;
}

const moduleKeyAliases: Record<string, string> = {
  main_dashboard: 'dashboard',
  analytics_dashboard: 'analytics',
  worker_management: 'workers',
  manpower_management: 'manpower',
  safety_observation: 'safety_observation',
  incident_management: 'incident_management',
  inspection_management: 'inspection_management',
  toolbox_talk: 'toolboxtalk',
  induction_training: 'inductiontraining',
  job_training: 'jobtraining',
  voice_translator: 'voice-translator',
  training_check_in: 'training-check-in',
  user_management: 'user_management',
  permission_control: 'permission_control',
  system_settings: 'system_settings',
};

export const normalizeModuleKey = (key: string) => moduleKeyAliases[key] || key;

const categoryIconMap: Record<string, React.ReactNode> = {
  dashboard: <DashboardOutlined />,
  safety: <SafetyOutlined />,
  training: <AuditOutlined />,
  workforce: <TeamOutlined />,
  communication: <MessageOutlined />,
  qms: <CheckCircleOutlined />,
  esg: <EnvironmentOutlined />,
  admin: <SettingOutlined />,
  reports: <BarChartOutlined />,
};

/**
 * Menu item mapping based on module keys
 * Note: System Administration modules are controlled by backend API only
 */
const getMenuItemByKey = (key: string): MenuItem | MenuItem[] | null => {
  const menuMap: Record<string, MenuItem | MenuItem[]> = {
    'dashboard': { key: '/dashboard', icon: <DashboardOutlined />, label: 'Overview' },
    'analytics': { key: '/dashboard/analytics', icon: <BarChartOutlined />, label: 'Analytics' },
    'attendance': { key: '/dashboard/attendance', icon: <ClockCircleOutlined />, label: 'Mark Attendance' },
    'chatbox': { key: '/dashboard/chatbox', icon: <MessageOutlined />, label: 'Chat Box' },
    'voice-translator': { key: '/dashboard/voice-translator', icon: <SoundOutlined />, label: 'Voice Translator' },
    'workers': { key: '/dashboard/workers', icon: <TeamOutlined />, label: 'Workers' },
    'manpower': { key: '/dashboard/manpower', icon: <TeamOutlined />, label: 'Manpower' },
    
    // Training modules
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
    'training-check-in': { key: '/dashboard/training/check-in', icon: <QrcodeOutlined />, label: 'Training Check-in' },
    'inductiontraining': { key: '/dashboard/inductiontraining', icon: <ReadOutlined />, label: 'Induction Training' },
    'jobtraining': { key: '/dashboard/jobtraining', icon: <ReadOutlined />, label: 'Job Training' },
    'toolboxtalk': { key: '/dashboard/toolboxtalk', icon: <BookOutlined />, label: 'Toolbox Talk' },
    
    // Safety modules
    'safety_observation': {
      key: 'safetyobservation',
      icon: <SafetyOutlined />,
      label: 'Safety Observation',
      children: [
        { key: '/dashboard/safetyobservation/form', icon: <FormOutlined />, label: 'Observation Form' },
        { key: '/dashboard/safetyobservation/list', icon: <TeamOutlined />, label: 'Observation List' },
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
    'incident_management': {
      key: 'incidentmanagement',
      icon: <SafetyOutlined />,
      label: 'Incident Management',
      children: [
        { key: '/dashboard/incidentmanagement/incidents', icon: <FileTextOutlined />, label: 'All Incidents' },
        { key: '/dashboard/incidentmanagement/create', icon: <PlusOutlined />, label: 'Report Incident' },
        { key: '/dashboard/incidentmanagement', icon: <BarChartOutlined />, label: 'Dashboard' },
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
    
    // Work permits
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
    
    // Inspections
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
    'inspection_management': {
      key: 'inspection',
      icon: <ExperimentOutlined />,
      label: 'Inspections',
      children: [
        { key: '/dashboard/inspection', icon: <FileTextOutlined />, label: 'All Inspections' },
        { key: '/dashboard/inspection/create', icon: <PlusOutlined />, label: 'Create Inspection' },
        { key: '/dashboard/inspection/reports', icon: <BarChartOutlined />, label: 'Reports' }
      ]
    },
    
    // ESG Management
    'esg': {
      key: 'esg',
      icon: <EnvironmentOutlined />,
      label: 'ESG Management',
      children: [
        { key: '/dashboard/esg', icon: <DashboardOutlined />, label: 'ESG Overview' },
        // Environment sub-module will be added dynamically based on enabled modules
        // Other ESG sub-modules will be added individually if enabled
      ]
    },
    
    // Quality Management
    'quality': {
      key: 'quality',
      icon: <CheckCircleOutlined />,
      label: 'Quality Management',
      children: [
        { key: '/dashboard/quality', icon: <DashboardOutlined />, label: 'Executive Dashboard' },
        { key: '/dashboard/quality/enhanced', icon: <LineChartOutlined />, label: 'Analytics & KPIs' },
        { key: '/dashboard/quality/inspections', icon: <ExperimentOutlined />, label: 'Quality Inspections' },
        { key: '/dashboard/quality/suppliers', icon: <TeamOutlined />, label: 'Supplier Quality' },
        { key: '/dashboard/quality/defects', icon: <BugOutlined />, label: 'Defect Management' },
        { key: '/dashboard/quality/templates', icon: <FileTextOutlined />, label: 'Quality Templates' },
        { key: '/dashboard/quality/standards', icon: <TrophyOutlined />, label: 'Quality Standards' },
        { key: '/dashboard/quality/alerts', icon: <AlertOutlined />, label: 'Quality Alerts' },
      ]
    },
    
    // Other modules
    'mom': { key: '/dashboard/mom', icon: <CalendarOutlined />, label: 'Minutes of Meeting' },
  };

  return menuMap[key] || null;
};

export const getSidebarLabelForModuleKey = (key: string): string | null => {
  const normalizedKey = normalizeModuleKey(key);
  const menuItem = getMenuItemByKey(normalizedKey);
  if (!menuItem || Array.isArray(menuItem)) {
    return null;
  }
  const label = menuItem.label;
  return typeof label === 'string' ? label : null;
};

const buildMenuItemsFromCategories = (categories: any[]): MenuItem[] => {
  const items: MenuItem[] = [];
  const usedKeys = new Set<string>();

  const sortedCategories = [...categories].sort((a, b) => {
    const orderA = typeof a?.order === 'number' ? a.order : 0;
    const orderB = typeof b?.order === 'number' ? b.order : 0;
    return orderA - orderB;
  });

  sortedCategories.forEach((category) => {
    const children: MenuItem[] = [];
    const modules = Array.isArray(category?.modules) ? category.modules : [];
    modules.forEach((module: any) => {
      const normalizedKey = normalizeModuleKey(module?.key || '');
      if (!normalizedKey) {
        return;
      }
      
      // Handle System Administration modules from backend API
      if (category.key === 'system_administration' || category.key === 'admin') {
        const sysAdminModules: Record<string, MenuItem> = {
          'user_management': { key: '/dashboard/users', icon: <UserOutlined />, label: 'User Management' },
          'permission_control': { key: '/dashboard/permissions', icon: <SettingOutlined />, label: 'Permission Control' },
          'system_settings': { key: '/dashboard/settings', icon: <SettingOutlined />, label: 'System Settings' },
        };
        
        const sysAdminItem = sysAdminModules[normalizedKey];
        if (sysAdminItem && !usedKeys.has(sysAdminItem.key)) {
          usedKeys.add(sysAdminItem.key);
          children.push(sysAdminItem);
        }
        return;
      }
      
      const menuItem = getMenuItemByKey(normalizedKey);
      const addItem = (item: MenuItem) => {
        if (!usedKeys.has(item.key)) {
          usedKeys.add(item.key);
          children.push(item);
        }
      };
      if (Array.isArray(menuItem)) {
        menuItem.forEach(addItem);
      } else if (menuItem) {
        addItem(menuItem);
      }
    });

    const categoryKey = String(category?.key || '').toLowerCase();
    const categoryName = String(category?.name || '').toLowerCase();
    if (categoryKey === 'training' || categoryName === 'training') {
      const trainingCheckIn = getMenuItemByKey('training-check-in');
      if (trainingCheckIn && !Array.isArray(trainingCheckIn)) {
        if (!usedKeys.has(trainingCheckIn.key)) {
          usedKeys.add(trainingCheckIn.key);
          children.unshift(trainingCheckIn);
        }
      }
    }

    if (children.length > 0) {
      items.push({
        key: `category-${category.key || category.id}`,
        icon: categoryIconMap[category.key] || undefined,
        label: category.name || 'Modules',
        children,
      });
    }
  });

  return items;
};

/**
 * Get menu items based on project-specific access control
 */
export const getProjectBasedMenuItems = async (
  usertype?: string | null,
  django_user_type?: string | null,
  isApproved: boolean = true,
  hasSubmittedDetails: boolean = true
): Promise<MenuItem[]> => {
  
  // Master admin gets full access - no project restrictions
  if (usertype === 'masteradmin' || django_user_type === 'masteradmin') {
    return [
      { key: '/dashboard', icon: <DashboardOutlined />, label: 'Overview' },
      { key: '/dashboard/analytics', icon: <BarChartOutlined />, label: 'Analytics' },
      { key: '/dashboard/projects', icon: <TeamOutlined />, label: 'Projects' },
      { key: '/dashboard/adminusers', icon: <TeamOutlined />, label: 'Admin Users' },
      { key: '/dashboard/menu-management', icon: <FormOutlined />, label: 'Menu Management' },
    ];
  }

  // If user is not approved, return restricted menu
  if (!isApproved && (django_user_type === 'projectadmin' || django_user_type === 'adminuser')) {
    return [
      { key: '/dashboard', icon: <DashboardOutlined />, label: 'Overview' },
      {
        key: django_user_type === 'projectadmin' ? '/dashboard/admindetail' : '/dashboard/userdetail',
        icon: <UserOutlined />,
        label: hasSubmittedDetails ? 'Profile (Pending Approval)' : 'Profile (Required)',
      }
    ];
  }

  try {
    // Get user's project-specific menu access
    let response;
    try {
      response = await api.get('/api/menu/user-menu/');
    } catch (error: any) {
      if (error?.response?.status === 404) {
        response = await api.get('/authentication/project-menu-access/user_menu_access/');
      } else {
        throw error;
      }
    }
    const menuPayload = response.data;
    const categories = Array.isArray(menuPayload?.menu)
      ? menuPayload.menu
      : Array.isArray(menuPayload)
        ? menuPayload
        : [];
    const flattenedModules = categories.flatMap((category: any) => category?.modules || []);
    const enabledModules = flattenedModules;
    
    console.log('API Response:', menuPayload);

    // Build menu items based on enabled modules
    const menuItems: MenuItem[] = [];
    
    // Remove user detail items from sidebar - they belong in header only
    // if (django_user_type === 'adminuser') {
    //   menuItems.push({ key: '/dashboard/userdetail', icon: <UserOutlined />, label: 'User Detail' });
    // } else if (['client', 'epc'].includes(usertype ?? '') || usertype?.includes('contractor')) {
    //   menuItems.push({ key: '/dashboard/users', icon: <UserOutlined />, label: 'Users' });
    //   menuItems.push({ key: '/dashboard/admindetail', icon: <UserOutlined />, label: 'Admin Detail' });
    // }

    const categorizedMenuItems = buildMenuItemsFromCategories(categories);
    if (categorizedMenuItems.length > 0) {
      return [...menuItems, ...categorizedMenuItems];
    }

    // Process enabled modules from API
    const getModuleKey = (moduleData: any) =>
      moduleData?.menu_module__key || moduleData?.menu_module_key || moduleData?.key;
    const rawKeys = enabledModules
      .map(getModuleKey)
      .filter((key: string | undefined) => Boolean(key)) as string[];
    const enabledKeys = rawKeys.map(normalizeModuleKey);
    
    // Build ESG menu with enabled sub-modules
    let esgMenuItem = null;
    if (enabledKeys.includes('esg')) {
      const esgChildren = [
        { key: '/dashboard/esg', icon: <DashboardOutlined />, label: 'ESG Overview' }
      ];
      
      // Add Environmental Management if environment is enabled
      if (enabledKeys.includes('environment')) {
        const envChildren = [
          { key: '/dashboard/esg/environment?tab=aspects', icon: <EnvironmentOutlined />, label: 'Environment Aspects' },
          { key: '/dashboard/esg/environment?tab=generation', icon: <ThunderboltOutlined />, label: 'Generation Data' },
          { key: '/dashboard/esg/environment?tab=waste', icon: <DeleteOutlined />, label: 'Waste Management' },
          { key: '/dashboard/esg/environment?tab=biodiversity', icon: <BugOutlined />, label: 'Biodiversity Events' }
        ];
        
        // Add individual environmental modules if enabled
        if (enabledKeys.includes('monitoring')) {
          envChildren.push({ key: '/dashboard/esg/monitoring', icon: <ExperimentOutlined />, label: 'Environmental Monitoring' });
        }
        if (enabledKeys.includes('carbon-footprint')) {
          envChildren.push({ key: '/dashboard/esg/carbon-footprint', icon: <GlobalOutlined />, label: 'Carbon Footprint' });
        }
        if (enabledKeys.includes('water-management')) {
          envChildren.push({ key: '/dashboard/esg/water-management', icon: <DropboxOutlined />, label: 'Water Management' });
        }
        if (enabledKeys.includes('energy-management')) {
          envChildren.push({ key: '/dashboard/esg/energy-management', icon: <ThunderboltOutlined />, label: 'Energy Management' });
        }
        if (enabledKeys.includes('environmental-incidents')) {
          envChildren.push({ key: '/dashboard/esg/environmental-incidents', icon: <AlertOutlined />, label: 'Environmental Incidents' });
        }
        
        esgChildren.push({
          key: 'environment',
          icon: <EnvironmentOutlined />,
          label: 'Environmental Management',
          children: envChildren
        });
      }
      
      // Add other ESG modules if enabled
      if (enabledKeys.includes('sustainability-targets')) {
        esgChildren.push({ key: '/dashboard/esg/sustainability-targets', icon: <TrophyOutlined />, label: 'Sustainability Targets' });
      }
      if (enabledKeys.includes('governance')) {
        esgChildren.push({ key: '/dashboard/esg/governance', icon: <AuditOutlined />, label: 'Governance' });
      }
      
      esgChildren.push({ key: '/dashboard/esg/reports', icon: <BarChartOutlined />, label: 'ESG Reports' });
      
      esgMenuItem = {
        key: 'esg',
        icon: <EnvironmentOutlined />,
        label: 'ESG Management',
        children: esgChildren
      };
    }
    
    // Build Quality menu with enabled sub-modules
    let qualityMenuItem = null;
    if (enabledKeys.includes('quality')) {
      const qualityChildren = [
        { key: '/dashboard/quality', icon: <DashboardOutlined />, label: 'Executive Dashboard' },
        { key: '/dashboard/quality/enhanced', icon: <LineChartOutlined />, label: 'Analytics & KPIs' }
      ];
      
      if (enabledKeys.includes('quality-inspections')) {
        qualityChildren.push({ key: '/dashboard/quality/inspections', icon: <ExperimentOutlined />, label: 'Quality Inspections' });
      }
      if (enabledKeys.includes('suppliers')) {
        qualityChildren.push({ key: '/dashboard/quality/suppliers', icon: <TeamOutlined />, label: 'Supplier Quality' });
      }
      if (enabledKeys.includes('defects')) {
        qualityChildren.push({ key: '/dashboard/quality/defects', icon: <BugOutlined />, label: 'Defect Management' });
      }
      if (enabledKeys.includes('templates')) {
        qualityChildren.push({ key: '/dashboard/quality/templates', icon: <FileTextOutlined />, label: 'Quality Templates' });
      }
      if (enabledKeys.includes('standards')) {
        qualityChildren.push({ key: '/dashboard/quality/standards', icon: <TrophyOutlined />, label: 'Quality Standards' });
      }
      if (enabledKeys.includes('alerts')) {
        qualityChildren.push({ key: '/dashboard/quality/alerts', icon: <AlertOutlined />, label: 'Quality Alerts' });
      }
      
      qualityMenuItem = {
        key: 'quality',
        icon: <CheckCircleOutlined />,
        label: 'Quality Management',
        children: qualityChildren
      };
    }
    
    // Build Training menu with enabled sub-modules
    const trainingEnabled = enabledKeys.some((key) =>
      ['training', 'inductiontraining', 'jobtraining', 'toolboxtalk'].includes(key)
    );
    let trainingMenuItem = null;
    if (trainingEnabled) {
      const trainingChildren = [
        { key: '/dashboard/training/check-in', icon: <QrcodeOutlined />, label: 'Training Check-in' },
      ];
      if (enabledKeys.includes('inductiontraining')) {
        trainingChildren.push({ key: '/dashboard/inductiontraining', icon: <ReadOutlined />, label: 'Induction Training' });
      }
      if (enabledKeys.includes('jobtraining')) {
        trainingChildren.push({ key: '/dashboard/jobtraining', icon: <ReadOutlined />, label: 'Job Training' });
      }
      if (enabledKeys.includes('toolboxtalk')) {
        trainingChildren.push({ key: '/dashboard/toolboxtalk', icon: <BookOutlined />, label: 'Toolbox Talk' });
      }
      
      if (trainingChildren.length > 0) {
        trainingMenuItem = {
          key: 'training',
          icon: <AuditOutlined />,
          label: 'Training',
          children: trainingChildren
        };
      }
    }
    
    for (const moduleData of enabledModules) {
      const rawKey = getModuleKey(moduleData);
      if (!rawKey) {
        continue;
      }
      const moduleKey = normalizeModuleKey(rawKey);
      if (!moduleKey) {
        continue;
      }
      
      // Skip modules that are handled above
      const skipModules = [
        'esg', 'environment', 'monitoring', 'carbon-footprint', 'water-management', 
        'energy-management', 'environmental-incidents', 'sustainability-targets', 'governance',
        'quality', 'quality-inspections', 'suppliers', 'defects', 'templates', 'standards', 'alerts',
        'training', 'inductiontraining', 'jobtraining', 'toolboxtalk'
      ];
      
      if (skipModules.includes(moduleKey)) {
        continue;
      }
      
      const menuItem = getMenuItemByKey(moduleKey);
      if (menuItem && !Array.isArray(menuItem)) {
        menuItems.push(menuItem);
      }
    }
    
    // Add built menus in order
    if (trainingMenuItem) {
      menuItems.push(trainingMenuItem);
    }
    if (esgMenuItem) {
      menuItems.push(esgMenuItem);
    }
    if (qualityMenuItem) {
      menuItems.push(qualityMenuItem);
    }

    console.log('Generated menu items:', menuItems);
    return menuItems;

  } catch (error) {
    console.error('Failed to load project menu access:', error);
    
    // If it's an authentication error, throw it to be handled by the caller
    if (error.response?.status === 401 || error.response?.status === 403) {
      throw error;
    }
    
    // For other errors, return minimal menu
    return [
      { key: '/dashboard', icon: <DashboardOutlined />, label: 'Overview' }
    ];
  }
};

/**
 * Enhanced menu configuration that uses project-based access control
 */
export const getEnhancedMenuItemsForUser = async (
  usertype?: string | null,
  django_user_type?: string | null,
  isApproved: boolean = true,
  hasSubmittedDetails: boolean = true,
  department?: string | null
): Promise<MenuItem[]> => {
  
  console.log('getEnhancedMenuItemsForUser called with:', {
    usertype,
    django_user_type,
    isApproved,
    hasSubmittedDetails,
    department
  });

  return await getProjectBasedMenuItems(usertype, django_user_type, isApproved, hasSubmittedDetails);
};

export default {
  getProjectBasedMenuItems,
  getEnhancedMenuItemsForUser
};
