import React, { useState } from 'react';
import { Table, Button, Input, Select, Tag } from 'antd';
import { useNavigate } from 'react-router-dom';
import { FileTextOutlined } from '@ant-design/icons';

const { Search } = Input;
const { Option } = Select;

const inspectionForms = [
  {
    id: 'ac-cable-testing',
    title: 'AC Cable Testing',
    description: 'Inspection Observation Card – AC Cable (Testing)',
    category: 'Electrical'
  },
  {
    id: 'acdb-checklist',
    title: 'ACDB Checklist',
    description: 'Pre-Commissioning Checklist – LT Swgr / ACDB / DCDB / UPS panel',
    category: 'Electrical'
  },
  {
    id: 'ht-cable',
    title: 'HT Cable Checklist',
    description: 'Inverter Room/Control Room Building Final Acceptance Checklist',
    category: 'Electrical'
  },
  {
    id: 'ht-precommission',
    title: 'HT Pre-Commission',
    description: 'HT Cable Pre-Commissioning Checklist',
    category: 'Electrical'
  },
  {
    id: 'ht-precommission-template',
    title: 'HT Pre-Commission Template',
    description: 'HT Cable Pre-Commissioning Checklist Template',
    category: 'Electrical'
  },
  {
    id: 'civil-work-checklist',
    title: 'Civil Work Checklist',
    description: 'Civil Work Checklist - Before Start of Work',
    category: 'Civil'
  },
  {
    id: 'cement-register',
    title: 'Cement Register',
    description: 'Cement Register Form',
    category: 'Quality'
  },
  {
    id: 'concrete-pour-card',
    title: 'Concrete Pour Card',
    description: 'Concrete Pour Card Form',
    category: 'Quality'
  },
  {
    id: 'pcc-checklist',
    title: 'PCC Checklist',
    description: 'Check List for Plain Cement Concrete Work',
    category: 'Quality'
  },
  {
    id: 'bar-bending-schedule',
    title: 'Bar Bending Schedule',
    description: 'Bar Bending Schedule (BBS)',
    category: 'Quality'
  },
  {
    id: 'battery-charger-checklist',
    title: 'Battery Charger Installation Checklist',
    description: 'Installation Checklist for Battery Bank & Battery Charger',
    category: 'Electrical'
  },
  {
    id: 'battery-ups-checklist',
    title: 'Battery UPS Checklist',
    description: 'Pre-Commissioning Checklist - Battery & UPS',
    category: 'Electrical'
  },
  {
    id: 'bus-duct-checklist',
    title: 'Bus Duct Checklist',
    description: 'Pre-Commissioning Checklist - Bus Duct and Auxiliary Transformer',
    category: 'Electrical'
  },
  {
    id: 'control-cable-checklist',
    title: 'Control Cable Checklist',
    description: 'Installation Checklist for Control Cable',
    category: 'Electrical'
  },
  {
    id: 'control-room-audit-checklist',
    title: 'Control Room Audit Checklist',
    description: 'Control Room General Audit Checklist',
    category: 'Electrical'
  },
  {
    id: 'earthing-checklist',
    title: 'Table to Table Earthing Checklist',
    description: 'Table to Table Earthing Checklist',
    category: 'Electrical'
  },
];

const InspectionFormSelector: React.FC = () => {
  const navigate = useNavigate();
  const [filteredForms, setFilteredForms] = useState(inspectionForms);
  const [filters, setFilters] = useState({ search: '', category: '' });

  const handleFormSelect = (formId: string) => {
    navigate(`/dashboard/inspection/forms/${formId}`);
  };

  const handleSearch = (value: string) => {
    setFilters(prev => ({ ...prev, search: value }));
    applyFilters(value, filters.category);
  };

  const handleCategoryFilter = (category: string) => {
    setFilters(prev => ({ ...prev, category }));
    applyFilters(filters.search, category);
  };

  const applyFilters = (search: string, category: string) => {
    let filtered = inspectionForms;
    
    if (search) {
      filtered = filtered.filter(form => 
        form.title.toLowerCase().includes(search.toLowerCase()) ||
        form.description.toLowerCase().includes(search.toLowerCase())
      );
    }
    
    if (category) {
      filtered = filtered.filter(form => form.category === category);
    }
    
    setFilteredForms(filtered);
  };

  const columns = [
    {
      title: 'Form Title',
      dataIndex: 'title',
      key: 'title',
      sorter: (a: any, b: any) => a.title.localeCompare(b.title),
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: 'Category',
      dataIndex: 'category',
      key: 'category',
      render: (category: string) => {
        const color = category === 'Electrical' ? 'blue' : category === 'Civil' ? 'green' : 'orange';
        return <Tag color={color}>{category}</Tag>;
      },
      sorter: (a: any, b: any) => a.category.localeCompare(b.category),
    },
    {
      title: 'Action',
      key: 'action',
      render: (_, record: any) => (
        <Button
          type="primary"
          icon={<FileTextOutlined />}
          onClick={() => handleFormSelect(record.id)}
        >
          Select Form
        </Button>
      ),
    },
  ];

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-6">Select Inspection Form</h2>
      
      <div className="mb-4 flex gap-4 flex-wrap">
        <Search
          placeholder="Search forms..."
          style={{ width: 300 }}
          onSearch={handleSearch}
          onChange={(e) => handleSearch(e.target.value)}
        />
        <Select
          placeholder="Filter by category"
          style={{ width: 150 }}
          allowClear
          onChange={handleCategoryFilter}
        >
          <Option value="Electrical">Electrical</Option>
          <Option value="Civil">Civil</Option>
          <Option value="Quality">Quality</Option>
        </Select>
      </div>

      <Table
        columns={columns}
        dataSource={filteredForms}
        rowKey="id"
        size="middle"
        pagination={{
          pageSize: 15,
          showSizeChanger: true,
          showTotal: (total) => `Total ${total} forms`
        }}
      />
    </div>
  );
};

export default InspectionFormSelector;