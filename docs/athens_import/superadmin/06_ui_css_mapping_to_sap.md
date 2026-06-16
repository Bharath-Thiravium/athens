# Athens Super Admin Module - UI/CSS Mapping to SAP

## Athens CSS Framework Analysis

### Primary CSS Framework
**Athens uses**: Ant Design (antd) + Tailwind CSS + Custom CSS variables

**Key Files**:
- `app/frontend/src/common/styles/global.css` - Global styles and CSS variables
- `app/frontend/tailwind.config.js` - Tailwind configuration
- Ant Design components with custom theming

### CSS Variable System
**File**: `app/frontend/src/common/styles/global.css`

Athens uses CSS custom properties for theming:
```css
:root {
  --color-primary: #1890ff;
  --color-bg-base: #ffffff;
  --color-bg-container: #ffffff;
  --color-text-base: #000000d9;
  --color-text-muted: #00000073;
  --color-border: #d9d9d9;
  --color-ui-hover: #f5f5f5;
}

[data-theme="dark"] {
  --color-primary: #1890ff;
  --color-bg-base: #141414;
  --color-bg-container: #1f1f1f;
  --color-text-base: #ffffffd9;
  --color-text-muted: #ffffff73;
  --color-border: #434343;
  --color-ui-hover: #262626;
}
```

## Athens UI Components Used in Super Admin

### Layout Components

#### 1. SuperadminLayout Structure
```typescript
<Layout className="dashboard-layout !bg-color-bg-base" hasSider>
  <Sider theme={theme} width={sidebarWidth} collapsed={collapsed}>
    <Menu mode="inline" selectedKeys={[selectedKey]} items={menuItems} />
  </Sider>
  <Layout>
    <Header className="dashboard-header">
      <Button icon={<MenuFoldOutlined />} onClick={toggleSidebar} />
      <Typography.Title level={4}>{currentTitle}</Typography.Title>
      <Dropdown menu={profileMenu}>
        <Avatar>{username[0]}</Avatar>
      </Dropdown>
    </Header>
    <Content className="dashboard-content">
      <Outlet />
    </Content>
  </Layout>
</Layout>
```

**SAP Mapping**:
- `Layout` → SAP's main container class
- `Sider` → SAP's sidebar/navigation component
- `Header` → SAP's header bar component
- `Content` → SAP's main content area

#### 2. Card-Based Layout
```typescript
<Card title="Tenants (Companies)" extra={<Button type="primary">New Tenant</Button>}>
  <Table dataSource={tenants} columns={columns} />
</Card>
```

**SAP Mapping**:
- `Card` → SAP's panel/card component
- `Card.title` → SAP's panel header
- `Card.extra` → SAP's panel actions area

### Data Display Components

#### 1. Table Component
```typescript
<Table
  rowKey="id"
  dataSource={tenants}
  columns={columns}
  loading={loading}
  pagination={{ pageSize: 10 }}
/>
```

**SAP Mapping**:
- `Table` → SAP's data table component
- `pagination` → SAP's pagination controls
- `loading` → SAP's loading spinner/skeleton

#### 2. Metric Cards
```typescript
<Row gutter={[16, 16]}>
  <Col xs={24} sm={12} md={6}>
    <Card title="Total Tenants" bordered>
      <Typography.Title level={2}>{totalTenants}</Typography.Title>
    </Card>
  </Col>
</Row>
```

**SAP Mapping**:
- `Row`/`Col` → SAP's grid system
- Metric cards → SAP's KPI/metric display components

### Form Components

#### 1. Modal Forms
```typescript
<Modal
  open={modalVisible}
  title="Create Tenant"
  onCancel={() => setModalVisible(false)}
  onOk={handleSubmit}
>
  <Form form={form} layout="vertical">
    <Form.Item name="name" label="Name" rules={[{ required: true }]}>
      <Input />
    </Form.Item>
    <Form.Item name="status" label="Status">
      <Select options={statusOptions} />
    </Form.Item>
  </Form>
</Modal>
```

**SAP Mapping**:
- `Modal` → SAP's dialog/modal component
- `Form` → SAP's form container
- `Form.Item` → SAP's form field wrapper
- `Input` → SAP's text input component
- `Select` → SAP's dropdown component

#### 2. Checkbox Groups
```typescript
<Checkbox.Group value={selectedModules} onChange={setSelectedModules}>
  <Space direction="vertical">
    {modules.map(module => (
      <Checkbox key={module} value={module}>
        {formatModuleLabel(module)}
      </Checkbox>
    ))}
  </Space>
</Checkbox.Group>
```

**SAP Mapping**:
- `Checkbox.Group` → SAP's checkbox group component
- `Checkbox` → SAP's individual checkbox
- `Space` → SAP's spacing/layout utility

### Navigation Components

#### 1. Menu System
```typescript
<Menu
  mode="inline"
  selectedKeys={[selectedKey]}
  onClick={handleMenuClick}
  theme={theme}
  items={menuItems}
  inlineCollapsed={collapsed}
/>
```

**SAP Mapping**:
- `Menu` → SAP's navigation menu component
- `Menu.Item` → SAP's menu item
- `selectedKeys` → SAP's active/selected state
- `inlineCollapsed` → SAP's collapsed menu state

#### 2. Breadcrumb/Title
```typescript
<Typography.Title level={4} style={{ margin: 0 }}>
  {currentTitle}
</Typography.Title>
```

**SAP Mapping**:
- `Typography.Title` → SAP's heading component
- Level hierarchy → SAP's heading size classes

### Interactive Components

#### 1. Action Buttons
```typescript
<Space>
  <Button size="small" onClick={() => openEdit(record)}>Edit</Button>
  <Button size="small" onClick={() => openModules(record)}>Modules</Button>
  <Button danger size="small" onClick={() => handleSuspend(record)}>Suspend</Button>
</Space>
```

**SAP Mapping**:
- `Button` → SAP's button component
- `danger` prop → SAP's destructive/danger button variant
- `size="small"` → SAP's button size variants
- `Space` → SAP's button group/spacing

#### 2. Dropdown Menus
```typescript
<Dropdown menu={profileMenu} placement="bottomRight" trigger={['click']}>
  <Avatar size="large" className="cursor-pointer">
    {username[0]}
  </Avatar>
</Dropdown>
```

**SAP Mapping**:
- `Dropdown` → SAP's dropdown/popover component
- `Avatar` → SAP's user avatar component
- `placement` → SAP's positioning options

## Mapping Strategy to SAP CSS

### 1. Direct Component Mapping

**Athens Component** → **SAP Equivalent**
- `Layout` → `.sap-layout-container`
- `Card` → `.sap-panel` or `.sap-card`
- `Table` → `.sap-data-table`
- `Button` → `.sap-button`
- `Input` → `.sap-input-field`
- `Modal` → `.sap-dialog`
- `Menu` → `.sap-navigation-menu`

### 2. CSS Variable Mapping

**Athens Variables** → **SAP CSS Variables**
```css
/* Athens */
--color-primary: #1890ff;
--color-bg-base: #ffffff;
--color-text-base: #000000d9;

/* Map to SAP */
--sap-primary-color: #0070f2;
--sap-background-color: #ffffff;
--sap-text-color: #32363a;
```

### 3. Spacing and Typography

**Athens Tailwind Classes** → **SAP Spacing Classes**
- `p-4` → `.sap-padding-medium`
- `m-2` → `.sap-margin-small`
- `gap-3` → `.sap-gap-medium`

**Athens Typography** → **SAP Typography**
- `Typography.Title level={4}` → `.sap-heading-h4`
- `Typography.Text` → `.sap-text-body`
- `text-color-text-muted` → `.sap-text-secondary`

### 4. Theme System Integration

**Athens Theme Toggle** → **SAP Theme System**
```typescript
// Athens approach
const { setTheme, effectiveTheme } = useTheme();

// SAP integration
const { setSAPTheme, currentSAPTheme } = useSAPTheme();
```

## Reusable vs Custom Components

### Can Reuse Directly from SAP
- **Layout containers**: Main layout, sidebar, header
- **Form components**: Input fields, dropdowns, checkboxes
- **Data display**: Tables, cards, lists
- **Navigation**: Menus, breadcrumbs
- **Buttons**: All button variants and sizes

### Need Thin Wrapper Components
- **Theme toggle**: Wrap SAP theme system
- **Notification system**: Adapt to SAP's notification API
- **Modal dialogs**: Ensure consistent behavior
- **Loading states**: Use SAP's loading indicators

### Athens-Specific Logic to Preserve
- **Responsive sidebar behavior**: Mobile collapse/expand
- **Form validation patterns**: Error handling and display
- **Data normalization**: `normalizeList()` function
- **API error handling**: Consistent error message display

## Implementation Recommendations

### 1. Create SAP Component Wrappers
```typescript
// components/sap-wrappers/SAPCard.tsx
export const SAPCard: React.FC<CardProps> = ({ title, extra, children, ...props }) => {
  return (
    <div className="sap-panel" {...props}>
      <div className="sap-panel-header">
        <h3 className="sap-panel-title">{title}</h3>
        {extra && <div className="sap-panel-actions">{extra}</div>}
      </div>
      <div className="sap-panel-content">{children}</div>
    </div>
  );
};
```

### 2. Maintain Athens Logic, Replace UI
```typescript
// Keep Athens state management and API calls
const [tenants, setTenants] = useState<Tenant[]>([]);
const [loading, setLoading] = useState(false);

// Replace Ant Design Table with SAP Table
<SAPTable
  data={tenants}
  columns={columns}
  loading={loading}
  onRowAction={handleRowAction}
/>
```

### 3. CSS Variable Bridge
```css
/* Bridge Athens variables to SAP */
:root {
  --athens-primary: var(--sap-primary-color);
  --athens-bg-base: var(--sap-background-color);
  --athens-text-base: var(--sap-text-color);
}
```

### 4. Preserve Responsive Behavior
```typescript
// Keep Athens responsive logic
const { isMobile, isTablet } = useResponsive();

// Apply to SAP components
<div className={`sap-layout ${isMobile ? 'sap-layout-mobile' : ''}`}>
```

This mapping strategy allows you to preserve all Athens Super Admin functionality while seamlessly integrating with SAP's existing CSS framework and design system.