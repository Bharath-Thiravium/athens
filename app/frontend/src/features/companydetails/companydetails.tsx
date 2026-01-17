import React, { useState, useEffect, useCallback } from 'react';
import { Form, Input, Button, Upload, Typography, InputNumber, Space, App, Spin, Row, Col, Tooltip, Breadcrumb } from 'antd';
import { UploadOutlined, EditOutlined, SaveOutlined, InfoCircleOutlined, HomeOutlined } from '@ant-design/icons';
import api from '../../common/utils/axiosetup';
import { useTheme } from '../../common/contexts/ThemeContext';
import type { UploadFile } from 'antd/es/upload/interface';


const { TextArea } = Input;
const { Title, Text } = Typography; // Using Text for labels is more flexible

const FORM_ID = "companyDetailsForm";

const CompanyDetailsForm: React.FC = () => {

  const { message } = App.useApp(); 
  // Rule 4: Get the current theme to apply the correct class to the top-level div
  const { effectiveTheme } = useTheme(); 
  const [form] = Form.useForm();
  const [logoPreview, setLogoPreview] = useState<string | null>(null);
  const [editMode, setEditMode] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isCreating, setIsCreating] = useState<boolean>(false);

  // All your logic functions (fetch, onFinish, etc.) are perfect and need no changes.
  // ... (fetchCompanyDetails, onFinish, and other handlers remain the same)
  const fetchCompanyDetails = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await api.get('/authentication/companydetail/');
      const data = response.data;
      
      setIsCreating(false);
      setEditMode(false);
      
      form.setFieldsValue({
        company_name: data.company_name || '',
        registered_office_address: data.registered_office_address || '',
        pan: data.pan || '',
        gst: data.gst || '',
        contact_phone: data.contact_phone || '',
        contact_email: data.contact_email || '',
        project_capacity_completed: data.project_capacity_completed ?? 0,
        project_capacity_ongoing: data.project_capacity_ongoing ?? 0,
        company_logo: data.company_logo ? [{ uid: '-1', name: 'logo.png', status: 'done', url: data.company_logo }] : [],
      });
      
      setLogoPreview(data.company_logo || null);
      
    } catch (error: any) {
      if (error.response && error.response.status === 404) {
        message.info('No company details found. Please fill in the form.');
        setIsCreating(true);
        setEditMode(true);
        form.resetFields();
        setLogoPreview(null);
      } else {
        message.error('Failed to fetch company details.');
        setEditMode(false);
      }
    } finally {
      setIsLoading(false);
    }
  }, [form]);

  useEffect(() => {
    fetchCompanyDetails();
  }, [fetchCompanyDetails]);

  const onFinish = async (values: any) => {
    setIsLoading(true);

    // Validate form data before submission
    const validationErrors = validateFormData(values);
    if (validationErrors.length > 0) {
      validationErrors.forEach(error => message.error(error));
      setIsLoading(false);
      return;
    }


    // Always use FormData for this endpoint as backend expects multipart/form-data
    const formData = new FormData();
    let hasNewLogo = false;

    // Add all form fields except logo
    Object.keys(values).forEach(key => {
      if (key !== 'company_logo') {
        formData.append(key, values[key] ?? '');
      }
    });

    const logoFileList = values.company_logo;

    // Handle logo upload if present
    if (logoFileList && logoFileList.length > 0) {
      const logoFile = logoFileList[0];

      if (logoFile.originFileObj) {
        const file = logoFile.originFileObj;

        console.log('Logo file details:', {
          name: file.name,
          type: file.type,
          size: file.size
        });

        // Validate file before upload
        const isValidType = file.type.startsWith('image/');
        const isValidSize = file.size / 1024 / 1024 < 5; // Less than 5MB

        if (!isValidType) {
          message.error('Please upload a valid image file (JPG, PNG, GIF, etc.)');
          setIsLoading(false);
          return;
        }

        if (!isValidSize) {
          message.error('Image must be smaller than 5MB');
          setIsLoading(false);
          return;
        }

        formData.append('company_logo', file, file.name);
        hasNewLogo = true;
      } else if (logoFile.url) {
        // This is an existing file, don't include it in the update
      }
    } else {
    }


    try {
      // Debug: Log FormData contents
      for (const [key, value] of formData.entries()) {
        if (value instanceof File) {
          console.log(`FormData file ${key}:`, {
            name: value.name,
            type: value.type,
            size: value.size
          });
        } else {
        }
      }

      // Configure axios to handle FormData properly
      // IMPORTANT: Remove the default 'application/json' Content-Type header
      const config = {
        headers: {
          'Content-Type': undefined, // This removes the default application/json header
        },
        transformRequest: [(data: any) => {
          // Return FormData as-is, don't let axios transform it
          return data;
        }],
      };

      const response = isCreating
        ? await api.post('/authentication/companydetail/', formData, config)
        : await api.patch('/authentication/companydetail/', formData, config);

      message.success(`Company details ${isCreating ? 'saved' : 'updated'} successfully!`);

      // Trigger unified company data update event for Dashboard
      if (response.data) {
        const companyDataEvent = new CustomEvent('company_data_updated', {
          detail: {
            logoUrl: response.data.company_logo,
            company_logo: response.data.company_logo,
            companyName: response.data.company_name,
            company_name: response.data.company_name,
            source: 'company_details_save'
          }
        });
        window.dispatchEvent(companyDataEvent);
        console.log('Company data updated:', {
          logo: response.data.company_logo,
          name: response.data.company_name
        });

        // Store PAN and GST in localStorage for EPC users to auto-fill
        if (response.data.pan) {
          localStorage.setItem('company_pan', response.data.pan);
        }

        if (response.data.gst) {
          localStorage.setItem('company_gst', response.data.gst);
        }
      }

      await fetchCompanyDetails();

    } catch (error: any) {

      // Handle specific error messages
      if (error.response?.data) {
        const errorData = error.response.data;
        if (errorData.company_logo && hasNewLogo) {
          // If logo upload failed, try submitting without logo
          message.warning('Logo upload failed. Saving other details without logo...');

          try {
            // Create FormData without logo for retry
            const formDataWithoutLogo = new FormData();
            Object.keys(values).forEach(key => {
              if (key !== 'company_logo') {
                formDataWithoutLogo.append(key, values[key] ?? '');
              }
            });

            const retryConfig = {
              headers: {
                'Content-Type': undefined, // Remove default application/json header
              },
              transformRequest: [(data: any) => data],
            };

            const response = isCreating
              ? await api.post('/authentication/companydetail/', formDataWithoutLogo, retryConfig)
              : await api.patch('/authentication/companydetail/', formDataWithoutLogo, retryConfig);

            message.success(`Company details ${isCreating ? 'saved' : 'updated'} successfully! Please try uploading the logo separately.`);
            await fetchCompanyDetails();
            return;
          } catch (retryError) {
          }

          message.error(`Logo upload error: ${errorData.company_logo[0]}. Please try a different image file.`);
        } else if (errorData.pan) {
          message.error(`PAN error: ${errorData.pan[0]}`);
        } else if (errorData.gst) {
          message.error(`GST error: ${errorData.gst[0]}`);
        } else {
          message.error('Failed to submit company details. Please check all fields.');
        }
      } else {
        message.error('Failed to submit company details.');
      }
    } finally {
      setIsLoading(false);
    }
  };
  


  const normFile = (e: any): UploadFile[] => {
    if (Array.isArray(e)) { return e; }
    return e?.fileList;
  };
  
  const handleLogoChange = (info: { file: UploadFile, fileList: UploadFile[] }) => {
    if (info.file.status === 'removed') {
        setLogoPreview(null);
    } else if (info.file.originFileObj) {
        // Validate file type and size
        const file = info.file.originFileObj;
        const isValidType = file.type.startsWith('image/');
        const isValidSize = file.size / 1024 / 1024 < 5; // Less than 5MB

        if (!isValidType) {
          message.error('Please upload a valid image file (JPG, PNG, GIF, etc.)');
          return;
        }

        if (!isValidSize) {
          message.error('Image must be smaller than 5MB');
          return;
        }

        const reader = new FileReader();
        reader.onloadend = () => { setLogoPreview(reader.result as string); };
        reader.readAsDataURL(file);
    }
  };

  // Helper function to format PAN input
  const handlePANChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
    form.setFieldsValue({ pan: value });
  };

  // Helper function to format GST input
  const handleGSTChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
    form.setFieldsValue({ gst: value });
  };

  // Helper function to validate form data
  const validateFormData = (values: any) => {
    const errors: string[] = [];

    // Validate PAN format
    if (values.pan && !/^[A-Z]{5}[0-9]{4}[A-Z]$/.test(values.pan)) {
      errors.push('PAN must be in format: ABCDE1234F');
    }

    // Validate GST format
    if (values.gst && !/^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$/.test(values.gst)) {
      errors.push('GST must be in format: 22ABCDE1234F1Z5');
    }

    // Validate phone number
    if (values.contact_phone && !/^\d{11}$/.test(values.contact_phone)) {
      errors.push('Phone number must be exactly 11 digits');
    }

    return errors;
  };


  // --- STYLING CHANGES ARE HERE ---

  // Instead of inline style objects, we will use a label component for consistency.
  const FormLabel = ({ children }: { children: React.ReactNode }) => (
    <Text className="!font-semibold !text-color-text-base">{children}</Text>
  );

  return (
    <div className="space-y-6" style={{ paddingTop: 80 }}>
      <Breadcrumb 
        style={{ marginBottom: 16 }}
        items={[
          {
            title: (
              <a href="/dashboard" style={{ color: 'inherit', textDecoration: 'none' }}>
                <HomeOutlined />
              </a>
            )
          },
          {
            title: 'Settings'
          },
          {
            title: 'Company Details'
          }
        ]}
      />
      <div className="flex flex-wrap justify-between items-center gap-4">
        <Title level={3} className="!mb-0 !text-color-text-base">Company Details</Title>
        {!editMode ? (
          <Button
            type="primary"
            icon={<EditOutlined />}
            onClick={() => setEditMode(true)}
            disabled={isLoading}
          >
            Edit Details
          </Button>
        ) : (
          <Space>
            <Button onClick={() => fetchCompanyDetails()}>
              Cancel
            </Button>
            <Button
              type="primary"
              icon={<SaveOutlined />}
              onClick={() => form.submit()}
            >
              Save Changes
            </Button>
          </Space>
        )}
      </div>
      <Card variant="borderless">
      <div className={`w-full min-h-full bg-color-bg-base`}>
        <Spin spinning={isLoading} tip="Loading company details...">
          <div className="bg-color-ui-base p-6 md:p-8">

          <Form id={FORM_ID} form={form} layout="vertical" onFinish={onFinish} disabled={!editMode} size="large">
            {/*
              Section container. Uses theme variables for background, border, and shadow.
            */}
            <div className="bg-color-bg-base p-6 rounded-lg border border-color-border mb-6 shadow-sm">
              <Title level={4} className="!text-color-text-base !font-semibold !mb-6">Basic Information</Title>
              <Row gutter={32}>
                <Col xs={24} md={12}>
                  <Form.Item label={<FormLabel>Company Name</FormLabel>} name="company_name" rules={[{ required: true }]}>
                    <Input placeholder="Enter company name" />
                  </Form.Item>
                </Col>
                <Col xs={24} md={12}>
                  <Form.Item
                    label={
                      <Space>
                        <FormLabel>PAN</FormLabel>
                        <Tooltip title="Permanent Account Number - 10 character alphanumeric code (5 letters + 4 digits + 1 letter)">
                          <InfoCircleOutlined className="text-gray-400" />
                        </Tooltip>
                      </Space>
                    }
                    name="pan"
                    rules={[
                      { required: true, message: 'PAN is required' },
                      {
                        pattern: /^[A-Z]{5}[0-9]{4}[A-Z]$/,
                        message: 'PAN must be in format: ABCDE1234F (5 letters, 4 digits, 1 letter)'
                      }
                    ]}
                    extra={
                      <div className="text-sm text-gray-500">
                        <div>Example: ABCDE1234F</div>
                        <div>Format: 5 letters + 4 digits + 1 letter</div>
                      </div>
                    }
                  >
                    <Input
                      placeholder="e.g., ABCDE1234F"
                      maxLength={10}
                      style={{ textTransform: 'uppercase' }}
                      onChange={handlePANChange}
                    />
                  </Form.Item>
                </Col>
              </Row>
              <Row gutter={32}>
                <Col xs={24} md={12}>
                  <Form.Item
                    label={
                      <Space>
                        <FormLabel>GST Number</FormLabel>
                        <Tooltip title="Goods and Services Tax Identification Number - 15 character alphanumeric code">
                          <InfoCircleOutlined className="text-gray-400" />
                        </Tooltip>
                      </Space>
                    }
                    name="gst"
                    rules={[
                      { required: true, message: 'GST number is required' },
                      {
                        pattern: /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$/,
                        message: 'GST must be in format: 22ABCDE1234F1Z5 (15 characters)'
                      }
                    ]}
                    extra={
                      <div className="text-sm text-gray-500">
                        <div>Example: 22ABCDE1234F1Z5</div>
                        <div>Format: 2 digits + 5 letters + 4 digits + 1 letter + 1 digit/letter + Z + 1 digit/letter</div>
                      </div>
                    }
                  >
                    <Input
                      placeholder="e.g., 22ABCDE1234F1Z5"
                      maxLength={15}
                      style={{ textTransform: 'uppercase' }}
                      onChange={handleGSTChange}
                    />
                  </Form.Item>
                </Col>
                <Col xs={24} md={12}>
                  <Form.Item
                    label={<FormLabel>Company Logo</FormLabel>}
                    name="company_logo"
                    valuePropName="fileList"
                    getValueFromEvent={normFile}
                    extra={<span className="text-sm text-gray-500">Upload JPG, PNG, or GIF. Max size: 5MB. Logo will appear in the dashboard sidebar.</span>}
                  >
                    <Upload
                      listType="picture-card"
                      maxCount={1}
                      beforeUpload={(file) => {
                        // Validate file type
                        const isValidType = file.type.startsWith('image/');
                        if (!isValidType) {
                          message.error('Please upload a valid image file (JPG, PNG, GIF, etc.)');
                          return false;
                        }

                        // Validate file size
                        const isValidSize = file.size / 1024 / 1024 < 5; // Less than 5MB
                        if (!isValidSize) {
                          message.error('Image must be smaller than 5MB');
                          return false;
                        }

                        return false; // Prevent auto upload
                      }}
                      onChange={handleLogoChange}
                      accept="image/*"
                    >
                      <div>
                        <UploadOutlined />
                        <div style={{ marginTop: 8 }}>Upload Logo</div>
                      </div>
                    </Upload>
                  </Form.Item>
                  {logoPreview && <img src={logoPreview} alt="Logo Preview" className="max-w-[200px] max-h-[120px] rounded border border-color-border p-1 ml-4" />}
                </Col>
              </Row>
            </div>

            <div className="bg-color-bg-base p-6 rounded-lg border border-color-border mb-6 shadow-sm">
              <Title level={4} className="!text-color-text-base !font-semibold !mb-6">Address & Contact Information</Title>
              <Form.Item label={<FormLabel>Registered Office Address</FormLabel>} name="registered_office_address" rules={[{ required: true }]}>
                <TextArea rows={4} placeholder="Enter registered office address" />
              </Form.Item>
              <Row gutter={32}>
                <Col xs={24} md={12}>
                  <Form.Item label={<FormLabel>Contact Phone</FormLabel>} name="contact_phone" rules={[{ required: true, len: 11, message: 'Phone number must be exactly 11 digits' }]}>
                    <Input
                      maxLength={11}
                      className="w-full"
                      placeholder="Enter 11-digit phone number (e.g., 91 44-69252555)"
                      size="large"
                      onKeyPress={(e) => {
                        if (!/[0-9]/.test(e.key)) {
                          e.preventDefault();
                        }
                      }}
                      onChange={(e) => {
                        const value = e.target.value.replace(/\D/g, '');
                        form.setFieldsValue({ contact_phone: value });
                      }}
                    />
                  </Form.Item>
                </Col>
                <Col xs={24} md={12}>
                  <Form.Item label={<FormLabel>Contact Email</FormLabel>} name="contact_email" rules={[{ required: true, type: 'email' }]}>
                    <Input placeholder="Email" />
                  </Form.Item>
                </Col>
              </Row>
            </div>

            <div className="bg-color-bg-base p-6 rounded-lg border border-color-border mb-6 shadow-sm">
              <Title level={4} className="!text-color-text-base !font-semibold !mb-6">Project Capacity Information</Title>
              <Row gutter={32}>
                <Col xs={24} md={12}>
                  <Form.Item label={<FormLabel>Completed Projects (MW)</FormLabel>} name="project_capacity_completed" rules={[{ required: true }]}>
                    <InputNumber
                      min={0}
                      className="w-full"
                      onKeyDown={(e) => {
                        if (
                          ['Backspace', 'Delete', 'Tab', 'Escape', 'Enter', 'ArrowLeft', 'ArrowRight', 'Home', 'End'].indexOf(e.key) !== -1
                        ) {
                          return;
                        }
                        if (!/^\d$/.test(e.key)) {
                          e.preventDefault();
                        }
                      }}
                    />
                  </Form.Item>
                </Col>
                <Col xs={24} md={12}>
                  <Form.Item label={<FormLabel>Ongoing Projects (MW)</FormLabel>} name="project_capacity_ongoing" rules={[{ required: true }]}>
                    <InputNumber
                      min={0}
                      className="w-full"
                      onKeyDown={(e) => {
                        if (
                          ['Backspace', 'Delete', 'Tab', 'Escape', 'Enter', 'ArrowLeft', 'ArrowRight', 'Home', 'End'].indexOf(e.key) !== -1
                        ) {
                          return;
                        }
                        if (!/^\d$/.test(e.key)) {
                          e.preventDefault();
                        }
                      }}
                    />
                  </Form.Item>
                </Col>
              </Row>
            </div>
          </Form>
        </div>
      </Spin>
    </div>
    </Card>
    </div>
  );
};

export default CompanyDetailsForm;