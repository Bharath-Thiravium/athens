// src/common/context/ThemeContext.tsx

import React, { createContext, useState, useContext, useEffect, useLayoutEffect } from 'react';
import type { ReactNode } from 'react';

// The type now includes 'system' for automatic OS detection.
type Theme = 'dark' | 'light' | 'system';
type EffectiveTheme = 'dark' | 'light';

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void; // Allow direct setting for UI controls
  effectiveTheme: EffectiveTheme; // The actual theme being applied ('light' or 'dark')
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const getSystemTheme = (): EffectiveTheme => {
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

export const ThemeProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [theme, setThemeState] = useState<Theme>(() => {
    // Read from localStorage, default to 'system'
    return (localStorage.getItem('dashboard-theme') as Theme) || 'system'; 
  });

  const [effectiveTheme, setEffectiveTheme] = useState<EffectiveTheme>(() => {
    // Calculate initial effective theme
    return theme === 'system' ? getSystemTheme() : theme;
  });

  // Effect to listen for OS theme changes if theme is 'system'
  useEffect(() => {
    if (theme !== 'system') return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const handleChange = () => {
      setEffectiveTheme(mediaQuery.matches ? 'dark' : 'light');
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [theme]);

  // Wrapper function for setting the theme to handle localStorage and state
  const setTheme = (newTheme: Theme) => {
    localStorage.setItem('dashboard-theme', newTheme);
    setThemeState(newTheme);
    // Immediately update effective theme when the setting changes
    if (newTheme === 'system') {
      setEffectiveTheme(getSystemTheme());
    } else {
      setEffectiveTheme(newTheme);
    }
  };

  // Apply the 'effectiveTheme' class to the document root
  useLayoutEffect(() => {
    const root = document.documentElement;
    root.classList.remove('light', 'dark');
    root.classList.add(effectiveTheme);
  }, [effectiveTheme]);

  return (
    <ThemeContext.Provider value={{ theme, setTheme, effectiveTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};