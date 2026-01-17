import { useState, useEffect } from 'react';
import { menuService, MenuCategory } from '../services/menuService';

export const useMenuAccess = () => {
  const [menuCategories, setMenuCategories] = useState<MenuCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadUserMenu = async () => {
    try {
      setLoading(true);
      setError(null);
      const categories = await menuService.getUserMenu();
      setMenuCategories(categories);
    } catch (err) {
      setError('Failed to load menu');
      console.error('Menu loading error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUserMenu();
  }, []);

  // Convert to Ant Design menu format
  const getAntMenuItems = () => {
    return menuCategories.map(category => ({
      key: category.key,
      label: category.name,
      icon: category.icon,
      children: category.modules.map(module => ({
        key: module.key,
        label: module.name,
        icon: module.icon,
        path: module.path
      }))
    }));
  };

  // Get flat menu items for routing
  const getFlatMenuItems = () => {
    const items: Array<{key: string, path: string, name: string}> = [];
    menuCategories.forEach(category => {
      category.modules.forEach(module => {
        items.push({
          key: module.key,
          path: module.path,
          name: module.name
        });
      });
    });
    return items;
  };

  return {
    menuCategories,
    loading,
    error,
    getAntMenuItems,
    getFlatMenuItems,
    refreshMenu: loadUserMenu
  };
};