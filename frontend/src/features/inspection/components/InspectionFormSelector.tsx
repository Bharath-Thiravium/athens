import React from 'react';
import { Card, Row, Col, Button } from 'antd';
import { useNavigate } from 'react-router-dom';
import { FileTextOutlined } from '@ant-design/icons';

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

  const handleFormSelect = (formId: string) => {
    navigate(`/dashboard/inspection/forms/${formId}`);
  };

  return (
    <div className="p-6">
      <Card>
        <h2 className="text-2xl font-bold mb-6">Select Inspection Form</h2>
        <Row gutter={[16, 16]}>
          {inspectionForms.map((form) => (
            <Col xs={24} sm={12} md={8} lg={6} key={form.id}>
              <Card
                hoverable
                className="h-full"
                actions={[
                  <Button
                    type="primary"
                    icon={<FileTextOutlined />}
                    onClick={() => handleFormSelect(form.id)}
                  >
                    Select Form
                  </Button>
                ]}
              >
                <Card.Meta
                  title={form.title}
                  description={
                    <div>
                      <p className="text-sm text-gray-600 mb-2">{form.description}</p>
                      <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        {form.category}
                      </span>
                    </div>
                  }
                />
              </Card>
            </Col>
          ))}
        </Row>
      </Card>
    </div>
  );
};

export default InspectionFormSelector;