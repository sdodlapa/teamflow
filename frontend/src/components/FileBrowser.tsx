/**
 * File Browser Component - Day 19 Implementation
 * File management interface with preview, download, and sharing functionality
 */

import React, { useState, useEffect } from 'react';
import {
  File,
  Download,
  Share2,
  Trash2,
  Search,
  Grid,
  List,
  User,
  FolderOpen,
  Image as ImageIcon,
  FileText,
  Archive,
  Music,
  Video,
  MoreVertical
} from 'lucide-react';
import { fileApiService, FileUpload, FileSearchRequest, FileListResponse } from '../services/fileApi';
import FileUploadComponent from './FileUpload';

export interface FileBrowserProps {
  projectId?: number;
  taskId?: number;
  onFileSelect?: (file: FileUpload) => void;
  allowUpload?: boolean;
  allowMultiSelect?: boolean;
  viewMode?: 'grid' | 'list';
  className?: string;
}

const FileBrowser: React.FC<FileBrowserProps> = ({
  projectId,
  taskId,
  onFileSelect,
  allowUpload = true,
  allowMultiSelect = false,
  viewMode: initialViewMode = 'grid',
  className = ''
}) => {
  const [files, setFiles] = useState<FileUpload[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>(initialViewMode);
  const [selectedFiles, setSelectedFiles] = useState<Set<number>>(new Set());
  const [sortBy, setSortBy] = useState('uploaded_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [showUpload, setShowUpload] = useState(false);
  const [fileTypeFilter, setFileTypeFilter] = useState<string>('');
  const [contextMenu, setContextMenu] = useState<{
    fileId: number;
    x: number;
    y: number;
  } | null>(null);

  const loadFiles = async (page = 1) => {
    try {
      setLoading(true);
      const searchRequest: FileSearchRequest = {
        filename: searchTerm || undefined,
        project_id: projectId,
        task_id: taskId,
        page,
        page_size: 20,
        sort_by: sortBy,
        sort_order: sortOrder,
        file_type: fileTypeFilter ? [fileTypeFilter] : undefined
      };

      const response: FileListResponse = await fileApiService.listFiles(searchRequest);
      setFiles(response.files);
      setTotalPages(response.total_pages);
      setCurrentPage(response.page);
    } catch (error) {
      console.error('Failed to load files:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFiles(1);
  }, [searchTerm, sortBy, sortOrder, fileTypeFilter, projectId, taskId]);

  const getFileIcon = (file: FileUpload, size = 'h-6 w-6') => {
    if (file.is_image) return <ImageIcon className={`${size} text-blue-500`} />;
    if (file.file_type.includes('video')) return <Video className={`${size} text-purple-500`} />;
    if (file.file_type.includes('audio')) return <Music className={`${size} text-green-500`} />;
    if (file.is_document) return <FileText className={`${size} text-orange-500`} />;
    if (file.file_type.includes('zip') || file.file_type.includes('archive')) return <Archive className={`${size} text-gray-500`} />;
    return <File className={`${size} text-gray-500`} />;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleFileClick = (file: FileUpload) => {
    if (allowMultiSelect) {
      const newSelected = new Set(selectedFiles);
      if (newSelected.has(file.id)) {
        newSelected.delete(file.id);
      } else {
        newSelected.add(file.id);
      }
      setSelectedFiles(newSelected);
    }
    
    if (onFileSelect) {
      onFileSelect(file);
    }
  };

  const handleDownload = async (file: FileUpload) => {
    try {
      await fileApiService.downloadFile(file.id, file.original_filename);
    } catch (error) {
      console.error('Download failed:', error);
    }
  };

  const handleDelete = async (file: FileUpload) => {
    if (window.confirm(`Are you sure you want to delete "${file.original_filename}"?`)) {
      try {
        await fileApiService.deleteFile(file.id);
        loadFiles(currentPage);
      } catch (error) {
        console.error('Delete failed:', error);
      }
    }
  };

  const handleShare = async (file: FileUpload) => {
    try {
      const shareResponse = await fileApiService.createFileShare(file.id, {
        expires_in_hours: 24,
        allow_download: true,
        allow_preview: true
      });
      
      // Copy share URL to clipboard
      await navigator.clipboard.writeText(shareResponse.share_url);
      alert('Share link copied to clipboard!');
    } catch (error) {
      console.error('Share failed:', error);
    }
  };

  const handleContextMenu = (e: React.MouseEvent, file: FileUpload) => {
    e.preventDefault();
    setContextMenu({
      fileId: file.id,
      x: e.clientX,
      y: e.clientY
    });
  };

  const handleUploadComplete = (_uploadedFiles: FileUpload[]) => {
    setShowUpload(false);
    loadFiles(currentPage);
  };

  const fileTypes = [
    { value: '', label: 'All Files' },
    { value: 'pdf', label: 'PDF Documents' },
    { value: 'jpeg', label: 'Images' },
    { value: 'docx', label: 'Word Documents' },
    { value: 'xlsx', label: 'Spreadsheets' },
    { value: 'zip', label: 'Archives' },
    { value: 'mp4', label: 'Videos' },
    { value: 'mp3', label: 'Audio' },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <FolderOpen className="h-5 w-5 text-gray-500" />
            <h2 className="text-lg font-semibold text-gray-900">Files</h2>
            <span className="text-sm text-gray-500">({files.length} files)</span>
          </div>
          
          <div className="flex items-center space-x-2">
            {/* View Mode Toggle */}
            <div className="flex rounded-md shadow-sm">
              <button
                onClick={() => setViewMode('grid')}
                className={`px-3 py-2 text-sm font-medium rounded-l-md border ${
                  viewMode === 'grid'
                    ? 'bg-blue-50 text-blue-700 border-blue-200'
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                }`}
              >
                <Grid className="h-4 w-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`px-3 py-2 text-sm font-medium rounded-r-md border-t border-r border-b ${
                  viewMode === 'list'
                    ? 'bg-blue-50 text-blue-700 border-blue-200'
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                }`}
              >
                <List className="h-4 w-4" />
              </button>
            </div>

            {/* Upload Button */}
            {allowUpload && (
              <button
                onClick={() => setShowUpload(!showUpload)}
                className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700"
              >
                Upload Files
              </button>
            )}
          </div>
        </div>

        {/* Filters and Search */}
        <div className="flex items-center space-x-4">
          <div className="flex-1 max-w-lg">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search files..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          <select
            value={fileTypeFilter}
            onChange={(e) => setFileTypeFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          >
            {fileTypes.map(type => (
              <option key={type.value} value={type.value}>{type.label}</option>
            ))}
          </select>

          <select
            value={`${sortBy}:${sortOrder}`}
            onChange={(e) => {
              const [field, order] = e.target.value.split(':');
              setSortBy(field);
              setSortOrder(order as 'asc' | 'desc');
            }}
            className="px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="uploaded_at:desc">Newest First</option>
            <option value="uploaded_at:asc">Oldest First</option>
            <option value="filename:asc">Name A-Z</option>
            <option value="filename:desc">Name Z-A</option>
            <option value="size:desc">Largest First</option>
            <option value="size:asc">Smallest First</option>
          </select>
        </div>
      </div>

      {/* Upload Area */}
      {showUpload && (
        <div className="p-4 border-b border-gray-200 bg-gray-50">
          <FileUploadComponent
            onUploadComplete={handleUploadComplete}
            projectId={projectId}
            taskId={taskId}
            allowMultiple={true}
          />
        </div>
      )}

      {/* Files Display */}
      <div className="p-4">
        {files.length === 0 ? (
          <div className="text-center py-12">
            <FolderOpen className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-4 text-lg font-medium text-gray-900">No files found</h3>
            <p className="mt-2 text-sm text-gray-500">
              {searchTerm ? 'Try adjusting your search terms.' : 'Upload some files to get started.'}
            </p>
          </div>
        ) : (
          <>
            {viewMode === 'grid' ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {files.map(file => (
                  <div
                    key={file.id}
                    onClick={() => handleFileClick(file)}
                    onContextMenu={(e) => handleContextMenu(e, file)}
                    className={`
                      relative group p-4 border rounded-lg cursor-pointer transition-all
                      ${selectedFiles.has(file.id)
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300 hover:shadow-md'
                      }
                    `}
                  >
                    <div className="flex flex-col items-center text-center space-y-2">
                      {file.is_image ? (
                        <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center overflow-hidden">
                          <img
                            src={fileApiService.getThumbnailUrl(file.id, 'medium')}
                            alt={file.original_filename}
                            className="w-full h-full object-cover"
                            onError={(e) => {
                              e.currentTarget.style.display = 'none';
                              e.currentTarget.parentElement!.innerHTML = `<div class="text-gray-400">${getFileIcon(file, 'h-8 w-8').props.children}</div>`;
                            }}
                          />
                        </div>
                      ) : (
                        <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center">
                          {getFileIcon(file, 'h-8 w-8')}
                        </div>
                      )}
                      
                      <div className="w-full">
                        <p className="text-sm font-medium text-gray-900 truncate" title={file.original_filename}>
                          {file.original_filename}
                        </p>
                        <p className="text-xs text-gray-500">{file.human_readable_size}</p>
                        <p className="text-xs text-gray-500">{formatDate(file.uploaded_at)}</p>
                      </div>
                    </div>

                    {/* Quick Actions */}
                    <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleContextMenu(e, file);
                        }}
                        className="p-1 bg-white rounded-md shadow-sm border border-gray-200 hover:bg-gray-50"
                      >
                        <MoreVertical className="h-4 w-4 text-gray-500" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-2">
                {files.map(file => (
                  <div
                    key={file.id}
                    onClick={() => handleFileClick(file)}
                    onContextMenu={(e) => handleContextMenu(e, file)}
                    className={`
                      flex items-center p-3 rounded-lg cursor-pointer transition-all
                      ${selectedFiles.has(file.id)
                        ? 'bg-blue-50 border border-blue-200'
                        : 'hover:bg-gray-50'
                      }
                    `}
                  >
                    <div className="flex-shrink-0 mr-3">
                      {getFileIcon(file)}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {file.original_filename}
                      </p>
                      <div className="flex items-center space-x-4 text-xs text-gray-500">
                        <span>{file.human_readable_size}</span>
                        <span>{formatDate(file.uploaded_at)}</span>
                        <div className="flex items-center">
                          <User className="h-3 w-3 mr-1" />
                          <span>User {file.uploaded_by}</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-1">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDownload(file);
                        }}
                        className="p-2 text-gray-400 hover:text-gray-600"
                        title="Download"
                      >
                        <Download className="h-4 w-4" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleShare(file);
                        }}
                        className="p-2 text-gray-400 hover:text-gray-600"
                        title="Share"
                      >
                        <Share2 className="h-4 w-4" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(file);
                        }}
                        className="p-2 text-gray-400 hover:text-red-600"
                        title="Delete"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between mt-6">
                <button
                  onClick={() => loadFiles(currentPage - 1)}
                  disabled={currentPage <= 1}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                
                <span className="text-sm text-gray-700">
                  Page {currentPage} of {totalPages}
                </span>
                
                <button
                  onClick={() => loadFiles(currentPage + 1)}
                  disabled={currentPage >= totalPages}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>

      {/* Context Menu */}
      {contextMenu && (
        <div
          className="fixed z-50 bg-white border border-gray-200 rounded-lg shadow-lg py-2"
          style={{ left: contextMenu.x, top: contextMenu.y }}
          onMouseLeave={() => setContextMenu(null)}
        >
          <button
            onClick={() => {
              const file = files.find(f => f.id === contextMenu.fileId);
              if (file) handleDownload(file);
              setContextMenu(null);
            }}
            className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center"
          >
            <Download className="h-4 w-4 mr-2" />
            Download
          </button>
          <button
            onClick={() => {
              const file = files.find(f => f.id === contextMenu.fileId);
              if (file) handleShare(file);
              setContextMenu(null);
            }}
            className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center"
          >
            <Share2 className="h-4 w-4 mr-2" />
            Share
          </button>
          <hr className="my-1" />
          <button
            onClick={() => {
              const file = files.find(f => f.id === contextMenu.fileId);
              if (file) handleDelete(file);
              setContextMenu(null);
            }}
            className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 flex items-center"
          >
            <Trash2 className="h-4 w-4 mr-2" />
            Delete
          </button>
        </div>
      )}
    </div>
  );
};

export default FileBrowser;