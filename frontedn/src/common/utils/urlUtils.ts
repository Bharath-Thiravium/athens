// src/common/utils/urlUtils.ts

/**
 * Converts a relative media URL to an absolute URL
 * @param url The URL to convert
 * @returns The absolute URL
 */
export const getAbsoluteMediaUrl = (url: string | null): string | null => {
  if (!url) return null;
  
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
  const baseUrlTrimmed = baseUrl.replace(/\/$/, '');
  
  if (url.startsWith('/media/')) {
    return `${baseUrlTrimmed}${url}`;
  } else if (url.startsWith('media/')) {
    return `${baseUrlTrimmed}/${url}`;
  }
  
  return url;
};

/**
 * Creates a cache key for company data based on username and usertype
 * @param username The username
 * @param usertype The user type
 * @returns The cache key
 */
export const getCompanyDataCacheKey = (username: string | null, usertype: string | null): string => {
  return `company_data_${username || 'unknown'}_${usertype || 'unknown'}`;
};