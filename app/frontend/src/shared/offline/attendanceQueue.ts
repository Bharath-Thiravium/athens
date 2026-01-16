export type AttendanceModule = 'REGULAR' | 'TBT' | 'TRAINING' | 'MOM';
export type AttendanceEventType = 'CHECK_IN' | 'CHECK_OUT';
export type AttendanceMethod = 'FACE' | 'QR' | 'PIN' | 'SELF_CONFIRM' | 'HOST' | 'MANUAL';

export interface AttendanceEventPayload {
  client_event_id: string;
  user_id?: number;
  module: AttendanceModule;
  module_ref_id?: string | number | null;
  event_type: AttendanceEventType;
  occurred_at: string;
  device_id?: string | null;
  offline?: boolean;
  method: AttendanceMethod;
  location?: any;
  payload?: any;
}

export type AttendanceQueueStatus = 'pending' | 'synced' | 'failed';

export interface AttendanceQueueItem {
  client_event_id: string;
  event: AttendanceEventPayload;
  status: AttendanceQueueStatus;
  attempts: number;
  created_at: string;
  last_attempt_at?: string;
  error?: string;
}

const DB_NAME = 'athens_offline';
const DB_VERSION = 1;
const STORE_NAME = 'attendance_events';
const STATUS_INDEX = 'status';
const FALLBACK_KEY = 'attendance_queue_fallback';
const DEVICE_ID_KEY = 'attendance_device_id';

export const ATTENDANCE_QUEUE_UPDATED_EVENT = 'attendance-queue-updated';

const supportsIndexedDB = () => typeof indexedDB !== 'undefined';

const openDb = (): Promise<IDBDatabase> => {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        const store = db.createObjectStore(STORE_NAME, { keyPath: 'client_event_id' });
        store.createIndex(STATUS_INDEX, 'status', { unique: false });
      }
    };

    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
};

const requestToPromise = <T>(request: IDBRequest<T>) => {
  return new Promise<T>((resolve, reject) => {
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
};

const waitForTransaction = (tx: IDBTransaction) => {
  return new Promise<void>((resolve, reject) => {
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
    tx.onabort = () => reject(tx.error);
  });
};

const readFallbackQueue = (): AttendanceQueueItem[] => {
  const stored = localStorage.getItem(FALLBACK_KEY);
  if (!stored) return [];
  try {
    return JSON.parse(stored) as AttendanceQueueItem[];
  } catch {
    return [];
  }
};

const writeFallbackQueue = (items: AttendanceQueueItem[]) => {
  localStorage.setItem(FALLBACK_KEY, JSON.stringify(items));
};

export const notifyAttendanceQueueUpdated = () => {
  window.dispatchEvent(new Event(ATTENDANCE_QUEUE_UPDATED_EVENT));
};

export const getAttendanceDeviceId = () => {
  let deviceId = localStorage.getItem(DEVICE_ID_KEY);
  if (!deviceId) {
    deviceId = typeof crypto !== 'undefined' && 'randomUUID' in crypto
      ? crypto.randomUUID()
      : `device_${Date.now()}_${Math.random().toString(36).slice(2)}`;
    localStorage.setItem(DEVICE_ID_KEY, deviceId);
  }
  return deviceId;
};

export const generateClientEventId = () => {
  return typeof crypto !== 'undefined' && 'randomUUID' in crypto
    ? crypto.randomUUID()
    : `evt_${Date.now()}_${Math.random().toString(36).slice(2)}`;
};

export const enqueueAttendanceEvent = async (event: AttendanceEventPayload) => {
  const item: AttendanceQueueItem = {
    client_event_id: event.client_event_id,
    event,
    status: 'pending',
    attempts: 0,
    created_at: new Date().toISOString(),
  };

  if (!supportsIndexedDB()) {
    const queue = readFallbackQueue();
    const updated = queue.filter(q => q.client_event_id !== item.client_event_id);
    updated.push(item);
    writeFallbackQueue(updated);
    notifyAttendanceQueueUpdated();
    return;
  }

  try {
    const db = await openDb();
    const tx = db.transaction(STORE_NAME, 'readwrite');
    const store = tx.objectStore(STORE_NAME);
    await requestToPromise(store.put(item));
    await waitForTransaction(tx);
  } catch {
    const queue = readFallbackQueue();
    const updated = queue.filter(q => q.client_event_id !== item.client_event_id);
    updated.push(item);
    writeFallbackQueue(updated);
  }

  notifyAttendanceQueueUpdated();
};

const listByStatusFallback = (status: AttendanceQueueStatus) => {
  return readFallbackQueue().filter(item => item.status === status);
};

const listByStatusIdb = async (status: AttendanceQueueStatus) => {
  const db = await openDb();
  const tx = db.transaction(STORE_NAME, 'readonly');
  const store = tx.objectStore(STORE_NAME);
  const index = store.index(STATUS_INDEX);
  const results = await requestToPromise(index.getAll(status));
  await waitForTransaction(tx);
  return results as AttendanceQueueItem[];
};

export const listPendingEvents = async (limit?: number) => {
  const items = supportsIndexedDB() ? await listByStatusIdb('pending') : listByStatusFallback('pending');
  if (!limit) return items;
  return items.slice(0, limit);
};

export const listFailedEvents = async () => {
  return supportsIndexedDB() ? await listByStatusIdb('failed') : listByStatusFallback('failed');
};

export const markEventSynced = async (client_event_id: string) => {
  return updateQueueItem(client_event_id, { status: 'synced', last_attempt_at: new Date().toISOString() });
};

export const markEventFailed = async (client_event_id: string, error?: string) => {
  return updateQueueItem(client_event_id, {
    status: 'failed',
    last_attempt_at: new Date().toISOString(),
    error,
  });
};

const updateQueueItem = async (client_event_id: string, updates: Partial<AttendanceQueueItem>) => {
  if (!supportsIndexedDB()) {
    const queue = readFallbackQueue();
    const updated = queue.map(item =>
      item.client_event_id === client_event_id ? { ...item, ...updates } : item
    );
    writeFallbackQueue(updated);
    notifyAttendanceQueueUpdated();
    return;
  }

  try {
    const db = await openDb();
    const tx = db.transaction(STORE_NAME, 'readwrite');
    const store = tx.objectStore(STORE_NAME);
    const existing = await requestToPromise(store.get(client_event_id));
    if (existing) {
      await requestToPromise(store.put({ ...existing, ...updates }));
    }
    await waitForTransaction(tx);
  } catch {
    const queue = readFallbackQueue();
    const updated = queue.map(item =>
      item.client_event_id === client_event_id ? { ...item, ...updates } : item
    );
    writeFallbackQueue(updated);
  }

  notifyAttendanceQueueUpdated();
};

export const removeSyncedEvents = async () => {
  if (!supportsIndexedDB()) {
    const queue = readFallbackQueue();
    writeFallbackQueue(queue.filter(item => item.status !== 'synced'));
    notifyAttendanceQueueUpdated();
    return;
  }

  try {
    const db = await openDb();
    const tx = db.transaction(STORE_NAME, 'readwrite');
    const store = tx.objectStore(STORE_NAME);
    const index = store.index(STATUS_INDEX);
    const synced = await requestToPromise(index.getAll('synced')) as AttendanceQueueItem[];
    synced.forEach(item => {
      store.delete(item.client_event_id);
    });
    await waitForTransaction(tx);
  } catch {
    const queue = readFallbackQueue();
    writeFallbackQueue(queue.filter(item => item.status !== 'synced'));
  }

  notifyAttendanceQueueUpdated();
};

export const getQueueSize = async () => {
  const pending = supportsIndexedDB() ? await listByStatusIdb('pending') : listByStatusFallback('pending');
  return pending.length;
};
