import React, { useState, useEffect } from 'react';
import { Card, Switch, Tree, message, Spin, Typography } from 'antd';
import { menuService, MenuCategory } from '../../services/menuService';

const { Title } = Typography;

interface MenuManagementProps {
  companyId?: number;
}

const MenuManagement: React.FC<MenuManagementProps> = ({ companyId }) => {
  const [categories, setCategories] = useState<MenuCategory[]>([]);
  const [companyAccess, setCompanyAccess] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMenuData();
  }, []);

  const loadMenuData = async () => {
    try {
      setLoading(true);
      const [categoriesData, accessData] = await Promise.all([
        menuService.getAllCategories(),
        menuService.getCompanyAccess()
      ]);
      
      setCategories(categoriesData);
      setCompanyAccess(accessData);
    } catch (error) {
      message.error('Failed to load menu data');
      console.error('Menu data error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleModuleToggle = async (moduleId: number, enabled: boolean) => {
    try {
      await menuService.updateCompanyAccess(moduleId, enabled);
      message.success('Menu access updated successfully');
      loadMenuData(); // Reload data
    } catch (error) {
      message.error('Failed to update menu access');
      console.error('Update error:', error);
    }
  };

  const isModuleEnabled = (moduleId: number) => {
    const access = companyAccess.find(a => a.module.id === moduleId);
    return access ? access.is_enabled : false;
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>Menu Management</Title>
      
      {categories.map(category => (
        <Card 
          key={category.id} 
          title={category.name} 
          style={{ marginBottom: '16px' }}
        >
          {category.modules.map(module => (
            <div 
              key={module.id}
              style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                padding: '8px 0',
                borderBottom: '1px solid #f0f0f0'
              }}
            >
              <div>
                <strong>{module.name}</strong>
                <div style={{ color: '#666', fontSize: '12px' }}>
                  Path: {module.path}
                </div>
              </div>
              <Switch
                checked={isModuleEnabled(module.id)}
                onChange={(checked) => handleModuleToggle(module.id, checked)}
              />
            </div>
          ))}
        </Card>
      ))}
    </div>
  );
};

export default MenuManagement;