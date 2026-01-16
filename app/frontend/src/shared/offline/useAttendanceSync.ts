import { useCallback, useEffect, useRef, useState } from 'react';
import { message } from 'antd';
import api from '@common/utils/axiosetup';

import {
  ATTENDANCE_QUEUE_UPDATED_EVENT,
  getQueueSize,
  listFailedEvents,
  listPendingEvents,
  markEventFailed,
  markEventSynced,
  removeSyncedEvents,
} from './attendanceQueue';

export interface AttendanceSyncStatus {
  isOnline: boolean;
  isSyncing: boolean;
  pendingCount: number;
  failedCount: number;
  lastSync: string | null;
}

const BATCH_SIZE = 50;

export const useAttendanceSync = () => {
  const [syncStatus, setSyncStatus] = useState<AttendanceSyncStatus>({
    isOnline: navigator.onLine,
    isSyncing: false,
    pendingCount: 0,
    failedCount: 0,
    lastSync: null,
  });

  const syncingRef = useRef(false);

  const refreshStatus = useCallback(async () => {
    const [pendingCount, failedEvents] = await Promise.all([
      getQueueSize(),
      listFailedEvents(),
    ]);

    setSyncStatus(prev => ({
      ...prev,
      pendingCount,
      failedCount: failedEvents.length,
    }));
  }, []);

  const syncNow = useCallback(async () => {
    if (!navigator.onLine || syncingRef.current) {
      return;
    }

    syncingRef.current = true;
    setSyncStatus(prev => ({ ...prev, isSyncing: true }));

    try {
      const pendingItems = await listPendingEvents(BATCH_SIZE);
      if (pendingItems.length === 0) {
        return;
      }

      const events = pendingItems.map(item => item.event);
      const response = await api.post('/api/attendance/events/bulk/', events);
      const { created = [], duplicates = [], rejected = [] } = response.data || {};

      const syncedIds = new Set<string>([...created, ...duplicates]);

      await Promise.all(
        pendingItems.map(item => {
          if (syncedIds.has(item.client_event_id)) {
            return markEventSynced(item.client_event_id);
          }
          return Promise.resolve();
        })
      );

      if (Array.isArray(rejected)) {
        await Promise.all(
          rejected.map((entry: { client_event_id: string; reason?: string }) =>
            markEventFailed(entry.client_event_id, entry.reason)
          )
        );
      }

      await removeSyncedEvents();
      await refreshStatus();

      setSyncStatus(prev => ({
        ...prev,
        lastSync: new Date().toISOString(),
      }));

      if (created.length > 0) {
        message.success(`Synced ${created.length} attendance events`);
      }
      if (rejected.length > 0) {
        message.warning(`${rejected.length} attendance events rejected`);
      }
    } catch (error: any) {
      message.error(`Attendance sync failed: ${error.response?.data?.error || error.message}`);
    } finally {
      syncingRef.current = false;
      setSyncStatus(prev => ({ ...prev, isSyncing: false }));
    }
  }, [refreshStatus]);

  useEffect(() => {
    refreshStatus();

    const handleOnline = () => {
      setSyncStatus(prev => ({ ...prev, isOnline: true }));
      syncNow();
    };

    const handleOffline = () => {
      setSyncStatus(prev => ({ ...prev, isOnline: false }));
    };

    const handleQueueUpdate = () => {
      refreshStatus();
      if (navigator.onLine) {
        syncNow();
      }
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    window.addEventListener(ATTENDANCE_QUEUE_UPDATED_EVENT, handleQueueUpdate);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      window.removeEventListener(ATTENDANCE_QUEUE_UPDATED_EVENT, handleQueueUpdate);
    };
  }, [refreshStatus, syncNow]);

  useEffect(() => {
    if (!syncStatus.isOnline) return;

    const interval = setInterval(() => {
      if (syncStatus.pendingCount > 0) {
        syncNow();
      }
    }, 5 * 60 * 1000);

    return () => clearInterval(interval);
  }, [syncStatus.isOnline, syncStatus.pendingCount, syncNow]);

  return {
    syncStatus,
    syncNow,
  };
};
