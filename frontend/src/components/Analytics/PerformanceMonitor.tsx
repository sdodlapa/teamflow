import React, { useState, useEffect, useRef } from 'react';
import {
  Activity, Cpu, HardDrive, Wifi, Database,
  Server, AlertTriangle, CheckCircle, Clock,
  Zap, Globe, RefreshCw, Settings, Download,
  TrendingUp, TrendingDown, Minus
} from 'lucide-react';
import './PerformanceMonitor.css';

interface SystemMetric {
  id: string;
  name: string;
  value: number;
  unit: string;
  threshold: {
    warning: number;
    critical: number;
  };
  trend: 'up' | 'down' | 'stable';
  history: { timestamp: string; value: number }[];
  status: 'healthy' | 'warning' | 'critical';
}

interface SystemAlert {
  id: string;
  type: 'info' | 'warning' | 'error';
  message: string;
  timestamp: string;
  metric?: string;
  resolved: boolean;
}

interface PerformanceMonitorProps {
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export const PerformanceMonitor: React.FC<PerformanceMonitorProps> = ({
  autoRefresh = true,
  refreshInterval = 5000
}) => {
  const [metrics, setMetrics] = useState<SystemMetric[]>([]);
  const [alerts, setAlerts] = useState<SystemAlert[]>([]);
  const [selectedMetric, setSelectedMetric] = useState<SystemMetric | null>(null);
  const [timeRange, setTimeRange] = useState<'1h' | '6h' | '24h' | '7d'>('1h');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const intervalRef = useRef<number | null>(null);

  // Mock system metrics data
  const generateMockMetrics = (): SystemMetric[] => {
    const now = new Date();
    const historyPoints = 60; // Last 60 data points

    return [
      {
        id: 'cpu_usage',
        name: 'CPU Usage',
        value: Math.random() * 100,
        unit: '%',
        threshold: { warning: 70, critical: 90 },
        trend: Math.random() > 0.5 ? 'up' : 'down',
        history: Array.from({ length: historyPoints }, (_, i) => ({
          timestamp: new Date(now.getTime() - (historyPoints - i) * 60000).toISOString(),
          value: Math.random() * 100
        })),
        status: 'healthy'
      },
      {
        id: 'memory_usage',
        name: 'Memory Usage',
        value: Math.random() * 100,
        unit: '%',
        threshold: { warning: 80, critical: 95 },
        trend: Math.random() > 0.5 ? 'up' : 'stable',
        history: Array.from({ length: historyPoints }, (_, i) => ({
          timestamp: new Date(now.getTime() - (historyPoints - i) * 60000).toISOString(),
          value: Math.random() * 100
        })),
        status: 'healthy'
      },
      {
        id: 'disk_usage',
        name: 'Disk Usage',
        value: Math.random() * 100,
        unit: '%',
        threshold: { warning: 85, critical: 95 },
        trend: 'stable',
        history: Array.from({ length: historyPoints }, (_, i) => ({
          timestamp: new Date(now.getTime() - (historyPoints - i) * 60000).toISOString(),
          value: 60 + Math.random() * 20
        })),
        status: 'warning'
      },
      {
        id: 'network_io',
        name: 'Network I/O',
        value: Math.random() * 1000,
        unit: 'MB/s',
        threshold: { warning: 800, critical: 950 },
        trend: 'up',
        history: Array.from({ length: historyPoints }, (_, i) => ({
          timestamp: new Date(now.getTime() - (historyPoints - i) * 60000).toISOString(),
          value: Math.random() * 1000
        })),
        status: 'healthy'
      },
      {
        id: 'database_connections',
        name: 'DB Connections',
        value: Math.floor(Math.random() * 200),
        unit: 'connections',
        threshold: { warning: 150, critical: 180 },
        trend: 'down',
        history: Array.from({ length: historyPoints }, (_, i) => ({
          timestamp: new Date(now.getTime() - (historyPoints - i) * 60000).toISOString(),
          value: Math.floor(Math.random() * 200)
        })),
        status: 'healthy'
      },
      {
        id: 'response_time',
        name: 'Response Time',
        value: Math.random() * 1000,
        unit: 'ms',
        threshold: { warning: 500, critical: 800 },
        trend: Math.random() > 0.7 ? 'up' : 'stable',
        history: Array.from({ length: historyPoints }, (_, i) => ({
          timestamp: new Date(now.getTime() - (historyPoints - i) * 60000).toISOString(),
          value: Math.random() * 1000
        })),
        status: 'healthy'
      }
    ];
  };

  // Mock alerts data
  const generateMockAlerts = (): SystemAlert[] => {
    return [
      {
        id: 'alert-1',
        type: 'warning',
        message: 'High disk usage detected on /var partition',
        timestamp: new Date(Date.now() - 300000).toISOString(),
        metric: 'disk_usage',
        resolved: false
      },
      {
        id: 'alert-2',
        type: 'info',
        message: 'Database backup completed successfully',
        timestamp: new Date(Date.now() - 900000).toISOString(),
        resolved: true
      },
      {
        id: 'alert-3',
        type: 'error',
        message: 'Failed to connect to external API service',
        timestamp: new Date(Date.now() - 1800000).toISOString(),
        resolved: false
      }
    ];
  };

  useEffect(() => {
    // Initial load
    const initialMetrics = generateMockMetrics();
    setMetrics(initialMetrics.map(metric => ({
      ...metric,
      status: getMetricStatus(metric.value, metric.threshold)
    })));
    setAlerts(generateMockAlerts());
    setSelectedMetric(initialMetrics[0]);

    // Set up auto-refresh
    if (autoRefresh) {
      intervalRef.current = window.setInterval(refreshData, refreshInterval);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [autoRefresh, refreshInterval]);

  const getMetricStatus = (value: number, threshold: { warning: number; critical: number }) => {
    if (value >= threshold.critical) return 'critical';
    if (value >= threshold.warning) return 'warning';
    return 'healthy';
  };

  const refreshData = async () => {
    setIsRefreshing(true);
    
    // Simulate API delay
    setTimeout(() => {
      const newMetrics = generateMockMetrics();
      setMetrics(newMetrics.map(metric => ({
        ...metric,
        status: getMetricStatus(metric.value, metric.threshold)
      })));
      setIsRefreshing(false);
    }, 1000);
  };

  const getTrendIcon = (trend: SystemMetric['trend']) => {
    switch (trend) {
      case 'up':
        return <TrendingUp size={14} className="trend-up" />;
      case 'down':
        return <TrendingDown size={14} className="trend-down" />;
      default:
        return <Minus size={14} className="trend-stable" />;
    }
  };

  const getStatusColor = (status: SystemMetric['status']) => {
    switch (status) {
      case 'critical':
        return '#ef4444';
      case 'warning':
        return '#f59e0b';
      default:
        return '#10b981';
    }
  };

  const getMetricIcon = (metricId: string) => {
    switch (metricId) {
      case 'cpu_usage':
        return <Cpu size={20} />;
      case 'memory_usage':
        return <Zap size={20} />;
      case 'disk_usage':
        return <HardDrive size={20} />;
      case 'network_io':
        return <Wifi size={20} />;
      case 'database_connections':
        return <Database size={20} />;
      case 'response_time':
        return <Activity size={20} />;
      default:
        return <Server size={20} />;
    }
  };

  const formatValue = (value: number, unit: string): string => {
    if (unit === '%') {
      return `${value.toFixed(1)}%`;
    }
    if (unit === 'MB/s') {
      return `${value.toFixed(1)} MB/s`;
    }
    if (unit === 'ms') {
      return `${value.toFixed(0)}ms`;
    }
    return `${value.toFixed(0)} ${unit}`;
  };

  const renderMetricCard = (metric: SystemMetric) => {
    const isSelected = selectedMetric?.id === metric.id;
    
    return (
      <div
        key={metric.id}
        className={`metric-card ${isSelected ? 'selected' : ''}`}
        onClick={() => setSelectedMetric(metric)}
        style={{ '--status-color': getStatusColor(metric.status) } as React.CSSProperties}
      >
        <div className="metric-header">
          <div className="metric-icon" style={{ color: getStatusColor(metric.status) }}>
            {getMetricIcon(metric.id)}
          </div>
          <div className="metric-trend">
            {getTrendIcon(metric.trend)}
          </div>
        </div>
        
        <div className="metric-value">
          {formatValue(metric.value, metric.unit)}
        </div>
        
        <div className="metric-name">{metric.name}</div>
        
        <div className="metric-status-bar">
          <div
            className="status-fill"
            style={{
              width: `${Math.min((metric.value / metric.threshold.critical) * 100, 100)}%`,
              backgroundColor: getStatusColor(metric.status)
            }}
          />
        </div>
        
        <div className="metric-threshold">
          Warning: {metric.threshold.warning}{metric.unit} | 
          Critical: {metric.threshold.critical}{metric.unit}
        </div>
      </div>
    );
  };

  const renderChart = () => {
    if (!selectedMetric) return null;

    const maxValue = Math.max(...selectedMetric.history.map(h => h.value));
    const recentHistory = selectedMetric.history.slice(-20); // Show last 20 points

    return (
      <div className="chart-container">
        <div className="chart-header">
          <h3>{selectedMetric.name} - {timeRange} view</h3>
          <div className="chart-controls">
            <div className="time-range-selector">
              {(['1h', '6h', '24h', '7d'] as const).map(range => (
                <button
                  key={range}
                  className={`range-btn ${timeRange === range ? 'active' : ''}`}
                  onClick={() => setTimeRange(range)}
                >
                  {range}
                </button>
              ))}
            </div>
          </div>
        </div>
        
        <div className="chart-content">
          <div className="chart-grid">
            {recentHistory.map((point, index) => (
              <div
                key={index}
                className="chart-point"
                style={{
                  height: `${(point.value / maxValue) * 100}%`,
                  backgroundColor: getStatusColor(
                    getMetricStatus(point.value, selectedMetric.threshold)
                  )
                }}
              />
            ))}
          </div>
          
          <div className="chart-thresholds">
            <div
              className="threshold-line critical"
              style={{
                bottom: `${(selectedMetric.threshold.critical / maxValue) * 100}%`
              }}
            >
              <span>Critical</span>
            </div>
            <div
              className="threshold-line warning"
              style={{
                bottom: `${(selectedMetric.threshold.warning / maxValue) * 100}%`
              }}
            >
              <span>Warning</span>
            </div>
          </div>
        </div>
        
        <div className="chart-legend">
          <div className="legend-item">
            <div className="legend-color healthy" />
            <span>Healthy</span>
          </div>
          <div className="legend-item">
            <div className="legend-color warning" />
            <span>Warning</span>
          </div>
          <div className="legend-item">
            <div className="legend-color critical" />
            <span>Critical</span>
          </div>
        </div>
      </div>
    );
  };

  const renderAlerts = () => {
    const activeAlerts = alerts.filter(alert => !alert.resolved);
    
    return (
      <div className="alerts-panel">
        <div className="alerts-header">
          <h3>Active Alerts ({activeAlerts.length})</h3>
          <button className="clear-all-btn">Clear All</button>
        </div>
        
        <div className="alerts-list">
          {activeAlerts.map(alert => (
            <div key={alert.id} className={`alert-item alert-${alert.type}`}>
              <div className="alert-icon">
                {alert.type === 'error' && <AlertTriangle size={16} />}
                {alert.type === 'warning' && <AlertTriangle size={16} />}
                {alert.type === 'info' && <CheckCircle size={16} />}
              </div>
              <div className="alert-content">
                <div className="alert-message">{alert.message}</div>
                <div className="alert-time">
                  <Clock size={12} />
                  {new Date(alert.timestamp).toLocaleString()}
                </div>
              </div>
              <button className="resolve-btn">Resolve</button>
            </div>
          ))}
          
          {activeAlerts.length === 0 && (
            <div className="no-alerts">
              <CheckCircle size={32} />
              <p>No active alerts</p>
              <span>All systems are running normally</span>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="performance-monitor">
      <div className="monitor-header">
        <div className="header-content">
          <h1>Performance Monitor</h1>
          <p>Real-time system health and performance metrics</p>
        </div>
        
        <div className="header-actions">
          <button
            className="action-btn secondary"
            onClick={() => setShowSettings(!showSettings)}
          >
            <Settings size={16} />
            Settings
          </button>
          <button
            className="action-btn secondary"
            onClick={refreshData}
            disabled={isRefreshing}
          >
            <RefreshCw size={16} className={isRefreshing ? 'spinning' : ''} />
            {isRefreshing ? 'Refreshing...' : 'Refresh'}
          </button>
          <button className="action-btn secondary">
            <Download size={16} />
            Export
          </button>
        </div>
      </div>

      {showSettings && (
        <div className="settings-panel">
          <div className="setting-group">
            <label>Auto Refresh</label>
            <input type="checkbox" defaultChecked={autoRefresh} />
          </div>
          <div className="setting-group">
            <label>Refresh Interval</label>
            <select defaultValue={refreshInterval}>
              <option value={1000}>1 second</option>
              <option value={5000}>5 seconds</option>
              <option value={10000}>10 seconds</option>
              <option value={30000}>30 seconds</option>
            </select>
          </div>
        </div>
      )}

      <div className="monitor-content">
        <div className="metrics-overview">
          <div className="overview-header">
            <h2>System Metrics</h2>
            <div className="system-status">
              <Globe size={16} />
              <span className="status-text">System Status: </span>
              <span className="status-indicator healthy">Healthy</span>
            </div>
          </div>
          
          <div className="metrics-grid">
            {metrics.map(renderMetricCard)}
          </div>
        </div>

        <div className="monitor-details">
          <div className="details-grid">
            <div className="chart-section">
              {renderChart()}
            </div>
            <div className="alerts-section">
              {renderAlerts()}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};