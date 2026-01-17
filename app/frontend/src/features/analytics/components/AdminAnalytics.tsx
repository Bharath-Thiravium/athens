import React, { useState, useEffect } from 'react';
import { Card, Typography, Row, Col, Table, Tag } from 'antd';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from 'recharts';
import api from '@common/utils/axiosetup';
import useAuthStore from '@common/store/authStore';
import PageLayout from '@common/components/PageLayout';

const { Title } = Typography;

const AdminAnalytics: React.FC = () => {
  const [consolidatedData, setConsolidatedData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const { usertype } = useAuthStore();

  useEffect(() => {
    if (usertype === 'masteradmin') {
      fetchConsolidatedData();
    }
  }, [usertype]);

  const fetchConsolidatedData = async () => {
    setLoading(true);
    try {
      const response = await api.get('/authentication/admin/dashboard/consolidated/');
      setConsolidatedData(response.data);
    } catch (error) {
      console.error('Failed to fetch analytics data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (usertype !== 'masteradmin') {
    return (
      <PageLayout title="Analytics" subtitle="System analytics and insights">
        <Card>
          <div className="text-center py-8">
            <Title level={4}>Access Restricted</Title>
            <p>Only Master Admin can access system analytics.</p>
          </div>
        </Card>
      </PageLayout>
    );
  }

  return (
    <PageLayout title="Analytics" subtitle="Detailed system analytics and insights">
      {consolidatedData && (
        <div className="space-y-6">
          {/* Detailed Charts and Analysis */}
          <Row gutter={[16, 16]} className="mb-6">
            <Col xs={24} lg={12}>
              <Card>
                <Title level={5} className="!mb-4">Admin Type Distribution</Title>
                <div style={{ height: 300 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={consolidatedData.charts?.admin_type_distribution || []}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={120}
                        dataKey="value"
                        paddingAngle={5}
                      >
                        {(consolidatedData.charts?.admin_type_distribution || []).map((entry: any, index: number) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </Card>
            </Col>
            
            <Col xs={24} lg={12}>
              <Card>
                <Title level={5} className="!mb-4">User Type Distribution</Title>
                <div style={{ height: 300 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={consolidatedData.charts?.user_type_distribution || []}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={120}
                        dataKey="value"
                        paddingAngle={5}
                      >
                        {(consolidatedData.charts?.user_type_distribution || []).map((entry: any, index: number) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </Card>
            </Col>
          </Row>
          
          {/* Project Performance Analysis */}
          <Row gutter={[16, 16]}>
            <Col xs={24}>
              <Card>
                <Title level={5} className="!mb-4">Project Performance Analysis</Title>
                <div style={{ height: 400 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={consolidatedData.charts?.project_distribution?.slice(0, 8) || []}>
                      <XAxis dataKey="project_name" angle={-45} textAnchor="end" height={100} />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="total_admins" fill="#3b82f6" name="Admins" />
                      <Bar dataKey="total_users" fill="#22c55e" name="Users" />
                      <Bar dataKey="pending_approvals" fill="#f59e0b" name="Pending" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </Card>
            </Col>
          </Row>
          
          {/* Detailed Statistics Table */}
          <Row gutter={[16, 16]} className="mt-6">
            <Col xs={24}>
              <Card>
                <Title level={5} className="!mb-4">Project Statistics</Title>
                <Table
                  dataSource={consolidatedData.project_data?.filter((p: any) => p.total_admins > 0 || p.total_users > 0) || []}
                  rowKey="project_id"
                  pagination={{ pageSize: 10 }}
                  size="small"
                  scroll={{ x: 800 }}
                  columns={[
                    {
                      title: 'Project Name',
                      dataIndex: 'project_name',
                      key: 'project_name',
                      width: 200,
                      fixed: 'left'
                    },
                    {
                      title: 'Admins',
                      dataIndex: 'total_admins',
                      key: 'total_admins',
                      align: 'center'
                    },
                    {
                      title: 'Users',
                      dataIndex: 'total_users',
                      key: 'total_users',
                      align: 'center'
                    },
                    {
                      title: 'Pending',
                      dataIndex: 'pending_approvals',
                      key: 'pending_approvals',
                      align: 'center',
                      render: (value: number) => (
                        <Tag color={value > 0 ? 'orange' : 'green'}>{value}</Tag>
                      )
                    },
                    {
                      title: 'Client',
                      children: [
                        {
                          title: 'Admins',
                          dataIndex: 'client_admins',
                          key: 'client_admins',
                          align: 'center',
                          width: 60
                        },
                        {
                          title: 'Users',
                          dataIndex: 'client_users',
                          key: 'client_users',
                          align: 'center',
                          width: 60
                        }
                      ]
                    },
                    {
                      title: 'EPC',
                      children: [
                        {
                          title: 'Admins',
                          dataIndex: 'epc_admins',
                          key: 'epc_admins',
                          align: 'center',
                          width: 60
                        },
                        {
                          title: 'Users',
                          dataIndex: 'epc_users',
                          key: 'epc_users',
                          align: 'center',
                          width: 60
                        }
                      ]
                    },
                    {
                      title: 'Contractor',
                      children: [
                        {
                          title: 'Admins',
                          dataIndex: 'contractor_admins',
                          key: 'contractor_admins',
                          align: 'center',
                          width: 60
                        },
                        {
                          title: 'Users',
                          dataIndex: 'contractor_users',
                          key: 'contractor_users',
                          align: 'center',
                          width: 60
                        }
                      ]
                    }
                  ]}
                />
              </Card>
            </Col>
          </Row>
        </div>
      )}
    </PageLayout>
  );
};

export default AdminAnalytics;
