// src/common/theme/antdTheme.ts

import { theme, type ThemeConfig } from 'antd';

type AppTheme = 'light' | 'dark';

export const antdTheme = (currentTheme: AppTheme): ThemeConfig => {
  const isDark = currentTheme === 'dark';

  return {
    algorithm: isDark ? theme.darkAlgorithm : theme.defaultAlgorithm,

    // === TOKEN MAPPING ===
    token: {
      colorPrimary: 'var(--color-primary)',
      colorPrimaryHover: 'var(--color-primary-hover)',
      colorPrimaryText: 'var(--color-primary-text)',
      colorSuccess: '#10b981',
      colorWarning: '#f59e0b',
      colorError: '#ef4444',
      colorInfo: 'var(--color-primary)',
      borderRadius: 6,
      borderRadiusLG: 12,
      fontFamily: "inherit",
      fontSize: 14,
      colorBgLayout: 'var(--color-bg-base)',
      colorBgContainer: 'var(--color-ui-base)',
      colorBgElevated: 'var(--color-ui-base)',
      colorText: 'var(--color-text-base)',
      colorTextSecondary: 'var(--color-text-muted)',
      colorBorder: 'var(--color-border)',
      colorSplit: 'var(--color-border)',
    },

    // === COMPONENT-LEVEL OVERRIDES ===
    components: {
      Button: {
        primaryShadow: 'var(--shadow-sm)',
      },
      Card: {
        boxShadow: 'var(--shadow-md)',
        colorBorderSecondary: 'transparent',
      },
      Modal: {
        boxShadow: 'var(--shadow-lg)',
        colorSplit: 'transparent',
      },
      
      // === THIS IS THE FULLY CORRECTED MENU CONFIGURATION ===
      Menu: {
        // --- Core Item Colors ---
        itemBg: 'transparent', // The default background of all menu items is transparent
        itemColor: 'var(--color-text-muted)', // Default text color for non-selected items

        // --- Hover State ---
        itemHoverBg: 'var(--color-ui-hover)', // Background on hover
        itemHoverColor: 'var(--color-text-base)', // Text color on hover

        // --- Selected State (The critical part) ---
        itemSelectedBg: 'var(--color-ui-active)', // Subtle background for the selected item
        itemSelectedColor: 'var(--color-primary)', // Brand color for text/icon of the selected item
        
        // --- Active State (when clicking) ---
        itemActiveBg: 'var(--color-ui-active)',

        // --- Sub-menu & Group styles ---
        subMenuItemBg: 'transparent',
        groupTitleColor: 'var(--color-text-muted)',
      },
    },
  };
};