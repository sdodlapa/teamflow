import React from 'react';
import { Wifi, WifiOff, Users, Clock } from 'lucide-react';

interface RealTimeStatusProps {
  isConnected: boolean;
  connectionState: string;
  activeUsersCount: number;
  lastSyncTime?: number;
  isSyncing?: boolean;
}

const RealTimeStatus: React.FC<RealTimeStatusProps> = ({
  isConnected,
  connectionState,
  activeUsersCount,
  lastSyncTime,
  isSyncing = false
}) => {
  const getStatusColor = () => {
    switch (connectionState) {
      case 'connected': return '#10b981';
      case 'connecting': return '#f59e0b';
      case 'disconnected': return '#ef4444';
      case 'error': return '#dc2626';
      default: return '#6b7280';
    }
  };

  const getStatusText = () => {
    switch (connectionState) {
      case 'connected': return 'Live';
      case 'connecting': return 'Connecting';
      case 'disconnected': return 'Offline';
      case 'error': return 'Error';
      default: return 'Unknown';
    }
  };

  const formatLastSync = () => {
    if (!lastSyncTime) return 'Never';
    
    const now = Date.now();
    const diff = now - lastSyncTime;
    
    if (diff < 1000) return 'Just now';
    if (diff < 60000) return `${Math.floor(diff / 1000)}s ago`;
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    return `${Math.floor(diff / 3600000)}h ago`;
  };

  return (
    <div style={{
      position: 'fixed',
      bottom: '20px',
      right: '20px',
      background: 'white',
      padding: '0.75rem 1rem',
      borderRadius: '0.5rem',
      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
      border: '1px solid #e5e7eb',
      display: 'flex',
      alignItems: 'center',
      gap: '0.75rem',
      fontSize: '0.875rem',
      zIndex: 999,
      minWidth: '200px'
    }}>
      {/* Connection Status */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        {isConnected ? <Wifi size={16} /> : <WifiOff size={16} />}
        <span style={{ 
          color: getStatusColor(),
          fontWeight: '600'
        }}>
          {getStatusText()}
        </span>
        {isSyncing && (
          <div style={{
            width: '12px',
            height: '12px',
            borderRadius: '50%',
            background: '#3b82f6',
            animation: 'pulse 1s ease-in-out infinite'
          }} />
        )}
      </div>

      {/* Separator */}
      <div style={{
        width: '1px',
        height: '16px',
        background: '#e5e7eb'
      }} />

      {/* Active Users */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
        <Users size={14} color="#6b7280" />
        <span style={{ color: '#374151' }}>
          {activeUsersCount}
        </span>
      </div>

      {/* Last Sync */}
      {lastSyncTime && (
        <>
          <div style={{
            width: '1px',
            height: '16px',
            background: '#e5e7eb'
          }} />
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <Clock size={14} color="#6b7280" />
            <span style={{ color: '#6b7280', fontSize: '0.75rem' }}>
              {formatLastSync()}
            </span>
          </div>
        </>
      )}

      <style>
        {`
          @keyframes pulse {
            0%, 100% {
              transform: scale(1);
              opacity: 1;
            }
            50% {
              transform: scale(1.1);
              opacity: 0.7;
            }
          }
        `}
      </style>
    </div>
  );
};

export default RealTimeStatus;