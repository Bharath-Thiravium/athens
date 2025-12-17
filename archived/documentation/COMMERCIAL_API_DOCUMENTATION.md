# Commercial Incident Management API Documentation

## 🚀 **Overview**

This API documentation covers the enhanced, commercial-grade incident management system with advanced features for enterprise clients.

## 🔐 **Authentication & Authorization**

### **Authentication Methods**
- **JWT Token Authentication** - Primary method for API access
- **Session Authentication** - For web interface
- **API Key Authentication** - For system integrations

### **Permission Levels**
```python
# Master Admin - Full system access
admin_type = 'master'

# Project Admins - Project-level management
admin_type in ['client', 'epc', 'contractor']

# Admin Users - Operational access
admin_type in ['clientuser', 'epcuser', 'contractoruser']

# Grade-based permissions
grade in ['A', 'B', 'C']  # A=Site Incharge, B=Team Leader, C=Worker
```

## 📊 **Enhanced Incident API**

### **POST /api/incidents/** - Create Incident
```json
{
  "title": "Equipment Failure - Crane #5",
  "description": "Hydraulic system failure during lifting operation",
  "incident_type": "equipment_failure",
  "severity_level": "high",
  "location": "Construction Site - Zone A",
  "department": "Operations",
  "date_time_incident": "2024-01-15T14:30:00Z",
  "reporter_name": "John Smith",
  "immediate_action_taken": "Crane shut down, area cordoned off",
  "potential_causes": "Hydraulic seal failure suspected",
  
  // Commercial Grade Fields
  "probability_score": 3,
  "impact_score": 4,
  "estimated_cost": 25000.00,
  "cost_category": "equipment_replacement",
  "regulatory_framework": "osha",
  "regulatory_reportable": true,
  "business_impact": "moderate",
  "production_impact_hours": 8.5,
  "personnel_affected_count": 12,
  "weather_conditions": "Clear, 25°C",
  "equipment_involved": "Crane #5, Model XYZ-2000",
  "equipment_serial_numbers": "CR-2023-001",
  "work_process": "Steel beam installation",
  "work_permit_number": "WP-2024-0115",
  "safety_procedures_followed": false
}
```

### **Response - Enhanced Incident Data**
```json
{
  "id": "uuid-here",
  "incident_id": "INC-2024-0001",
  "title": "Equipment Failure - Crane #5",
  "status": "reported",
  "risk_level": "high",
  "risk_matrix_score": 12,
  "priority_score": 15,
  "escalation_level": 1,
  "days_since_reported": 0,
  "is_overdue": false,
  "completion_percentage": 10,
  "financial_impact": 25000.00,
  "estimated_completion_date": "2024-01-22T14:30:00Z",
  "risk_score_display": "12 - Medium Risk",
  // ... all other fields
}
```

## 💰 **Cost Management API**

### **POST /api/incidents/{id}/costs/** - Add Cost Entry
```json
{
  "cost_type": "equipment_replacement",
  "description": "Replacement hydraulic pump for Crane #5",
  "estimated_amount": 15000.00,
  "budget_code": "MAINT-2024-Q1",
  "department_charged": "Operations",
  "requires_approval": true
}
```

### **GET /api/incidents/{id}/costs/** - Get Cost Breakdown
```json
{
  "total_estimated": 25000.00,
  "total_actual": 18500.00,
  "cost_breakdown": [
    {
      "cost_type": "equipment_replacement",
      "estimated_amount": 15000.00,
      "actual_amount": 12000.00,
      "status": "approved"
    },
    {
      "cost_type": "production_loss",
      "estimated_amount": 10000.00,
      "actual_amount": 6500.00,
      "status": "calculated"
    }
  ]
}
```

## 📈 **Analytics & Reporting API**

### **GET /api/analytics/dashboard/** - Executive Dashboard
```json
{
  "total_incidents": 156,
  "open_incidents": 23,
  "closed_incidents": 133,
  "overdue_incidents": 5,
  "severity_distribution": [
    {"severity_level": "critical", "count": 8, "percentage": 5.1},
    {"severity_level": "high", "count": 31, "percentage": 19.9},
    {"severity_level": "medium", "count": 67, "percentage": 42.9},
    {"severity_level": "low", "count": 50, "percentage": 32.1}
  ],
  "risk_distribution": [
    {"risk_level": "very_high", "count": 12, "percentage": 7.7},
    {"risk_level": "high", "count": 28, "percentage": 17.9},
    {"risk_level": "medium", "count": 45, "percentage": 28.8},
    {"risk_level": "low", "count": 41, "percentage": 26.3},
    {"risk_level": "very_low", "count": 30, "percentage": 19.2}
  ],
  "total_cost": 2450000.00,
  "average_cost_per_incident": 15705.13,
  "average_time_to_close": "P7DT12H30M",
  "investigation_completion_rate": 0.89,
  "capa_completion_rate": 0.76,
  "monthly_trends": [
    {"month": "2024-01", "incidents": 18, "cost": 285000.00},
    {"month": "2024-02", "incidents": 22, "cost": 340000.00}
  ]
}
```

### **GET /api/analytics/risk-matrix/** - Risk Heat Map Data
```json
{
  "matrix_data": [
    [2, 4, 6, 8, 10],
    [4, 8, 12, 16, 20],
    [6, 12, 18, 24, 30],
    [8, 16, 24, 32, 40],
    [10, 20, 30, 40, 50]
  ],
  "incident_distribution": {
    "1": 5, "2": 8, "3": 12, "4": 15,
    "6": 18, "8": 22, "9": 8, "12": 25,
    "16": 12, "20": 6, "25": 3
  },
  "risk_zones": {
    "low": {"range": [1, 8], "color": "#28a745", "count": 43},
    "medium": {"range": [9, 16], "color": "#ffc107", "count": 67},
    "high": {"range": [17, 25], "color": "#dc3545", "count": 21}
  }
}
```

## 🔄 **Workflow Management API**

### **POST /api/workflows/** - Create Custom Workflow
```json
{
  "name": "Construction Site Incident Workflow",
  "description": "Workflow for construction site incidents",
  "incident_types": ["injury", "fall_from_height", "struck_by_object"],
  "workflow_steps": [
    {
      "step": 1,
      "name": "Immediate Response",
      "duration_hours": 1,
      "required_roles": ["site_supervisor"],
      "actions": ["secure_area", "provide_first_aid", "notify_management"]
    },
    {
      "step": 2,
      "name": "Investigation Assignment",
      "duration_hours": 4,
      "required_roles": ["safety_officer"],
      "actions": ["assign_investigator", "gather_witnesses"]
    }
  ],
  "escalation_rules": {
    "high_severity": {
      "escalate_after_hours": 2,
      "escalate_to": ["project_manager", "safety_director"]
    }
  },
  "notification_rules": {
    "immediate": ["site_supervisor", "safety_officer"],
    "24_hours": ["project_manager"],
    "regulatory": ["compliance_officer"]
  }
}
```

## 📚 **Knowledge Management API**

### **POST /api/incidents/{id}/learning/** - Capture Lessons Learned
```json
{
  "key_findings": "Hydraulic system failure due to inadequate maintenance schedule",
  "lessons_learned": "Regular hydraulic system inspections must be increased from monthly to bi-weekly",
  "best_practices": "Implement predictive maintenance using vibration analysis",
  "applicable_to": ["crane_operations", "heavy_equipment", "maintenance"],
  "training_required": true,
  "training_topics": "Hydraulic system maintenance, Predictive maintenance techniques",
  "policy_updates_required": true,
  "policy_recommendations": "Update maintenance schedule policy for hydraulic equipment",
  "communication_method": "toolbox_talk"
}
```

## 🏭 **Industry-Specific Configurations**

### **GET /api/configurations/industry/{industry_type}/** - Get Industry Config
```json
{
  "industry_type": "construction",
  "incident_categories": [
    {
      "name": "Fall from Height",
      "color_code": "#dc3545",
      "risk_factors": ["height", "weather", "equipment", "training"]
    },
    {
      "name": "Struck by Object",
      "color_code": "#fd7e14",
      "risk_factors": ["overhead_work", "crane_operations", "ppe"]
    }
  ],
  "risk_assessment_template": {
    "probability_criteria": {
      "1": "Very unlikely to occur (< 1% chance)",
      "2": "Unlikely to occur (1-10% chance)",
      "3": "Possible to occur (10-50% chance)",
      "4": "Likely to occur (50-90% chance)",
      "5": "Almost certain to occur (> 90% chance)"
    },
    "impact_criteria": {
      "1": "Negligible impact (minor first aid)",
      "2": "Minor impact (medical treatment)",
      "3": "Moderate impact (lost time injury)",
      "4": "Major impact (permanent disability)",
      "5": "Catastrophic impact (fatality)"
    }
  },
  "regulatory_requirements": {
    "reportable_incidents": ["injury", "fatality", "major_property_damage"],
    "reporting_timeframe": "24_hours",
    "required_documentation": ["incident_report", "witness_statements", "photos"]
  }
}
```

## 📱 **Mobile API Endpoints**

### **GET /api/mobile/incidents/nearby/** - Get Nearby Incidents
```json
{
  "latitude": 40.7128,
  "longitude": -74.0060,
  "radius_km": 5,
  "incidents": [
    {
      "incident_id": "INC-2024-0001",
      "title": "Equipment Failure",
      "severity_level": "high",
      "distance_km": 1.2,
      "status": "under_investigation"
    }
  ]
}
```

### **POST /api/mobile/incidents/quick-report/** - Quick Mobile Report
```json
{
  "title": "Slip and Fall",
  "incident_type": "injury",
  "severity_level": "medium",
  "location_gps": {"lat": 40.7128, "lng": -74.0060},
  "photos": ["base64_encoded_image_1", "base64_encoded_image_2"],
  "voice_note": "base64_encoded_audio",
  "offline_timestamp": "2024-01-15T14:30:00Z"
}
```

## 🔗 **Integration APIs**

### **Webhook Notifications**
```json
{
  "event": "incident.created",
  "incident_id": "INC-2024-0001",
  "severity_level": "high",
  "timestamp": "2024-01-15T14:30:00Z",
  "data": {
    "title": "Equipment Failure",
    "location": "Site A",
    "reporter": "John Smith"
  }
}
```

### **Export API**
```
GET /api/export/incidents/?format=excel&date_from=2024-01-01&date_to=2024-01-31
GET /api/export/incidents/?format=pdf&incident_ids=1,2,3,4,5
GET /api/export/analytics/?format=csv&report_type=monthly_summary
```

## 🎯 **Rate Limits & Quotas**

### **API Rate Limits**
- **Starter Plan**: 1,000 requests/hour
- **Professional Plan**: 5,000 requests/hour  
- **Enterprise Plan**: 25,000 requests/hour
- **Enterprise Plus**: Unlimited

### **Data Limits**
- **File Upload**: 10MB per file, 50MB per incident
- **Bulk Operations**: 1,000 records per request
- **Export Limits**: 10,000 records per export

## 🔒 **Security Features**

### **Data Encryption**
- **In Transit**: TLS 1.3 encryption
- **At Rest**: AES-256 encryption
- **Database**: Encrypted sensitive fields

### **Audit Logging**
- All API calls logged with user, timestamp, IP
- Data change tracking with before/after values
- Compliance reporting for regulatory audits

### **Access Control**
- Project-based data isolation
- Role-based permissions
- IP whitelisting for enterprise clients
- Multi-factor authentication support

This commercial API provides enterprise-grade functionality with comprehensive incident management, advanced analytics, and industry-specific configurations suitable for sale to large organizations.
