/**
 * File Upload Component - Day 19 Implementati}) => {
  const [uploadProgress, setUploadProgress] = useState<UploadProgress[]>([]);

  const handleFiles = useCallback(async (files: File[]) => { Drag-and-drop file upload with progress indicators and validation
 */

import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { 
  Upload, 
  File, 
  Image as ImageIcon, 
  FileText, 
  Archive, 
  Music, 
  Video,
  X,
  Check,
  AlertCircle,
  Loader2
} from 'lucide-react';
import { fileApiService, FileUploadRequest, FileUpload } from '../services/fileApi';

export interface FileUploadComponentProps {
  onUploadComplete?: (files: FileUpload[]) => void;
  onUploadError?: (error: string) => void;
  maxFiles?: number;
  maxFileSize?: number;
  projectId?: number;
  taskId?: number;
  allowMultiple?: boolean;
  acceptedFileTypes?: string[];
  className?: string;
}

interface UploadProgress {
  file: File;
  progress: number;
  status: 'uploading' | 'complete' | 'error';
  error?: string;
  result?: FileUpload;
}

const FileUploadComponent: React.FC<FileUploadComponentProps> = ({
  onUploadComplete,
  onUploadError,
  maxFiles = 10,
  maxFileSize = 100 * 1024 * 1024, // 100MB
  projectId,
  taskId,
  allowMultiple = true,
  acceptedFileTypes,
  className = ''
}) => {
  const [uploadProgress, setUploadProgress] = useState<UploadProgress[]>([]);

  const handleFiles = useCallback(async (files: FileList) => {
    const filesToUpload = allowMultiple ? Array.from(files) : Array.from(files).slice(0, 1);
    
    // Check if we exceed max files
    if (filesToUpload.length > maxFiles) {
      onUploadError?.(
        `You can only upload a maximum of ${maxFiles} files at once. Selected ${filesToUpload.length} files.`
      );
      return;
    }

    // Initialize progress tracking
    const initialProgress: UploadProgress[] = filesToUpload.map(file => ({
      file,
      progress: 0,
      status: 'uploading' as const
    }));
    
    setUploadProgress(initialProgress);
    const uploadedFiles: FileUpload[] = [];
    
    // Upload files sequentially to avoid overwhelming the server
    for (let i = 0; i < filesToUpload.length; i++) {
      const file = filesToUpload[i];
      
      try {
        // Validate file
        const validation = fileApiService.validateFile(file);
        if (!validation.isValid) {
          setUploadProgress(prev => prev.map((item, index) => 
            index === i ? { ...item, status: 'error', error: validation.error } : item
          ));
          continue;
        }

        const uploadRequest: FileUploadRequest = {
          file,
          project_id: projectId,
          task_id: taskId,
          visibility: 'public'
        };

        const result = await fileApiService.uploadFileWithProgress(
          uploadRequest,
          (progress) => {
            setUploadProgress(prev => prev.map((item, index) => 
              index === i ? { ...item, progress } : item
            ));
          }
        );

        // Mark as complete
        setUploadProgress(prev => prev.map((item, index) => 
          index === i ? { ...item, status: 'complete', progress: 100, result } : item
        ));
        
        uploadedFiles.push(result);
        
      } catch (error) {
        console.error(`Upload failed for ${file.name}:`, error);
        setUploadProgress(prev => prev.map((item, index) => 
          index === i ? { 
            ...item, 
            status: 'error', 
            error: error instanceof Error ? error.message : 'Upload failed'
          } : item
        ));
        
        if (onUploadError) {
          onUploadError(`Failed to upload ${file.name}: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
      }
    }

    // Notify completion
    if (uploadedFiles.length > 0 && onUploadComplete) {
      onUploadComplete(uploadedFiles);
    }
  }, [allowMultiple, maxFiles, projectId, taskId, onUploadComplete, onUploadError]);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    handleFiles(acceptedFiles);
  }, [handleFiles]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: allowMultiple,
    maxFiles,
    maxSize: maxFileSize,
    accept: acceptedFileTypes ? 
      acceptedFileTypes.reduce((acc, type) => ({ ...acc, [type]: [] }), {}) : 
      {
        'image/*': [],
        'application/pdf': [],
        'application/msword': [],
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': [],
        'text/plain': [],
        'application/vnd.ms-excel': [],
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': [],
        'text/csv': [],
        'application/zip': [],
        'video/mp4': [],
        'audio/mp3': []
      }
  });

  const getFileIcon = (file: File) => {
    if (file.type.startsWith('image/')) return <ImageIcon className="h-6 w-6" />;
    if (file.type.startsWith('video/')) return <Video className="h-6 w-6" />;
    if (file.type.startsWith('audio/')) return <Music className="h-6 w-6" />;
    if (file.type.includes('pdf') || file.type.includes('document')) return <FileText className="h-6 w-6" />;
    if (file.type.includes('zip') || file.type.includes('archive')) return <Archive className="h-6 w-6" />;
    return <File className="h-6 w-6" />;
  };

  const getStatusIcon = (status: UploadProgress['status']) => {
    switch (status) {
      case 'uploading':
        return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />;
      case 'complete':
        return <Check className="h-4 w-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return null;
    }
  };

  const clearProgress = () => {
    setUploadProgress([]);
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Upload Area */}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all
          ${isDragActive
            ? 'border-blue-500 bg-blue-50 scale-105'
            : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
          }
        `}
      >
        <input {...getInputProps()} />
        <Upload className={`
          mx-auto h-12 w-12 mb-4 
          ${isDragActive ? 'text-blue-500' : 'text-gray-400'}
        `} />
        
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          {isDragActive ? 'Drop files here' : 'Upload files'}
        </h3>
        
        <p className="text-sm text-gray-600 mb-4">
          {allowMultiple
            ? `Drag and drop files here, or click to select (max ${maxFiles} files)`
            : 'Drag and drop a file here, or click to select'
          }
        </p>
        
        <p className="text-xs text-gray-500">
          Supported formats: PDF, DOC, DOCX, TXT, Images, XLS, XLSX, CSV, ZIP, MP4, MP3
        </p>
        <p className="text-xs text-gray-500">
          Maximum file size: 100MB per file
        </p>
      </div>

      {/* Upload Progress */}
      {uploadProgress.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-sm font-medium text-gray-900">
              Uploading {uploadProgress.length} file{uploadProgress.length > 1 ? 's' : ''}
            </h4>
            <button
              onClick={clearProgress}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
          
          <div className="space-y-3">
            {uploadProgress.map((item, index) => (
              <div key={index} className="flex items-center space-x-3">
                {/* File Icon */}
                <div className="text-gray-500">
                  {getFileIcon(item.file)}
                </div>
                
                {/* File Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {item.file.name}
                    </p>
                    <div className="flex items-center space-x-2">
                      <span className="text-xs text-gray-500">
                        {fileApiService.formatFileSize(item.file.size)}
                      </span>
                      {getStatusIcon(item.status)}
                    </div>
                  </div>
                  
                  {/* Progress Bar */}
                  {item.status === 'uploading' && (
                    <div className="mt-1">
                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <span>Uploading...</span>
                        <span>{Math.round(item.progress)}%</span>
                      </div>
                      <div className="mt-1 w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${item.progress}%` }}
                        />
                      </div>
                    </div>
                  )}
                  
                  {/* Error Message */}
                  {item.status === 'error' && item.error && (
                    <p className="text-xs text-red-600 mt-1">{item.error}</p>
                  )}
                  
                  {/* Success Message */}
                  {item.status === 'complete' && (
                    <p className="text-xs text-green-600 mt-1">Upload complete</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUploadComponent;