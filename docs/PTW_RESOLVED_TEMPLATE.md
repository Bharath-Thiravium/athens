# PTW Resolved Template Schema

## Source: app/backend/ptw/template_utils.py

## API Endpoint
`GET /api/v1/ptw/permit-types/{id}/resolved-template/?project={project_id}`

## Response Structure

```json
{
  "resolved_template": {
    "version": 1,
    "sections": [
      {
        "id": "section_id",
        "title": "Section Title",
        "category": "required|recommended|optional",
        "fields": [
          {
            "key": "field_key",
            "label": "Field Label",
            "type": "boolean|text|textarea|select|multiselect|date|datetime|number|file",
            "default": "default_value",
            "required": true|false,
            "help": "Help text",
            "options": []
          }
        ]
      }
    ],
    "references": [
      {
        "type": "SOP|HIRA|JSA",
        "code": "DOC-CODE-001",
        "title": "Document Title",
        "url": "https://..."
      }
    ]
  },
  "resolved_prefill": {
    "ppe_requirements": ["Hard Hat", "Safety Boots"],
    "safety_checklist": ["item1", "item2"],
    "control_measures": ["measure1"],
    "risk_factors": ["factor1"],
    "emergency_procedures": ["procedure1"]
  },
  "resolved_flags": {
    "requires_gas_testing": true|false,
    "requires_fire_watch": true|false,
    "requires_isolation": true|false,
    "requires_structured_isolation": true|false,
    "requires_deisolation_on_closeout": true|false,
    "requires_medical_surveillance": true|false,
    "requires_training_verification": true|false,
    "validity_hours": 24,
    "escalation_time_hours": 4,
    "min_personnel_required": 2,
    "requires_approval_levels": 2
  }
}
```

## Default Template Sections

### 1. General Requirements (Always Present)
```json
{
  "id": "general_requirements",
  "title": "General Requirements",
  "category": "required",
  "fields": [
    {
      "key": "work_scope_defined",
      "label": "Work scope defined",
      "type": "boolean",
      "default": true,
      "required": true,
      "help": "Confirm the scope is clear and agreed."
    },
    {
      "key": "work_area_checked",
      "label": "Work area checked",
      "type": "boolean",
      "default": true,
      "required": true,
      "help": "Inspect the work area before starting."
    },
    {
      "key": "tools_inspected",
      "label": "Tools and equipment inspected",
      "type": "boolean",
      "default": true,
      "required": true,
      "help": "Verify tools are safe and fit for use."
    }
  ]
}
```

### 2. Hazard Controls (Always Present)
```json
{
  "id": "hazard_controls",
  "title": "Hazard Controls",
  "category": "recommended",
  "fields": [
    {
      "key": "hazards_reviewed",
      "label": "Hazards reviewed",
      "type": "boolean",
      "default": true,
      "required": false
    },
    {
      "key": "controls_applied",
      "label": "Controls applied",
      "type": "boolean",
      "default": true,
      "required": false
    }
  ]
}
```

### 3. Authorization (Always Present)
```json
{
  "id": "authorization",
  "title": "Authorization",
  "category": "required",
  "fields": [
    {
      "key": "permit_displayed",
      "label": "Permit displayed at worksite",
      "type": "boolean",
      "default": true,
      "required": true
    },
    {
      "key": "authorization_confirmed",
      "label": "Authorization confirmed",
      "type": "boolean",
      "default": true,
      "required": true
    }
  ]
}
```

### 4. Emergency Preparedness (Always Present)
```json
{
  "id": "emergency_preparedness",
  "title": "Emergency Preparedness",
  "category": "required",
  "fields": [
    {
      "key": "emergency_contacts_available",
      "label": "Emergency contacts available",
      "type": "boolean",
      "default": true,
      "required": true
    },
    {
      "key": "evacuation_route_known",
      "label": "Evacuation route known",
      "type": "boolean",
      "default": true,
      "required": true
    }
  ]
}
```

## Category-Specific Sections

### Hot Work (category='hot_work')
```json
{
  "id": "hot_work_controls",
  "title": "Hot Work Controls",
  "category": "required",
  "fields": [
    {
      "key": "hot_work_area_cleared",
      "label": "Hot work area cleared of combustibles",
      "type": "boolean",
      "required": true
    },
    {
      "key": "fire_watch_assigned",
      "label": "Fire watch assigned",
      "type": "boolean",
      "required": true
    },
    {
      "key": "spark_containment_in_place",
      "label": "Spark containment in place",
      "type": "boolean",
      "required": true
    }
  ]
}
```

### Confined Space (category='confined_space')
```json
{
  "id": "confined_space_entry",
  "title": "Confined Space Entry",
  "category": "required",
  "fields": [
    {
      "key": "entry_supervisor_assigned",
      "label": "Entry supervisor assigned",
      "type": "boolean",
      "required": true
    },
    {
      "key": "attendant_assigned",
      "label": "Attendant assigned",
      "type": "boolean",
      "required": true
    },
    {
      "key": "rescue_plan_confirmed",
      "label": "Rescue plan confirmed",
      "type": "boolean",
      "required": true
    }
  ]
}
```

### Electrical (category='electrical')
```json
{
  "id": "electrical_controls",
  "title": "Electrical Controls",
  "category": "required",
  "fields": [
    {
      "key": "lockout_tagout_applied",
      "label": "Lockout/tagout applied",
      "type": "boolean",
      "required": true
    },
    {
      "key": "voltage_verified",
      "label": "Zero energy verified",
      "type": "boolean",
      "required": true
    },
    {
      "key": "insulated_tools_used",
      "label": "Insulated tools used",
      "type": "boolean",
      "required": false
    }
  ]
}
```

### Work at Height (category='height')
```json
{
  "id": "work_at_height",
  "title": "Work at Height",
  "category": "required",
  "fields": [
    {
      "key": "fall_protection_inspected",
      "label": "Fall protection inspected",
      "type": "boolean",
      "required": true
    },
    {
      "key": "drop_zone_established",
      "label": "Drop zone established",
      "type": "boolean",
      "required": true
    }
  ]
}
```

### Excavation (category='excavation')
```json
{
  "id": "excavation_controls",
  "title": "Excavation Controls",
  "category": "required",
  "fields": [
    {
      "key": "utilities_located",
      "label": "Underground utilities located",
      "type": "boolean",
      "required": true
    },
    {
      "key": "shoring_or_sloping_in_place",
      "label": "Shoring or sloping in place",
      "type": "boolean",
      "required": true
    }
  ]
}
```

### Crane/Lifting (category='crane_lifting')
```json
{
  "id": "lifting_controls",
  "title": "Lifting Operations",
  "category": "required",
  "fields": [
    {
      "key": "lift_plan_reviewed",
      "label": "Lift plan reviewed",
      "type": "boolean",
      "required": true
    },
    {
      "key": "rigging_inspected",
      "label": "Rigging inspected",
      "type": "boolean",
      "required": true
    },
    {
      "key": "exclusion_zone_set",
      "label": "Exclusion zone set",
      "type": "boolean",
      "required": true
    }
  ]
}
```

## Conditional Sections

### Gas Testing (if requires_gas_testing=true)
```json
{
  "id": "gas_testing",
  "title": "Gas Testing",
  "category": "required",
  "fields": [
    {
      "key": "gas_testing_required",
      "label": "Gas testing required",
      "type": "boolean",
      "required": true
    },
    {
      "key": "continuous_monitoring",
      "label": "Continuous monitoring in place",
      "type": "boolean",
      "required": false
    }
  ]
}
```

### Isolation Controls (if requires_isolation=true)
```json
{
  "id": "isolation_controls",
  "title": "Isolation & Energy Control",
  "category": "required",
  "fields": [
    {
      "key": "isolation_required",
      "label": "Isolation required",
      "type": "boolean",
      "required": true
    },
    {
      "key": "isolation_verified",
      "label": "Isolation verified",
      "type": "boolean",
      "required": true
    }
  ]
}
```

### Fire Watch (if requires_fire_watch=true)
```json
{
  "id": "fire_watch",
  "title": "Fire Watch",
  "category": "required",
  "fields": [
    {
      "key": "fire_watch_required",
      "label": "Fire watch required",
      "type": "boolean",
      "required": true
    }
  ]
}
```

### Competency Requirements (if requires_training or requires_medical=true)
```json
{
  "id": "competency_requirements",
  "title": "Competency Requirements",
  "category": "required",
  "fields": [
    {
      "key": "training_verified",
      "label": "Training verified",
      "type": "boolean",
      "required": true
    },
    {
      "key": "medical_surveillance_confirmed",
      "label": "Medical surveillance confirmed",
      "type": "boolean",
      "required": true
    }
  ]
}
```

## Template Merging Logic

1. **Base Template**: From `permit_type.form_template` or generated via `build_minimal_template()`
2. **Project Override**: If `permit_type.project_overrides_enabled=true`, merge with `PermitTypeTemplateOverride.override_template`
3. **Prefill Merge**: Merge `permit_type` fields with template prefill and project override prefill
4. **Flags**: Always include `resolved_flags` from `permit_type` boolean fields

## Field Types

- **boolean**: Checkbox (true/false)
- **text**: Single-line text input
- **textarea**: Multi-line text input
- **select**: Dropdown (single selection)
- **multiselect**: Multi-select dropdown
- **date**: Date picker
- **datetime**: Date and time picker
- **number**: Numeric input
- **file**: File upload
- **signature**: Digital signature capture
