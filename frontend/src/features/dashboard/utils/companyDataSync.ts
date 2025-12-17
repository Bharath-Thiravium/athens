/**
 * Utility functions for synchronizing company data between components
 * This helps ensure that company logo and name updates are properly
 * reflected across the application, especially in the dashboard.
 */

export interface CompanyData {
  logoUrl?: string;
  companyName?: string;
}

/**
 * Dispatches a company logo update event
 */
export const dispatchLogoUpdate = (logoUrl: string) => {
  const event = new CustomEvent('company_logo_updated', {
    detail: { logoUrl }
  });
  window.dispatchEvent(event);
  localStorage.setItem('company_logo_url', logoUrl);
};

/**
 * Dispatches a company name update event
 */
export const dispatchNameUpdate = (companyName: string) => {
  const event = new CustomEvent('company_name_updated', {
    detail: { companyName }
  });
  window.dispatchEvent(event);
  localStorage.setItem('company_name', companyName);
};

/**
 * Dispatches admin logo update event
 */
export const dispatchAdminLogoUpdate = (logoUrl: string) => {
  const event = new CustomEvent('admin_logo_updated', {
    detail: { logoUrl }
  });
  window.dispatchEvent(event);
  localStorage.setItem('company_logo_url', logoUrl);
};

/**
 * Dispatches admin company name update event
 */
export const dispatchAdminCompanyUpdate = (companyName: string) => {
  const event = new CustomEvent('admin_company_updated', {
    detail: { companyName }
  });
  window.dispatchEvent(event);
  localStorage.setItem('company_name', companyName);
};

/**
 * Gets cached company data from localStorage
 */
export const getCachedCompanyData = (): CompanyData => {
  return {
    logoUrl: localStorage.getItem('company_logo_url') || undefined,
    companyName: localStorage.getItem('company_name') || undefined,
  };
};

/**
 * Clears cached company data
 */
export const clearCachedCompanyData = () => {
  localStorage.removeItem('company_logo_url');
  localStorage.removeItem('company_name');
};

/**
 * Debug function to log current company data state
 */
export const debugCompanyData = () => {
  const cached = getCachedCompanyData();
  console.log({
    cached,
    events: {
      company_logo_updated: 'Available',
      company_name_updated: 'Available', 
      admin_logo_updated: 'Available',
      admin_company_updated: 'Available'
    }
  });
  return cached;
};

/**
 * Test function to simulate company data updates
 */
export const testCompanyDataSync = () => {
  
  // Test company updates
  setTimeout(() => {
    dispatchLogoUpdate('https://example.com/test-logo.png');
    dispatchNameUpdate('Test Company Name');
  }, 1000);
  
  // Test admin updates
  setTimeout(() => {
    dispatchAdminLogoUpdate('https://example.com/admin-logo.png');
    dispatchAdminCompanyUpdate('Admin Test Company');
  }, 2000);
  
};
