/**
 * Settings Page Component
 * Application and account settings (placeholder for future implementation)
 */

import React from 'react';
import Layout from '../components/Layout';
import { Settings as SettingsIcon, User, Bell, Shield, Palette, Globe } from 'lucide-react';

const Settings: React.FC = () => {
  return (
    <Layout>
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center">
            <SettingsIcon className="mr-3 text-blue-600" size={32} />
            Settings
          </h1>
          <p className="text-gray-600 mt-1">
            Manage your account preferences and application settings
          </p>
        </div>

        {/* Settings Categories */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Account Settings */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="flex items-center mb-4">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                <User className="text-blue-600" size={20} />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Account Settings</h3>
            </div>
            <p className="text-gray-600 text-sm mb-4">
              Manage your personal information and account preferences
            </p>
            <div className="space-y-3">
              <div className="flex justify-between items-center py-2 border-b border-gray-100">
                <span className="text-sm text-gray-700">Profile Information</span>
                <span className="text-xs text-blue-600 cursor-pointer hover:text-blue-700">Edit</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-gray-100">
                <span className="text-sm text-gray-700">Password & Security</span>
                <span className="text-xs text-blue-600 cursor-pointer hover:text-blue-700">Manage</span>
              </div>
              <div className="flex justify-between items-center py-2">
                <span className="text-sm text-gray-700">Email Preferences</span>
                <span className="text-xs text-blue-600 cursor-pointer hover:text-blue-700">Configure</span>
              </div>
            </div>
          </div>

          {/* Notifications */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="flex items-center mb-4">
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mr-3">
                <Bell className="text-green-600" size={20} />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Notifications</h3>
            </div>
            <p className="text-gray-600 text-sm mb-4">
              Control how and when you receive notifications
            </p>
            <div className="space-y-3">
              <div className="flex justify-between items-center py-2">
                <span className="text-sm text-gray-700">Task Updates</span>
                <div className="w-10 h-6 bg-blue-600 rounded-full relative cursor-pointer">
                  <div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full"></div>
                </div>
              </div>
              <div className="flex justify-between items-center py-2">
                <span className="text-sm text-gray-700">Project Changes</span>
                <div className="w-10 h-6 bg-gray-200 rounded-full relative cursor-pointer">
                  <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full"></div>
                </div>
              </div>
              <div className="flex justify-between items-center py-2">
                <span className="text-sm text-gray-700">Email Digest</span>
                <div className="w-10 h-6 bg-blue-600 rounded-full relative cursor-pointer">
                  <div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full"></div>
                </div>
              </div>
            </div>
          </div>

          {/* Privacy & Security */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="flex items-center mb-4">
              <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center mr-3">
                <Shield className="text-red-600" size={20} />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Privacy & Security</h3>
            </div>
            <p className="text-gray-600 text-sm mb-4">
              Manage your privacy settings and security preferences
            </p>
            <div className="space-y-3">
              <div className="flex justify-between items-center py-2 border-b border-gray-100">
                <span className="text-sm text-gray-700">Two-Factor Authentication</span>
                <span className="text-xs text-green-600">Enabled</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-gray-100">
                <span className="text-sm text-gray-700">Login History</span>
                <span className="text-xs text-blue-600 cursor-pointer hover:text-blue-700">View</span>
              </div>
              <div className="flex justify-between items-center py-2">
                <span className="text-sm text-gray-700">Data Export</span>
                <span className="text-xs text-blue-600 cursor-pointer hover:text-blue-700">Request</span>
              </div>
            </div>
          </div>

          {/* Appearance */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="flex items-center mb-4">
              <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mr-3">
                <Palette className="text-purple-600" size={20} />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Appearance</h3>
            </div>
            <p className="text-gray-600 text-sm mb-4">
              Customize the look and feel of your workspace
            </p>
            <div className="space-y-3">
              <div className="flex justify-between items-center py-2">
                <span className="text-sm text-gray-700">Theme</span>
                <select className="text-xs border border-gray-300 rounded px-2 py-1 focus:ring-1 focus:ring-blue-500">
                  <option>Light</option>
                  <option>Dark</option>
                  <option>Auto</option>
                </select>
              </div>
              <div className="flex justify-between items-center py-2">
                <span className="text-sm text-gray-700">Language</span>
                <select className="text-xs border border-gray-300 rounded px-2 py-1 focus:ring-1 focus:ring-blue-500">
                  <option>English</option>
                  <option>Spanish</option>
                  <option>French</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Coming Soon Banner */}
        <div className="mt-8 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6 text-center">
          <Globe size={48} className="mx-auto text-blue-600 mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Advanced Settings Coming Soon</h3>
          <p className="text-gray-600 max-w-2xl mx-auto">
            We're working on comprehensive settings management including team preferences, 
            integration configurations, and advanced customization options. Stay tuned for updates!
          </p>
        </div>
      </div>
    </Layout>
  );
};

export default Settings;