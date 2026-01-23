/**
 * Performance monitoring for ChatKit widget rendering (T086)
 *
 * This module provides utilities to track and report performance metrics
 * for chat widget rendering, message processing, and API response times.
 */

export interface PerformanceMetric {
  name: string;
  startTime: number;
  endTime?: number;
  duration?: number;
  metadata?: Record<string, any>;
}

export interface PerformanceReport {
  sessionId: string;
  metrics: PerformanceMetric[];
  summary: {
    totalMetrics: number;
    averageRenderTime: number;
    maxRenderTime: number;
    minRenderTime: number;
    p95RenderTime: number;
    totalApiCalls: number;
    averageApiResponseTime: number;
  };
  timestamp: string;
}

type MetricCallback = (metric: PerformanceMetric) => void;

class PerformanceMonitor {
  private metrics: PerformanceMetric[] = [];
  private activeTimers: Map<string, PerformanceMetric> = new Map();
  private sessionId: string;
  private isEnabled: boolean = true;
  private callbacks: MetricCallback[] = [];
  private maxMetrics: number = 1000; // Limit stored metrics to prevent memory issues

  constructor() {
    this.sessionId = this.generateSessionId();
  }

  private generateSessionId(): string {
    return `perf-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
  }

  /**
   * Enable or disable performance monitoring
   */
  setEnabled(enabled: boolean): void {
    this.isEnabled = enabled;
  }

  /**
   * Check if monitoring is enabled
   */
  isMonitoringEnabled(): boolean {
    return this.isEnabled;
  }

  /**
   * Register a callback to be notified of new metrics
   */
  onMetric(callback: MetricCallback): () => void {
    this.callbacks.push(callback);
    return () => {
      this.callbacks = this.callbacks.filter(cb => cb !== callback);
    };
  }

  /**
   * Start timing an operation
   */
  startTimer(name: string, metadata?: Record<string, any>): void {
    if (!this.isEnabled) return;

    const metric: PerformanceMetric = {
      name,
      startTime: performance.now(),
      metadata,
    };

    this.activeTimers.set(name, metric);
  }

  /**
   * End timing an operation and record the metric
   */
  endTimer(name: string, additionalMetadata?: Record<string, any>): PerformanceMetric | null {
    if (!this.isEnabled) return null;

    const metric = this.activeTimers.get(name);
    if (!metric) {
      console.warn(`Performance timer "${name}" was not started`);
      return null;
    }

    metric.endTime = performance.now();
    metric.duration = metric.endTime - metric.startTime;

    if (additionalMetadata) {
      metric.metadata = { ...metric.metadata, ...additionalMetadata };
    }

    this.activeTimers.delete(name);
    this.recordMetric(metric);

    return metric;
  }

  /**
   * Record a metric directly (for external measurements)
   */
  recordMetric(metric: PerformanceMetric): void {
    if (!this.isEnabled) return;

    // Trim metrics if we've exceeded the limit
    if (this.metrics.length >= this.maxMetrics) {
      this.metrics = this.metrics.slice(-Math.floor(this.maxMetrics / 2));
    }

    this.metrics.push(metric);

    // Notify callbacks
    this.callbacks.forEach(cb => {
      try {
        cb(metric);
      } catch (error) {
        console.error('Performance monitor callback error:', error);
      }
    });

    // Log slow operations in development
    if (process.env.NODE_ENV === 'development' && metric.duration && metric.duration > 100) {
      console.warn(`Slow operation: ${metric.name} took ${metric.duration.toFixed(2)}ms`, metric.metadata);
    }
  }

  /**
   * Measure widget render time
   */
  measureWidgetRender(widgetType: string, fn: () => void): void {
    const timerName = `widget-render-${widgetType}-${Date.now()}`;
    this.startTimer(timerName, { type: 'widget-render', widgetType });

    try {
      fn();
    } finally {
      this.endTimer(timerName);
    }
  }

  /**
   * Measure async operation (like API calls)
   */
  async measureAsync<T>(
    name: string,
    fn: () => Promise<T>,
    metadata?: Record<string, any>
  ): Promise<T> {
    const timerName = `${name}-${Date.now()}`;
    this.startTimer(timerName, { type: 'async', ...metadata });

    try {
      const result = await fn();
      this.endTimer(timerName, { success: true });
      return result;
    } catch (error) {
      this.endTimer(timerName, { success: false, error: String(error) });
      throw error;
    }
  }

  /**
   * Get metrics filtered by name pattern
   */
  getMetricsByName(pattern: string | RegExp): PerformanceMetric[] {
    const regex = typeof pattern === 'string' ? new RegExp(pattern) : pattern;
    return this.metrics.filter(m => regex.test(m.name));
  }

  /**
   * Get widget render metrics
   */
  getWidgetRenderMetrics(): PerformanceMetric[] {
    return this.metrics.filter(m => m.metadata?.type === 'widget-render');
  }

  /**
   * Get API call metrics
   */
  getApiCallMetrics(): PerformanceMetric[] {
    return this.metrics.filter(m => m.name.includes('api-') || m.metadata?.type === 'async');
  }

  /**
   * Calculate percentile from a sorted array of numbers
   */
  private percentile(arr: number[], p: number): number {
    if (arr.length === 0) return 0;
    const index = Math.ceil((p / 100) * arr.length) - 1;
    return arr[Math.max(0, index)];
  }

  /**
   * Generate a performance report
   */
  generateReport(): PerformanceReport {
    const renderMetrics = this.getWidgetRenderMetrics();
    const apiMetrics = this.getApiCallMetrics();

    const renderTimes = renderMetrics
      .filter(m => m.duration !== undefined)
      .map(m => m.duration!)
      .sort((a, b) => a - b);

    const apiTimes = apiMetrics
      .filter(m => m.duration !== undefined)
      .map(m => m.duration!);

    const averageRender = renderTimes.length > 0
      ? renderTimes.reduce((a, b) => a + b, 0) / renderTimes.length
      : 0;

    const averageApi = apiTimes.length > 0
      ? apiTimes.reduce((a, b) => a + b, 0) / apiTimes.length
      : 0;

    return {
      sessionId: this.sessionId,
      metrics: this.metrics,
      summary: {
        totalMetrics: this.metrics.length,
        averageRenderTime: averageRender,
        maxRenderTime: renderTimes.length > 0 ? Math.max(...renderTimes) : 0,
        minRenderTime: renderTimes.length > 0 ? Math.min(...renderTimes) : 0,
        p95RenderTime: this.percentile(renderTimes, 95),
        totalApiCalls: apiMetrics.length,
        averageApiResponseTime: averageApi,
      },
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Clear all metrics
   */
  clearMetrics(): void {
    this.metrics = [];
    this.activeTimers.clear();
  }

  /**
   * Reset the session (clears metrics and generates new session ID)
   */
  resetSession(): void {
    this.clearMetrics();
    this.sessionId = this.generateSessionId();
  }

  /**
   * Export metrics as JSON for debugging or analytics
   */
  exportMetrics(): string {
    return JSON.stringify(this.generateReport(), null, 2);
  }
}

// Create singleton instance
export const performanceMonitor = new PerformanceMonitor();

// React hook for using performance monitoring
export function usePerformanceMonitor() {
  return {
    startTimer: performanceMonitor.startTimer.bind(performanceMonitor),
    endTimer: performanceMonitor.endTimer.bind(performanceMonitor),
    measureWidgetRender: performanceMonitor.measureWidgetRender.bind(performanceMonitor),
    measureAsync: performanceMonitor.measureAsync.bind(performanceMonitor),
    getReport: performanceMonitor.generateReport.bind(performanceMonitor),
    clearMetrics: performanceMonitor.clearMetrics.bind(performanceMonitor),
    setEnabled: performanceMonitor.setEnabled.bind(performanceMonitor),
    onMetric: performanceMonitor.onMetric.bind(performanceMonitor),
  };
}

// Utility function to wrap a function with performance measurement
export function withPerformanceMeasurement<T extends (...args: any[]) => any>(
  name: string,
  fn: T,
  metadata?: Record<string, any>
): T {
  return ((...args: Parameters<T>): ReturnType<T> => {
    const timerName = `${name}-${Date.now()}`;
    performanceMonitor.startTimer(timerName, metadata);

    try {
      const result = fn(...args);

      // Handle promises
      if (result instanceof Promise) {
        return result
          .then((value) => {
            performanceMonitor.endTimer(timerName, { success: true });
            return value;
          })
          .catch((error) => {
            performanceMonitor.endTimer(timerName, { success: false, error: String(error) });
            throw error;
          }) as ReturnType<T>;
      }

      performanceMonitor.endTimer(timerName, { success: true });
      return result;
    } catch (error) {
      performanceMonitor.endTimer(timerName, { success: false, error: String(error) });
      throw error;
    }
  }) as T;
}
