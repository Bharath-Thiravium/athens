import React from 'react';
import { Button, Space, Tag, Tooltip } from 'antd';
import { CloudOutlined, CloudSyncOutlined, SyncOutlined } from '@ant-design/icons';

import { useAttendanceSync } from './useAttendanceSync';

const AttendanceSyncIndicator: React.FC = () => {
  const { syncStatus, syncNow } = useAttendanceSync();

  if (syncStatus.pendingCount === 0 && syncStatus.isOnline) {
    return null;
  }

  return (
    <Space size="small">
      {!syncStatus.isOnline && (
        <Tag color="orange">Offline mode</Tag>
      )}
      {syncStatus.pendingCount > 0 && (
        <Tag color="blue">Pending sync: {syncStatus.pendingCount}</Tag>
      )}
      {syncStatus.failedCount > 0 && (
        <Tag color="red">Sync issues: {syncStatus.failedCount}</Tag>
      )}
      <Tooltip title={syncStatus.isOnline ? 'Sync attendance now' : 'Offline'}>
        <Button
          type="text"
          size="small"
          icon={syncStatus.isSyncing ? <SyncOutlined spin /> : <CloudSyncOutlined />}
          disabled={!syncStatus.isOnline || syncStatus.isSyncing || syncStatus.pendingCount === 0}
          onClick={() => syncNow()}
        />
      </Tooltip>
      {syncStatus.isOnline && syncStatus.pendingCount > 0 && (
        <CloudOutlined style={{ color: '#1677ff' }} />
      )}
    </Space>
  );
};

export default AttendanceSyncIndicator;
