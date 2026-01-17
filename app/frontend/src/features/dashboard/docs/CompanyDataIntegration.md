# Company Data Integration Guide

This document explains how company logo and name data flows between the CompanyDetails, AdminDetail, and Dashboard components.

## Overview

The system supports two main sources of company data:
1. **CompanyDetails** - Used by master admins to set company-wide information
2. **AdminDetail** - Used by project admins (client, EPC, contractor) to set their specific company information

The **Dashboard** component automatically displays the appropriate logo and company name based on the user type and available data.

## Data Flow

### 1. CompanyDetails Component (`/frontedn/src/features/companydetails/companydetails.tsx`)

**Used by:** Master admins
**Endpoint:** `/authentication/companydetail/`
**Fields:** `company_name`, `company_logo`

**When data is saved:**
1. Form submits to backend
2. Backend returns updated data
3. Component dispatches events:
   - `company_logo_updated` (if logo changed)
   - `company_name_updated` (if name changed)
4. Data is cached in localStorage
5. Dashboard automatically updates

### 2. AdminDetail Component (`/frontedn/src/features/admin/components/AdminDetail.tsx`)

**Used by:** Project admins (client, EPC, contractor users)
**Endpoint:** `/authentication/admin/me/`
**Fields:** `company_name`, `logo_url`

**When data is saved:**
1. Form submits to backend for approval
2. Master admin approves the details
3. Component dispatches events:
   - `admin_logo_updated` (if logo changed)
   - `admin_company_updated` (if company name changed)
4. Data is cached in localStorage
5. Dashboard automatically updates

### 3. Dashboard Component (`/frontedn/src/features/dashboard/components/Dashboard.tsx`)

**Data Loading Strategy:**
1. **Immediate:** Load cached data from localStorage for instant display
2. **API Fetch:** Based on user type:
   - **Master admin:** Try `/authentication/companydetail/` first
   - **Project admin:** Try `/authentication/admin/me/` first, fallback to company details
   - **Other users:** Try `/authentication/admin/me/` only
3. **Event Listening:** Listen for real-time updates from other components

**Event Listeners:**
- `company_logo_updated` - From CompanyDetails component
- `company_name_updated` - From CompanyDetails component  
- `admin_logo_updated` - From AdminDetail component
- `admin_company_updated` - From AdminDetail component

## User Type Behavior

### Master Admin (`usertype: 'masteradmin'`)
- **Primary source:** CompanyDetails form
- **Dashboard shows:** Company logo and name from `/authentication/companydetail/`
- **Fallback:** Default logo (ApartmentOutlined icon) and "YourBrand" text

### Project Admins (`usertype: 'client'`, `'epc'`, `'contractor'`)
- **Primary source:** AdminDetail form (after approval)
- **Dashboard shows:** Company logo and name from `/authentication/admin/me/`
- **Fallback:** Company details if available, then defaults

### Regular Users (`django_user_type: 'clientuser'`, `'epcuser'`, `'contractoruser'`)
- **Source:** AdminDetail data from their admin
- **Dashboard shows:** Company logo and name from `/authentication/admin/me/`
- **Fallback:** Default logo and "YourBrand" text

## Implementation Details

### Event System
```typescript
// Dispatching updates (from CompanyDetails/AdminDetail)
const logoUpdateEvent = new CustomEvent('company_logo_updated', {
  detail: { logoUrl: 'https://example.com/logo.png' }
});
window.dispatchEvent(logoUpdateEvent);

// Listening for updates (in Dashboard)
window.addEventListener('company_logo_updated', (event: CustomEvent) => {
  setCompanyLogoUrl(event.detail.logoUrl);
});
```

### Caching Strategy
```typescript
// Save to cache
localStorage.setItem('company_logo_url', logoUrl);
localStorage.setItem('company_name', companyName);

// Load from cache
const cachedLogo = localStorage.getItem('company_logo_url');
const cachedName = localStorage.getItem('company_name');
```

### API Endpoints

1. **Company Details**
   - `GET /authentication/companydetail/` - Fetch company details
   - `POST/PATCH /authentication/companydetail/` - Save company details

2. **Admin Details**
   - `GET /authentication/admin/me/` - Fetch current admin details
   - `PUT /authentication/admin/detail/update/{usertype}/` - Update admin details

## Troubleshooting

### Logo not showing in dashboard
1. Check browser console for API errors
2. Verify the image URL is accessible
3. Check localStorage for cached values
4. Ensure events are being dispatched

### Company name not updating
1. Check if the form submission was successful
2. Verify the backend returns the updated company_name
3. Check localStorage for the cached value
4. Ensure the correct event is being dispatched

### Debug Tools
Use the utility functions in `/frontedn/src/features/dashboard/utils/companyDataSync.ts`:

```typescript
import { debugCompanyData, testCompanyDataSync } from '@features/dashboard/utils/companyDataSync';

// Debug current state
debugCompanyData();

// Test the sync system
testCompanyDataSync();
```

## Best Practices

1. **Always cache data** in localStorage for immediate display
2. **Dispatch events** after successful API calls
3. **Handle errors gracefully** with fallback values
4. **Use consistent event names** across components
5. **Log important operations** for debugging
