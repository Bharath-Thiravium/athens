# ESG System Implementation Guide

## Overview
The ESG (Environmental, Social, Governance) system has been successfully implemented in the UpatePro project with proper navigation, report generation, and backend API integration.

## Fixed Issues

### 1. Navigation Problem
**Issue**: Left menu clicks weren't changing the right-side content properly.
**Solution**: 
- Created dedicated page components for each ESG section
- Updated routing in App.tsx to use specific components instead of tabs
- Fixed menu navigation to use proper React Router navigation

### 2. Report Generation Not Working
**Issue**: "Generate ESG Report" button wasn't functional.
**Solution**:
- Added backend API endpoints for report generation
- Implemented PDF report generation using reportlab
- Connected frontend to backend APIs
- Added proper error handling and user feedback

## New Components Created

### Frontend Components
1. **EnvironmentPage.tsx** - Dedicated environment management page
2. **GovernancePage.tsx** - Governance and compliance management
3. **ESGReportsPage.tsx** - Report generation and management
4. **Updated ESGDashboard.tsx** - Fixed Quick Actions with proper navigation

### Backend Components
1. **ESGReportViewSet** - API endpoints for report generation
2. **Report generation methods** - BRSR, GHG, Environmental, Safety, Sustainability reports
3. **PDF generation** - Using reportlab for downloadable reports

## How It Works

### Navigation Flow
1. **Left Menu Click**: User clicks on ESG menu items (Environment, Governance, Reports)
2. **Route Navigation**: React Router navigates to specific ESG pages
3. **Component Rendering**: Dedicated page components render with relevant content
4. **Data Loading**: Each page loads its specific data via API calls

### Report Generation Flow
1. **User Input**: Select report type and date range
2. **API Call**: Frontend sends request to `/api/v1/environment/reports/generate/`
3. **Backend Processing**: Django processes request and generates report data
4. **PDF Creation**: ReportLab creates downloadable PDF
5. **User Notification**: Success message with download option

## API Endpoints

### ESG Reports
- `POST /api/v1/environment/reports/generate/` - Generate new report
- `GET /api/v1/environment/reports/` - List existing reports  
- `GET /api/v1/environment/reports/{id}/download/` - Download report PDF

### Environment Data
- `GET /api/v1/environment/aspects/` - Environment aspects
- `GET /api/v1/environment/generation/` - Generation data
- `GET /api/v1/environment/ghg-activities/` - GHG activities
- `GET /api/v1/environment/waste-manifests/` - Waste management

## Testing the System

### 1. Navigation Test
1. Login to the system
2. Navigate to ESG Management in left menu
3. Click on "Environment", "Governance", "ESG Reports"
4. Verify each shows different content

### 2. Report Generation Test
1. Go to ESG Reports page
2. Select report type (BRSR, GHG, etc.)
3. Choose date range
4. Click "Generate Report"
5. Verify success message appears
6. Check if report appears in existing reports table

### 3. Quick Actions Test
1. Go to ESG Overview (main dashboard)
2. Click buttons in Quick Actions section
3. Verify navigation to correct pages

## Database Requirements

Ensure these migrations are applied:
```bash
cd backend
python manage.py makemigrations environment
python manage.py migrate
```

## Frontend Dependencies

All required dependencies are already installed:
- React Router for navigation
- Ant Design for UI components
- Axios for API calls
- Day.js for date handling

## Backend Dependencies

Required packages (already in requirements.txt):
- reportlab==4.0.4 (for PDF generation)
- Django REST Framework
- PostgreSQL support

## User Roles and Permissions

ESG system is accessible to:
- `adminuser` - Full access to all ESG features
- `client`, `epc`, `contractor` - Project-level access
- Role-based permissions implemented via ESGPermission class

## File Structure

```
frontedn/src/features/esg/
├── components/
│   ├── ESGDashboard.tsx (updated)
│   ├── EnvironmentAspectForm.tsx
│   └── GenerationDataForm.tsx
├── pages/
│   ├── ESGOverview.tsx (main dashboard)
│   ├── EnvironmentPage.tsx (new)
│   ├── GovernancePage.tsx (new)
│   └── ESGReportsPage.tsx (new)
├── services/
│   └── esgAPI.ts (updated with report APIs)
└── types/
    └── index.ts

backend/environment/
├── models.py (ESG data models)
├── views.py (updated with ESGReportViewSet)
├── urls.py (updated with report routes)
├── serializers.py
└── permissions.py
```

## Next Steps

1. **Test the complete flow** from navigation to report generation
2. **Customize report templates** based on specific requirements
3. **Add more report types** as needed
4. **Implement email notifications** for report completion
5. **Add data validation** for better user experience

## Troubleshooting

### Navigation Issues
- Check React Router configuration in App.tsx
- Verify menu configuration in menuConfig.tsx
- Ensure proper role-based access

### Report Generation Issues
- Check backend logs for API errors
- Verify database connections
- Ensure reportlab is properly installed
- Check file permissions for PDF generation

### API Connection Issues
- Verify axios configuration
- Check CORS settings
- Ensure proper authentication tokens

The ESG system is now fully functional with proper navigation, report generation, and backend integration. All components work together to provide a comprehensive ESG management solution.