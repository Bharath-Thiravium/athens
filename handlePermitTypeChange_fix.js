  const handlePermitTypeChange = async (value: number) => {
    const permitTypeId = Number(value);
    form.setFieldValue('permit_type', permitTypeId);
    setFormData(prev => ({ ...prev, permit_type: permitTypeId }));
    setAllFormValues(prev => ({ ...prev, permit_type: permitTypeId }));

    if (!permitTypeId) {
      setResolvedTemplate(null);
      return;
    }

    // Always apply defaults when permit type changes, regardless of edit mode
    await loadResolvedTemplate(permitTypeId, { applyDefaults: true, mode: isEditing ? 'merge' : 'create' });
    
    // Show template loaded indicator
    message.success('Permit type template loaded');
  };