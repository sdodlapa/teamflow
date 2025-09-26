import React, { useState } from 'react';
import {
  CollaborationProvider,
  PresenceIndicator,
  ActiveUsersList,
  CollaborationStatus,
  RealtimeComments,
  LiveUpdateNotification,
  CollaborativeEditingIndicator
} from '../components/collaboration';
import collaborationTest from '../utils/collaborationTest';

const CollaborationDemo: React.FC = () => {
  const [selectedTaskId, setSelectedTaskId] = useState('task-1');
  const [editingField, setEditingField] = useState<string | null>(null);
  const [taskTitle, setTaskTitle] = useState('Sample Task');
  const [testResults, setTestResults] = useState<string>('');
  const workspaceId = 'demo-workspace';
  
  const handleRunTests = async () => {
    console.log('🧪 Running collaboration tests...');
    const results = await collaborationTest.runCollaborationTests();
    const displayText = collaborationTest.displayTestResults(results);
    setTestResults(displayText);
  };
  
  const mockTasks = [
    { id: 'task-1', title: 'Design Homepage' },
    { id: 'task-2', title: 'Implement Auth' },
    { id: 'task-3', title: 'Setup Database' }
  ];
  
  return (
    <CollaborationProvider workspaceId={workspaceId}>
      <div className="min-h-screen bg-gray-50 p-6">
        {/* Live Update Notifications */}
        <LiveUpdateNotification />
        
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Header with Status */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  🚀 Real-time Collaboration Demo
                </h1>
                <p className="text-gray-600 mt-2">
                  Experience live collaboration features in action
                </p>
              </div>
              <div className="text-right">
                <CollaborationStatus className="mb-2" />
                <div className="text-sm text-gray-500 mb-3">
                  Workspace: {workspaceId}
                </div>
                <button 
                  onClick={handleRunTests}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
                >
                  🧪 Test Connection
                </button>
              </div>
            </div>
            
            {testResults && (
              <div className="mt-4 p-4 bg-gray-100 rounded-lg">
                <pre className="text-sm text-gray-700 whitespace-pre-line font-mono">
                  {testResults}
                </pre>
              </div>
            )}
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Sidebar - Active Users */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                👥 Team Presence
              </h2>
              <ActiveUsersList showActivity={true} />
              
              <div className="mt-6 pt-6 border-t border-gray-200">
                <h3 className="text-lg font-medium text-gray-900 mb-3">
                  Individual Status
                </h3>
                <div className="space-y-2">
                  {['user-1', 'user-2', 'user-3'].map(userId => (
                    <div key={userId} className="flex items-center justify-between">
                      <span className="text-sm text-gray-700">User {userId}</span>
                      <PresenceIndicator userId={userId} showActivity={true} />
                    </div>
                  ))}
                </div>
              </div>
            </div>
            
            {/* Center - Task Editing */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900">
                  ✏️ Collaborative Editing
                </h2>
                <CollaborativeEditingIndicator 
                  entityType="task"
                  entityId={selectedTaskId}
                  currentField={editingField || undefined}
                />
              </div>
              
              {/* Task Selector */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Task to Edit
                </label>
                <select
                  value={selectedTaskId}
                  onChange={(e) => setSelectedTaskId(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {mockTasks.map(task => (
                    <option key={task.id} value={task.id}>
                      {task.title}
                    </option>
                  ))}
                </select>
              </div>
              
              {/* Editable Task Form */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Task Title
                  </label>
                  <input
                    type="text"
                    value={taskTitle}
                    onChange={(e) => setTaskTitle(e.target.value)}
                    onFocus={() => setEditingField('task title')}
                    onBlur={() => setEditingField(null)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Enter task title..."
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <textarea
                    onFocus={() => setEditingField('description')}
                    onBlur={() => setEditingField(null)}
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Enter task description..."
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Status
                  </label>
                  <select
                    onFocus={() => setEditingField('status')}
                    onBlur={() => setEditingField(null)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="todo">To Do</option>
                    <option value="in-progress">In Progress</option>
                    <option value="done">Done</option>
                  </select>
                </div>
              </div>
              
              <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                <div className="flex items-start gap-3">
                  <div className="w-5 h-5 text-blue-500 mt-0.5">💡</div>
                  <div>
                    <h4 className="font-medium text-blue-900">Live Collaboration</h4>
                    <p className="text-sm text-blue-700 mt-1">
                      When you edit fields, other users see your activity in real-time. 
                      Try opening this page in multiple tabs to see the magic!
                    </p>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Right - Live Comments */}
            <div className="bg-white rounded-lg shadow-sm overflow-hidden">
              <RealtimeComments 
                entityType="task"
                entityId={selectedTaskId}
                className="h-full"
              />
            </div>
          </div>
          
          {/* Bottom - Feature Showcase */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              🎯 Real-time Collaboration Features
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-4 bg-green-50 rounded-lg">
                <div className="text-2xl mb-2">👥</div>
                <h3 className="font-semibold text-green-900">User Presence</h3>
                <p className="text-sm text-green-700">
                  See who's online and what they're working on
                </p>
              </div>
              
              <div className="p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl mb-2">💬</div>
                <h3 className="font-semibold text-blue-900">Live Comments</h3>
                <p className="text-sm text-blue-700">
                  Chat in real-time with typing indicators
                </p>
              </div>
              
              <div className="p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl mb-2">✏️</div>
                <h3 className="font-semibold text-purple-900">Collaborative Editing</h3>
                <p className="text-sm text-purple-700">
                  See what others are editing simultaneously
                </p>
              </div>
              
              <div className="p-4 bg-yellow-50 rounded-lg">
                <div className="text-2xl mb-2">🔔</div>
                <h3 className="font-semibold text-yellow-900">Live Notifications</h3>
                <p className="text-sm text-yellow-700">
                  Get notified of changes as they happen
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </CollaborationProvider>
  );
};

export default CollaborationDemo;