/**
 * Performance Optimization Utilities
 * Provides utilities for optimizing React component performance
 */

import { useCallback, useMemo, useRef, useEffect } from 'react';

// Debounce hook for performance optimization
export const useDebounce = <T>(value: T, delay: number): T => {
  const [debouncedValue, setDebouncedValue] = React.useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

// Throttle hook for performance optimization
export const useThrottle = <T>(value: T, limit: number): T => {
  const [throttledValue, setThrottledValue] = React.useState<T>(value);
  const lastRan = useRef<number>(Date.now());

  useEffect(() => {
    const handler = setTimeout(() => {
      if (Date.now() - lastRan.current >= limit) {
        setThrottledValue(value);
        lastRan.current = Date.now();
      }
    }, limit - (Date.now() - lastRan.current));

    return () => {
      clearTimeout(handler);
    };
  }, [value, limit]);

  return throttledValue;
};

// Memoized participant statistics calculator
export const useParticipantStats = (participants: any[]) => {
  return useMemo(() => {
    const stats = participants.reduce((acc, participant) => {
      switch (participant.status) {
        case 'accepted':
          acc.acceptedCount++;
          break;
        case 'rejected':
          acc.rejectedCount++;
          break;
        case 'pending':
        case 'noresponse':
          acc.noResponseCount++;
          break;
      }
      return acc;
    }, {
      acceptedCount: 0,
      rejectedCount: 0,
      noResponseCount: 0,
      totalParticipants: participants.length
    });

    const responseRate = stats.totalParticipants > 0 
      ? Math.round(((stats.acceptedCount + stats.rejectedCount) / stats.totalParticipants) * 100)
      : 0;
    
    const acceptanceRate = stats.totalParticipants > 0 
      ? Math.round((stats.acceptedCount / stats.totalParticipants) * 100)
      : 0;

    return {
      ...stats,
      responseRate,
      acceptanceRate
    };
  }, [participants]);
};

// Optimized API call hook with caching
export const useOptimizedApiCall = <T>(
  apiCall: () => Promise<T>,
  dependencies: any[],
  cacheKey?: string
) => {
  const [data, setData] = React.useState<T | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<Error | null>(null);
  const cache = useRef<Map<string, { data: T; timestamp: number }>>(new Map());
  const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

  const memoizedApiCall = useCallback(async () => {
    if (cacheKey) {
      const cached = cache.current.get(cacheKey);
      if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
        setData(cached.data);
        return;
      }
    }

    setLoading(true);
    setError(null);

    try {
      const result = await apiCall();
      setData(result);
      
      if (cacheKey) {
        cache.current.set(cacheKey, { data: result, timestamp: Date.now() });
      }
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, dependencies);

  useEffect(() => {
    memoizedApiCall();
  }, [memoizedApiCall]);

  return { data, loading, error, refetch: memoizedApiCall };
};

// Batch API calls to reduce network requests
export const batchApiCalls = async <T>(
  apiCalls: (() => Promise<T>)[],
  batchSize: number = 5
): Promise<T[]> => {
  const results: T[] = [];
  
  for (let i = 0; i < apiCalls.length; i += batchSize) {
    const batch = apiCalls.slice(i, i + batchSize);
    const batchResults = await Promise.all(batch.map(call => call()));
    results.push(...batchResults);
  }
  
  return results;
};

// Virtual scrolling for large lists
export const useVirtualScrolling = (
  items: any[],
  itemHeight: number,
  containerHeight: number
) => {
  const [scrollTop, setScrollTop] = React.useState(0);
  
  const visibleItems = useMemo(() => {
    const startIndex = Math.floor(scrollTop / itemHeight);
    const endIndex = Math.min(
      startIndex + Math.ceil(containerHeight / itemHeight) + 1,
      items.length
    );
    
    return {
      startIndex,
      endIndex,
      visibleItems: items.slice(startIndex, endIndex),
      totalHeight: items.length * itemHeight,
      offsetY: startIndex * itemHeight
    };
  }, [items, itemHeight, containerHeight, scrollTop]);

  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(e.currentTarget.scrollTop);
  }, []);

  return {
    ...visibleItems,
    handleScroll
  };
};

// Lazy loading hook
export const useLazyLoading = <T>(
  loadMore: () => Promise<T[]>,
  hasMore: boolean,
  threshold: number = 100
) => {
  const [items, setItems] = React.useState<T[]>([]);
  const [loading, setLoading] = React.useState(false);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const loadingRef = useRef<HTMLDivElement | null>(null);

  const loadMoreItems = useCallback(async () => {
    if (loading || !hasMore) return;
    
    setLoading(true);
    try {
      const newItems = await loadMore();
      setItems(prev => [...prev, ...newItems]);
    } catch (error) {
    } finally {
      setLoading(false);
    }
  }, [loadMore, loading, hasMore]);

  useEffect(() => {
    if (!loadingRef.current) return;

    observerRef.current = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          loadMoreItems();
        }
      },
      { threshold: 0.1 }
    );

    observerRef.current.observe(loadingRef.current);

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [loadMoreItems]);

  return {
    items,
    loading,
    loadingRef,
    setItems
  };
};

// Performance monitoring
export const usePerformanceMonitor = (componentName: string) => {
  const renderCount = useRef(0);
  const startTime = useRef<number>(Date.now());

  useEffect(() => {
    renderCount.current++;
    const renderTime = Date.now() - startTime.current;
    
    if (process.env.NODE_ENV === 'development') {
    }
  });

  return {
    renderCount: renderCount.current,
    renderTime: Date.now() - startTime.current
  };
};