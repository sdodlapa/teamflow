/**
 * File Management Test Page - Day 19 Implementation
 * Test page to demonstrate all file management features
 */

import React, { useState } from 'react';
import { FileUpload } from '../services/fileApi';
import FileUploadComponent from '../components/FileUpload';
import FileBrowser from '../components/FileBrowser';
import FilePreview from '../components/FilePreview';

const FileManagementTest: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<FileUpload | null>(null);
  const [showPreview, setShowPreview] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const [activeTab, setActiveTab] = useState<'upload' | 'browser' | 'preview'>('upload');

  const handleFileSelect = (file: FileUpload) => {
    setSelectedFile(file);
    setShowPreview(true);
  };

  const handleUploadComplete = () => {
    setRefreshKey(prev => prev + 1); // Force browser refresh
  };

  const handleDownload = async (file: FileUpload) => {
    try {
      // Create a temporary link and trigger download
      const link = document.createElement('a');
      link.href = `/api/v1/files/${file.id}`;
      link.download = file.original_filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Download failed:', error);
    }
  };

  const handleShare = async (file: FileUpload) => {
    try {
      // This would integrate with the file sharing API
      const shareUrl = `${window.location.origin}/shared/${file.id}`;
      await navigator.clipboard.writeText(shareUrl);
      alert('Share link copied to clipboard!');
    } catch (error) {
      console.error('Share failed:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">File Management System</h1>
          <p className="mt-2 text-lg text-gray-600">
            Day 19 Implementation - Complete file upload, browse, and preview functionality
          </p>
        </div>

        {/* Simple Tab Navigation */}
        <div className="mb-6">
          <div className="flex space-x-4 border-b">
            <button
              onClick={() => setActiveTab('upload')}
              className={`px-4 py-2 font-medium ${
                activeTab === 'upload'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              File Upload
            </button>
            <button
              onClick={() => setActiveTab('browser')}
              className={`px-4 py-2 font-medium ${
                activeTab === 'browser'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              File Browser
            </button>
            <button
              onClick={() => setActiveTab('preview')}
              className={`px-4 py-2 font-medium ${
                activeTab === 'preview'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              File Preview
            </button>
          </div>
        </div>

        {/* Upload Tab */}
        {activeTab === 'upload' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">Upload Files</h2>
              <p className="text-gray-600 mb-6">
                Drag and drop files or click to select. Supports images, documents, videos, and more.
              </p>
              
              <FileUploadComponent
                onUploadComplete={handleUploadComplete}
                allowMultiple={true}
                maxFiles={10}
                maxFileSize={50 * 1024 * 1024} // 50MB
                acceptedFileTypes={['.png', '.jpg', '.jpeg', '.gif', '.webp', '.pdf', '.txt', '.md', '.json', '.docx', '.xlsx']}
              />

              <div className="mt-6 p-4 bg-blue-50 rounded-md">
                <h3 className="font-medium text-blue-900 mb-2">Features Demonstrated:</h3>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• Drag and drop interface using react-dropzone</li>
                  <li>• File type validation and size limits</li>
                  <li>• Upload progress indicators</li>
                  <li>• Multiple file selection</li>
                  <li>• Error handling and user feedback</li>
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Browser Tab */}
        {activeTab === 'browser' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow">
              <div className="p-6 border-b">
                <h2 className="text-xl font-semibold">File Browser</h2>
                <p className="text-gray-600 mt-1">
                  Browse, search, and manage uploaded files with grid and list views.
                </p>
              </div>
              
              <div key={refreshKey}>
                <FileBrowser
                  onFileSelect={handleFileSelect}
                  allowUpload={true}
                  allowMultiSelect={false}
                  viewMode="grid"
                />
              </div>

              <div className="p-6 border-t bg-gray-50">
                <h3 className="font-medium text-gray-900 mb-2">Features Demonstrated:</h3>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Grid and list view modes</li>
                  <li>• Search and filter functionality</li>
                  <li>• File type icons and thumbnails</li>
                  <li>• Sort by name, date, size</li>
                  <li>• Context menus with actions</li>
                  <li>• Pagination for large file lists</li>
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Preview Tab */}
        {activeTab === 'preview' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">File Preview</h2>
              <p className="text-gray-600 mb-6">
                Select a file from the browser tab to preview it here.
              </p>

              {selectedFile ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <h3 className="font-medium">{selectedFile.original_filename}</h3>
                      <p className="text-sm text-gray-500">
                        {selectedFile.file_type} • {selectedFile.human_readable_size}
                      </p>
                    </div>
                    <button
                      onClick={() => setShowPreview(true)}
                      className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                    >
                      Open Preview
                    </button>
                  </div>

                  <div className="p-4 bg-green-50 rounded-md">
                    <h3 className="font-medium text-green-900 mb-2">Preview Features:</h3>
                    <ul className="text-sm text-green-800 space-y-1">
                      <li>• Image preview with zoom and rotate controls</li>
                      <li>• PDF document viewer</li>
                      <li>• Video and audio playback</li>
                      <li>• Text file content display</li>
                      <li>• Fullscreen mode</li>
                      <li>• Download and share options</li>
                    </ul>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <p>No file selected for preview</p>
                  <p className="text-sm mt-1">Click on a file in the browser tab to preview it</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* File Preview Modal */}
        <FilePreview
          file={selectedFile}
          isOpen={showPreview}
          onClose={() => setShowPreview(false)}
          onDownload={handleDownload}
          onShare={handleShare}
        />

        {/* Implementation Summary */}
        <div className="mt-12 bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Day 19 - File Management System Complete</h2>
          
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-medium text-gray-900 mb-3">Backend Implementation</h3>
              <ul className="text-sm text-gray-600 space-y-2">
                <li>✅ Re-enabled file management service</li>
                <li>✅ FastAPI routes for CRUD operations</li>
                <li>✅ File validation and security</li>
                <li>✅ Thumbnail generation</li>
                <li>✅ File sharing and permissions</li>
                <li>✅ Deployment-compatible MIME detection</li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-medium text-gray-900 mb-3">Frontend Implementation</h3>
              <ul className="text-sm text-gray-600 space-y-2">
                <li>✅ React-dropzone upload component</li>
                <li>✅ File browser with grid/list views</li>
                <li>✅ Multi-format file preview</li>
                <li>✅ Search and filter functionality</li>
                <li>✅ Progress indicators and error handling</li>
                <li>✅ Responsive design and accessibility</li>
              </ul>
            </div>
          </div>

          <div className="mt-6 p-4 bg-yellow-50 rounded-md">
            <h3 className="font-medium text-yellow-900 mb-2">🎉 Day 19 Complete!</h3>
            <p className="text-sm text-yellow-800">
              File management system has been fully restored and enhanced with modern React components,
              drag-and-drop functionality, comprehensive previews, and robust backend integration.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FileManagementTest;