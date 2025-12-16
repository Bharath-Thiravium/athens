# 🏗️ Dashboard Layout Structure Guide

## 📋 Overview

This document outlines the improved layout structure for the dashboard application, providing consistent spacing, responsive design, and proper component organization.

## 🎯 Layout Architecture

### 1. **Main Layout Components**

```
App.tsx (Root)
├── ThemeProvider + NotificationsProvider
└── Dashboard.tsx (Main Layout)
    ├── Fixed Sidebar (250px/88px)
    ├── Fixed Header (80px)
    └── Content Area (Scrollable)
        └── PageLayout (Standardized wrapper)
            ├── Page Header (Title, Breadcrumbs, Actions)
            └── Page Content (Your components)
```

### 2. **Layout Dimensions**

- **Sidebar**: 250px (expanded) / 88px (collapsed)
- **Header**: 80px height (fixed)
- **Content**: `calc(100vh - 80px)` (scrollable)
- **Content Padding**: 24px (desktop) / 16px (mobile) / 32px (large screens)

## 🔧 Key Improvements Made

### ✅ **Fixed Layout Issues**

1. **Removed `marginTop: '80px'`** from content area
2. **Added `.dashboard-content-wrapper`** for consistent spacing
3. **Improved responsive behavior** across all screen sizes
4. **Created `PageLayout` component** for standardized page structure

### ✅ **New CSS Classes**

```css
/* Main content wrapper */
.dashboard-content-wrapper {
  padding: 1.5rem;
  min-height: calc(100vh - 80px);
  max-width: 100%;
  margin: 0 auto;
}

/* Page layout component */
.page-layout {
  width: 100%;
  max-width: 100%;
}
```

## 🎨 Using the New Layout System

### **Option 1: Use PageLayout Component (Recommended)**

```tsx
import PageLayout from '@common/components/PageLayout';

const MyPage = () => {
  return (
    <PageLayout
      title="Page Title"
      subtitle="Optional description"
      breadcrumbs={[
        { title: 'Section', href: '/dashboard/section' },
        { title: 'Current Page' }
      ]}
      actions={
        <Button type="primary">Action Button</Button>
      }
    >
      {/* Your page content */}
      <Card>
        <p>Your content here</p>
      </Card>
    </PageLayout>
  );
};
```

### **Option 2: Direct Content (Legacy Support)**

```tsx
const MyPage = () => {
  return (
    <div className="p-6">
      {/* Your existing content */}
    </div>
  );
};
```

## 📱 Responsive Breakpoints

- **Mobile**: `< 640px` - 16px padding
- **Tablet**: `640px - 1024px` - 24px padding  
- **Desktop**: `1024px - 1200px` - 24px padding
- **Large**: `> 1200px` - 32px padding, max-width 1400px

## 🎯 Best Practices

### ✅ **Do's**

- Use `PageLayout` for new pages
- Keep consistent spacing with the wrapper
- Use proper semantic HTML structure
- Follow the breadcrumb pattern
- Group related actions in the header

### ❌ **Don'ts**

- Don't add custom margins to override layout
- Don't use fixed positioning inside content
- Don't break the responsive grid system
- Don't hardcode spacing values

## 🔄 Migration Guide

### **For Existing Pages:**

1. **Wrap content in PageLayout**:
   ```tsx
   // Before
   <div className="max-w-5xl mx-auto">
     <Card>
       <Title>My Page</Title>
       {/* content */}
     </Card>
   </div>

   // After
   <PageLayout title="My Page" subtitle="Description">
     <Card>
       {/* content */}
     </Card>
   </PageLayout>
   ```

2. **Remove custom spacing**:
   - Remove `max-w-*` classes from root elements
   - Remove custom `margin` and `padding` from page containers
   - Let PageLayout handle the spacing

3. **Update imports**:
   ```tsx
   import PageLayout from '@common/components/PageLayout';
   ```

## 🎨 Theme Integration

The layout system is fully integrated with the theme system:

- **CSS Variables**: All colors use theme variables
- **Dark Mode**: Automatic theme switching
- **Responsive**: Mobile-first approach
- **Accessibility**: Proper focus states and ARIA labels

## 🚀 Next Steps

1. **Migrate existing pages** to use PageLayout
2. **Test responsive behavior** on all screen sizes
3. **Verify theme switching** works correctly
4. **Update any custom CSS** that conflicts with the new system

## 📞 Support

If you encounter any layout issues:

1. Check if you're using the correct wrapper classes
2. Verify responsive breakpoints are working
3. Ensure theme variables are properly applied
4. Test with both light and dark themes
