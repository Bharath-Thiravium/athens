/**
 * Production-Grade Defensive API Utilities
 * 
 * CRITICAL: Ensures NO undefined/null values ever reach Ant Design components
 * which internally call .toString() and crash the application.
 */

import { message } from 'antd';

// MANDATORY: Safe value extractors with strict type checking
export const safeString = (value: any, fallback: string = '-'): string => {
  if (value === null || value === undefined) return fallback;
  if (typeof value === 'string') return value;
  if (typeof value === 'number' && !isNaN(value)) return value.toString();
  if (typeof value === 'boolean') return value.toString();
  if (typeof value === 'object') {
    try {
      return JSON.stringify(value);
    } catch {
      return fallback;
    }
  }
  return fallback;
};

export const safeNumber = (value: any, fallback: number = 0): number => {
  if (value === null || value === undefined) return fallback;
  if (typeof value === 'number' && !isNaN(value) && isFinite(value)) return value;
  if (typeof value === 'string') {
    const parsed = parseFloat(value);
    return isNaN(parsed) || !isFinite(parsed) ? fallback : parsed;
  }
  if (typeof value === 'boolean') return value ? 1 : 0;
  return fallback;
};

export const safeArray = <T>(value: any, fallback: T[] = []): T[] => {
  if (Array.isArray(value)) {
    // Filter out null/undefined items to prevent crashes
    return value.filter(item => item !== null && item !== undefined);
  }
  return fallback;
};

export const safeObject = <T>(value: any, fallback: T | {} = {}): T => {
  if (value && typeof value === 'object' && !Array.isArray(value)) return value;
  return fallback as T;
};

// CRITICAL: Safe percentage calculation for progress bars
export const safePercentage = (value: any, total: any, fallback: number = 0): number => {
  const safeValue = safeNumber(value);
  const safeTotal = safeNumber(total);
  if (safeTotal === 0) return fallback;
  const result = Math.round((safeValue / safeTotal) * 100);
  return Math.min(Math.max(result, 0), 100); // Clamp between 0-100
};

// MANDATORY: Ant Design component prop sanitizers
export const antdSafe = {
  // For Statistic components
  statistic: (value: any, suffix: string = '') => ({
    value: safeNumber(value),
    suffix: safeString(suffix)
  }),

  // For Progress components
  progress: (percent: any) => ({
    percent: Math.min(Math.max(safeNumber(percent), 0), 100)
  }),

  // For Tag components
  tag: (children: any, color?: string) => ({
    children: safeString(children),
    color: color ? safeString(color) : undefined
  }),

  // For Table rowKey
  rowKey: (record: any, index: number) => {
    const id = record?.id || record?.key || record?.observationID;
    return safeString(id, `row-${index}-${Date.now()}`);
  },

  // For pagination
  pagination: (total: any, current: any, pageSize: any) => ({
    total: safeNumber(total),
    current: safeNumber(current, 1),
    pageSize: safeNumber(pageSize, 10)
  })
};

// CRITICAL: Chart data sanitizers
export const chartSafe = {
  // Sanitize chart data arrays
  data: (data: any) => {
    const safeData = safeArray(data);
    return safeData.map((item: any, index: number) => {
      if (!item || typeof item !== 'object') {
        return { name: `Item ${index}`, value: 0 };
      }
      
      // Ensure all chart items have required fields
      return {
        ...item,
        name: safeString(item.name, `Item ${index}`),
        value: safeNumber(item.value),
        // Preserve other fields but make them safe
        ...Object.keys(item).reduce((acc, key) => {
          if (key !== 'name' && key !== 'value') {
            acc[key] = item[key] === null || item[key] === undefined ? 0 : item[key];
          }
          return acc;
        }, {} as any)
      };
    });
  },

  // Sanitize pie chart data
  pieData: (data: any) => {
    const safeData = safeArray(data);
    return safeData.map((item: any, index: number) => ({
      name: safeString(item?.name, `Segment ${index}`),
      value: safeNumber(item?.value),
      color: safeString(item?.color, '#8884d8')
    }));
  }
};

// API Response Validators
export interface SafeApiResponse<T> {
  success: boolean;
  data: T;
  error?: string;
}

export const validateApiResponse = <T>(response: any): SafeApiResponse<T> => {
  try {
    if (!response) {
      return { success: false, data: {} as T, error: 'No response received' };
    }

    if (response.data) {
      return { success: true, data: response.data };
    }

    return { success: true, data: response };
  } catch (error) {
    return { success: false, data: {} as T, error: 'Invalid response format' };
  }
};

// CRITICAL: Safe API call wrapper with proper error handling
export const safeApiCall = async <T>(
  apiCall: () => Promise<any>,
  fallbackData: T,
  errorMessage: string = 'Failed to load data'
): Promise<SafeApiResponse<T>> => {
  try {
    const response = await apiCall();
    const validated = validateApiResponse<T>(response);
    
    if (!validated.success) {
      console.warn('API validation failed:', validated.error);
      return { success: false, data: fallbackData, error: validated.error };
    }

    return validated;
  } catch (error: any) {
    console.error('API call failed:', error);
    
    // Don't show error message for tenant-related errors (handled by middleware)
    const isTenantError = error?.response?.data?.error?.includes('TENANT_ERROR');
    const isAuthError = error?.response?.status === 401;
    
    if (!isTenantError && !isAuthError) {
      message.error(errorMessage);
    }
    
    return { 
      success: false, 
      data: fallbackData, 
      error: error?.message || 'Unknown error' 
    };
  }
};

// MANDATORY: Default data structures
export const getDefaultDashboardData = () => ({
  statistics: {
    permits: { total: 0, this_period: 0, change_percentage: 0, pending_approvals: 0 },
    safety_observations: { total: 0, this_period: 0, change_percentage: 0, critical: 0 },
    workers: { total: 0, active: 0, this_period: 0, change_percentage: 0, on_leave: 0 },
    pending_approvals: { total: 0, permits: 0, incidents: 0 },
    attendance: { today: 0, present_count: 0, absent_count: 0 },
    incidents: { 
      total: 0, 
      this_period: 0, 
      change_percentage: 0,
      severity_breakdown: { critical: 0, high: 0, medium: 0, low: 0 }
    },
    compliance: { score: 0, audits_completed: 0, non_conformities: 0 }
  },
  charts: {
    permit_status: [],
    safety_trend: [],
    incident_trend: [],
    worker_distribution: [],
    compliance_score: [],
    training_progress: [],
    environmental_metrics: []
  },
  recent_activity: [],
  alerts: [],
  kpis: []
});

export const getDefaultTableData = () => ({
  count: 0,
  results: [],
  next: null,
  previous: null
});

// CRITICAL: Safe render helpers that NEVER return undefined
export const safeRender = {
  // Safe table cell renderer - NEVER returns undefined
  cell: (value: any, fallback: string = '-') => {
    return safeString(value, fallback);
  },

  // Safe tag renderer with guaranteed props
  tag: (value: any, colorMap: Record<string, string> = {}, fallback: string = 'default') => {
    const safeValue = safeString(value);
    const color = colorMap[safeValue] || fallback;
    return { value: safeValue, color };
  },

  // Safe progress renderer - always returns valid percentage
  progress: (value: any, total: any = 100) => {
    return safePercentage(value, total);
  },

  // Safe statistic renderer - guaranteed number
  statistic: (value: any, suffix: string = '') => {
    return antdSafe.statistic(value, suffix);
  }
};

// CRITICAL: Component state validators
export const validateComponentState = {
  // Validate dashboard state before rendering
  dashboard: (state: any) => {
    if (!state || typeof state !== 'object') {
      return { isValid: false, data: getDefaultDashboardData() };
    }
    
    return {
      isValid: true,
      data: {
        ...getDefaultDashboardData(),
        ...state,
        statistics: {
          ...getDefaultDashboardData().statistics,
          ...safeObject(state.statistics)
        },
        charts: {
          ...getDefaultDashboardData().charts,
          ...safeObject(state.charts)
        }
      }
    };
  },

  // Validate table state
  table: (state: any) => {
    if (!state || typeof state !== 'object') {
      return { isValid: false, data: getDefaultTableData() };
    }
    
    return {
      isValid: true,
      data: {
        ...getDefaultTableData(),
        ...state,
        results: safeArray(state.results)
      }
    };
  }
};

// CRITICAL: Safe date formatter that never crashes
export const safeFormatDate = (date: any, format: string = 'DD/MM/YYYY', fallback: string = '-'): string => {
  try {
    if (!date) return fallback;
    
    const dateObj = new Date(date);
    if (isNaN(dateObj.getTime())) return fallback;
    
    if (format === 'DD/MM/YYYY') {
      return dateObj.toLocaleDateString('en-GB');
    }
    
    return dateObj.toLocaleDateString();
  } catch {
    return fallback;
  }
};

// CRITICAL: Safe array operations that never crash
export const safeMap = <T, R>(
  array: any, 
  mapper: (item: T, index: number) => R, 
  fallback: R[] = []
): R[] => {
  try {
    const safeArr = safeArray<T>(array);
    return safeArr.map((item, index) => {
      try {
        return mapper(item, index);
      } catch (error) {
        console.warn('Mapper function failed for item:', item, error);
        return null as any;
      }
    }).filter(item => item !== null);
  } catch {
    return fallback;
  }
};

// CRITICAL: Error boundary fallback data
export const getErrorFallbackData = (componentName: string) => ({
  error: true,
  message: `${componentName} encountered an error`,
  data: null
});

// CRITICAL: Loading state helpers
export const createLoadingState = <T>(initialData: T) => ({
  loading: false,
  error: null,
  data: initialData
});

export default {
  safeString,
  safeNumber,
  safeArray,
  safeObject,
  safePercentage,
  antdSafe,
  chartSafe,
  validateApiResponse,
  safeApiCall,
  getDefaultDashboardData,
  getDefaultTableData,
  safeRender,
  validateComponentState,
  getErrorFallbackData,
  createLoadingState,
  safeFormatDate,
  safeMap
};