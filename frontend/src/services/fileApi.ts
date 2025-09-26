/**
 * File Management API Service
 * Day 19 Implementation - File Management Restoration
 */

import { apiClient } from '../utils/apiClient';

export interface FileUpload {
  id: number;
  filename: string;
  original_filename: string;
  file_size: number;
  human_readable_size: string;
  file_type: string;
  mime_type: string;
  visibility: string;
  description?: string;
  project_id?: number;
  task_id?: number;
  organization_id: number;
  uploaded_by: number;
  uploaded_at: string;
  is_image: boolean;
  is_document: boolean;
  image_width?: number;
  image_height?: number;
  is_processed: boolean;
  processing_status?: string;
  scan_status: string;
}

export interface FileUploadRequest {
  file: File;
  description?: string;
  visibility?: 'public' | 'private' | 'restricted';
  project_id?: number;
  task_id?: number;
}

export interface FileListResponse {
  files: FileUpload[];
  total_count: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface FileSearchRequest {
  filename?: string;
  file_type?: string[];
  project_id?: number;
  task_id?: number;
  uploaded_by?: number;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface FileShareRequest {
  password?: string;
  expires_in_hours?: number;
  max_downloads?: number;
  allow_preview?: boolean;
  allow_download?: boolean;
  require_login?: boolean;
}

export interface FileShareResponse {
  id: number;
  share_token: string;
  share_url: string;
  has_password: boolean;
  max_downloads?: number;
  current_downloads: number;
  allow_preview: boolean;
  allow_download: boolean;
  require_login: boolean;
  created_at: string;
  expires_at?: string;
  is_active: boolean;
  last_accessed?: string;
  file_id: number;
  filename: string;
  file_size: number;
}

export interface FileStatsResponse {
  total_files: number;
  total_size_bytes: number;
  total_size_readable: string;
  files_by_type: Record<string, number>;
  size_by_type: Record<string, number>;
  files_by_project: Record<string, number>;
  recent_uploads: number;
  recent_downloads: number;
  storage_quota_bytes?: number;
  storage_used_percentage?: number;
}

export interface BulkFileActionRequest {
  file_ids: number[];
  action: 'delete' | 'archive' | 'change_visibility' | 'move_project';
  new_visibility?: 'public' | 'private' | 'restricted';
  target_project_id?: number;
}

export interface BulkFileActionResponse {
  total_processed: number;
  successful: number;
  failed: number;
  errors: Array<{ file_id: number; error: string }>;
}

class FileApiService {
  private baseUrl = '/api/v1/files';

  /**
   * Upload a new file
   */
  async uploadFile(request: FileUploadRequest): Promise<FileUpload> {
    const formData = new FormData();
    formData.append('file', request.file);
    
    if (request.description) {
      formData.append('description', request.description);
    }
    if (request.visibility) {
      formData.append('visibility', request.visibility);
    }
    if (request.project_id) {
      formData.append('project_id', request.project_id.toString());
    }
    if (request.task_id) {
      formData.append('task_id', request.task_id.toString());
    }

    const response = await apiClient.upload<FileUpload>(`${this.baseUrl}/upload`, formData);
    return response.data;
  }

  /**
   * Upload file with progress tracking
   */
  async uploadFileWithProgress(
    request: FileUploadRequest,
    onProgress?: (progress: number) => void
  ): Promise<FileUpload> {
    const formData = new FormData();
    formData.append('file', request.file);
    
    if (request.description) {
      formData.append('description', request.description);
    }
    if (request.visibility) {
      formData.append('visibility', request.visibility);
    }
    if (request.project_id) {
      formData.append('project_id', request.project_id.toString());
    }
    if (request.task_id) {
      formData.append('task_id', request.task_id.toString());
    }

    // Use XMLHttpRequest for progress tracking
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable && onProgress) {
          const progress = (e.loaded / e.total) * 100;
          onProgress(progress);
        }
      });

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response = JSON.parse(xhr.responseText);
            resolve(response);
          } catch (e) {
            reject(new Error('Invalid JSON response'));
          }
        } else {
          reject(new Error(`Upload failed: ${xhr.statusText}`));
        }
      });

      xhr.addEventListener('error', () => {
        reject(new Error('Upload failed'));
      });

      // Set authorization header
      const token = localStorage.getItem('access_token');
      if (token) {
        xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      }

      xhr.open('POST', `${this.baseUrl}/upload`);
      xhr.send(formData);
    });
  }

  /**
   * List files with optional filtering
   */
  async listFiles(searchRequest: FileSearchRequest = {}): Promise<FileListResponse> {
    const params = new URLSearchParams();
    
    if (searchRequest.filename) params.append('filename', searchRequest.filename);
    if (searchRequest.file_type) {
      searchRequest.file_type.forEach(type => params.append('file_type', type));
    }
    if (searchRequest.project_id) params.append('project_id', searchRequest.project_id.toString());
    if (searchRequest.task_id) params.append('task_id', searchRequest.task_id.toString());
    if (searchRequest.uploaded_by) params.append('uploaded_by', searchRequest.uploaded_by.toString());
    if (searchRequest.page) params.append('page', searchRequest.page.toString());
    if (searchRequest.page_size) params.append('page_size', searchRequest.page_size.toString());
    if (searchRequest.sort_by) params.append('sort_by', searchRequest.sort_by);
    if (searchRequest.sort_order) params.append('sort_order', searchRequest.sort_order);

    const response = await apiClient.get<FileListResponse>(`${this.baseUrl}/?${params.toString()}`);
    return response.data;
  }

  /**
   * Get detailed file information
   */
  async getFileDetails(fileId: number): Promise<FileUpload> {
    const response = await apiClient.get<FileUpload>(`${this.baseUrl}/${fileId}`);
    return response.data;
  }

  /**
   * Download a file
   */
  async downloadFile(fileId: number, filename?: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/${fileId}/download`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    });

    if (!response.ok) {
      throw new Error('Download failed');
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename || `file_${fileId}`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }

  /**
   * Get file URL for direct access
   */
  getFileUrl(fileId: number): string {
    const token = localStorage.getItem('access_token');
    return `${this.baseUrl}/${fileId}?token=${token}`;
  }

  /**
   * Get file thumbnail
   */
  getThumbnailUrl(fileId: number, size: 'small' | 'medium' | 'large' | 'preview' = 'medium'): string {
    const token = localStorage.getItem('access_token');
    return `${this.baseUrl}/${fileId}/thumbnail/${size}?token=${token}`;
  }

  /**
   * Delete a file
   */
  async deleteFile(fileId: number): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/${fileId}`);
  }

  /**
   * Create a shareable link for a file
   */
  async createFileShare(fileId: number, shareRequest: FileShareRequest): Promise<FileShareResponse> {
    const response = await apiClient.post<FileShareResponse>(`${this.baseUrl}/${fileId}/share`, shareRequest);
    return response.data;
  }

  /**
   * Perform bulk actions on multiple files
   */
  async bulkFileAction(request: BulkFileActionRequest): Promise<BulkFileActionResponse> {
    const response = await apiClient.post<BulkFileActionResponse>(`${this.baseUrl}/bulk-action`, request);
    return response.data;
  }

  /**
   * Get file statistics
   */
  async getFileStatistics(projectId?: number): Promise<FileStatsResponse> {
    const params = new URLSearchParams();
    if (projectId) {
      params.append('project_id', projectId.toString());
    }

    const response = await apiClient.get<FileStatsResponse>(`${this.baseUrl}/statistics?${params.toString()}`);
    return response.data;
  }

  /**
   * Validate file before upload
   */
  validateFile(file: File): { isValid: boolean; error?: string } {
    // File size validation (100MB max)
    const maxSize = 100 * 1024 * 1024; // 100MB
    if (file.size > maxSize) {
      return {
        isValid: false,
        error: `File size (${(file.size / (1024 * 1024)).toFixed(1)}MB) exceeds maximum allowed size (100MB)`
      };
    }

    // File type validation
    const allowedTypes = [
      // Documents
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain',
      'application/rtf',
      // Images
      'image/jpeg',
      'image/jpg',
      'image/png',
      'image/gif',
      'image/svg+xml',
      'image/webp',
      // Spreadsheets
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'text/csv',
      // Presentations
      'application/vnd.ms-powerpoint',
      'application/vnd.openxmlformats-officedocument.presentationml.presentation',
      // Archives
      'application/zip',
      'application/x-rar-compressed',
      'application/x-tar',
      'application/gzip',
      // Media
      'video/mp4',
      'video/x-msvideo',
      'video/quicktime',
      'audio/mpeg',
      'audio/wav',
    ];

    if (!allowedTypes.includes(file.type)) {
      return {
        isValid: false,
        error: `File type '${file.type}' is not allowed`
      };
    }

    return { isValid: true };
  }

  /**
   * Format file size to human readable string
   */
  formatFileSize(bytes: number): string {
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round((bytes / Math.pow(1024, i)) * 100) / 100 + ' ' + sizes[i];
  }
}

export const fileApiService = new FileApiService();
export default fileApiService;