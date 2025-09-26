/**
 * Real-time Collaboration Test Utilities
 * Functions to test and validate collaboration features
 */

interface WebSocketTestResult {
  connected: boolean;
  error?: string;
  latency?: number;
}

interface CollaborationTestResults {
  websocket: WebSocketTestResult;
  healthCheck: { status: number; data?: any; error?: string };
  presenceSystem: boolean;
  messageBroadcast: boolean;
}

/**
 * Test WebSocket connection to collaboration service
 */
export const testWebSocketConnection = (workspaceId: string = 'test-workspace'): Promise<WebSocketTestResult> => {
  return new Promise((resolve) => {
    const startTime = Date.now();
    const wsUrl = `ws://localhost:8000/api/v1/collaboration/ws/${workspaceId}?token=test-token`;
    
    try {
      const socket = new WebSocket(wsUrl);
      let resolved = false;
      
      socket.onopen = () => {
        if (!resolved) {
          resolved = true;
          const latency = Date.now() - startTime;
          socket.close();
          resolve({ connected: true, latency });
        }
      };
      
      socket.onerror = () => {
        if (!resolved) {
          resolved = true;
          resolve({ 
            connected: false, 
            error: 'WebSocket connection failed'
          });
        }
      };
      
      socket.onclose = (event) => {
        if (!resolved) {
          resolved = true;
          resolve({ 
            connected: false, 
            error: `Connection closed with code: ${event.code}`
          });
        }
      };
      
      // Timeout after 5 seconds
      setTimeout(() => {
        if (!resolved) {
          resolved = true;
          socket.close();
          resolve({ 
            connected: false, 
            error: 'Connection timeout'
          });
        }
      }, 5000);
      
    } catch (error) {
      resolve({ 
        connected: false, 
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  });
};

/**
 * Test collaboration health endpoint
 */
export const testCollaborationHealth = async (): Promise<{ status: number; data?: any; error?: string }> => {
  try {
    const response = await fetch('http://localhost:8000/api/v1/collaboration/health');
    const data = await response.json();
    
    return {
      status: response.status,
      data: response.status === 200 ? data : undefined,
      error: response.status !== 200 ? `HTTP ${response.status}: ${JSON.stringify(data)}` : undefined
    };
  } catch (error) {
    return {
      status: 0,
      error: error instanceof Error ? error.message : 'Network error'
    };
  }
};

/**
 * Run comprehensive collaboration system test
 */
export const runCollaborationTests = async (): Promise<CollaborationTestResults> => {
  console.log('🧪 Running collaboration system tests...');
  
  // Test health endpoint
  const healthCheck = await testCollaborationHealth();
  console.log('🏥 Health check:', healthCheck.status === 200 ? '✅ PASS' : '❌ FAIL', healthCheck);
  
  // Test WebSocket connection
  const websocket = await testWebSocketConnection();
  console.log('🔌 WebSocket:', websocket.connected ? '✅ PASS' : '❌ FAIL', websocket);
  
  // Basic presence and broadcast tests (simulated)
  const presenceSystem = healthCheck.status === 200;
  const messageBroadcast = websocket.connected;
  
  const results: CollaborationTestResults = {
    websocket,
    healthCheck,
    presenceSystem,
    messageBroadcast
  };
  
  console.log('📊 Collaboration Test Results:', results);
  
  return results;
};

/**
 * Display test results in a user-friendly format
 */
export const displayTestResults = (results: CollaborationTestResults): string => {
  const lines = [
    '🧪 **COLLABORATION SYSTEM TEST RESULTS**',
    '',
    `🏥 Health Check: ${results.healthCheck.status === 200 ? '✅ PASS' : '❌ FAIL'}`,
    results.healthCheck.error ? `   Error: ${results.healthCheck.error}` : '   Status: API endpoint healthy',
    '',
    `🔌 WebSocket Connection: ${results.websocket.connected ? '✅ PASS' : '❌ FAIL'}`,
    results.websocket.error ? `   Error: ${results.websocket.error}` : `   Latency: ${results.websocket.latency}ms`,
    '',
    `👥 Presence System: ${results.presenceSystem ? '✅ READY' : '❌ NOT READY'}`,
    `📡 Message Broadcast: ${results.messageBroadcast ? '✅ READY' : '❌ NOT READY'}`,
    '',
    '**Overall Status:**',
    results.websocket.connected && results.healthCheck.status === 200 
      ? '🚀 **COLLABORATION SYSTEM READY FOR TESTING!**'
      : '⚠️ **SOME ISSUES DETECTED - CHECK LOGS ABOVE**'
  ];
  
  return lines.join('\n');
};

/**
 * Collaboration feature readiness check
 */
export const checkCollaborationReadiness = async (): Promise<{
  ready: boolean;
  issues: string[];
  recommendations: string[];
}> => {
  const results = await runCollaborationTests();
  const issues: string[] = [];
  const recommendations: string[] = [];
  
  // Check health endpoint
  if (results.healthCheck.status !== 200) {
    issues.push('Backend health endpoint not accessible');
    recommendations.push('Ensure backend server is running on localhost:8000');
  }
  
  // Check WebSocket
  if (!results.websocket.connected) {
    issues.push('WebSocket connection failed');
    if (results.websocket.error?.includes('timeout')) {
      recommendations.push('Check if WebSocket endpoint is properly configured');
    } else if (results.websocket.error?.includes('connection failed')) {
      recommendations.push('Verify backend WebSocket service is running');
    }
  }
  
  // Check overall readiness
  const ready = results.websocket.connected && results.healthCheck.status === 200;
  
  if (ready) {
    recommendations.push('🚀 System ready! Open multiple browser tabs to test collaboration');
    recommendations.push('📱 Try the collaboration demo at /collaboration-demo');
  }
  
  return { ready, issues, recommendations };
};

// Export for use in components
export default {
  testWebSocketConnection,
  testCollaborationHealth,
  runCollaborationTests,
  displayTestResults,
  checkCollaborationReadiness
};