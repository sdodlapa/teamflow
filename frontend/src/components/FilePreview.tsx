/**
 * File Preview Component - Day 19 Implementation
 * Preview component for different file types with modal display
 */

import React, { useState, useEffect } from 'react';
import {
  X,
  Download,
  Share2,
  Maximize2,
  Minimize2,
  ZoomIn,
  ZoomOut,
  RotateCw,
  FileText,
  File,
  Play,
  Pause,
  Volume2,
  AlertCircle
} from 'lucide-react';
import { fileApiService, FileUpload } from '../services/fileApi';

export interface FilePreviewProps {
  file: FileUpload | null;
  isOpen: boolean;
  onClose: () => void;
  onDownload?: (file: FileUpload) => void;
  onShare?: (file: FileUpload) => void;
  className?: string;
}

const FilePreview: React.FC<FilePreviewProps> = ({
  file,
  isOpen,
  onClose,
  onDownload,
  onShare,
  className = ''
}) => {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [imageZoom, setImageZoom] = useState(100);
  const [imageRotation, setImageRotation] = useState(0);
  const [audioPlaying, setAudioPlaying] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [previewError, setPreviewError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (file && isOpen) {
      loadPreview();
    }
    return () => {
      if (previewUrl && previewUrl.startsWith('blob:')) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [file, isOpen]);

  const loadPreview = async () => {
    if (!file) return;
    
    try {
      setLoading(true);
      setPreviewError(null);
      
      if (file.is_image || file.file_type.includes('pdf')) {
        // Use thumbnail URL for images, direct URL for PDFs
        const url = file.is_image 
          ? fileApiService.getThumbnailUrl(file.id, 'large')
          : fileApiService.getFileUrl(file.id);
        setPreviewUrl(url);
      } else if (file.file_type.includes('text') || file.file_type.includes('json') || file.file_type.includes('xml')) {
        // For text files, fetch content
        try {
          const response = await fetch(fileApiService.getFileUrl(file.id));
          const text = await response.text();
          setPreviewUrl(`data:text/plain;charset=utf-8,${encodeURIComponent(text)}`);
        } catch (error) {
          setPreviewError('Unable to load text content');
        }
      } else if (file.file_type.includes('video') || file.file_type.includes('audio')) {
        // For media files, use direct URL
        setPreviewUrl(fileApiService.getFileUrl(file.id));
      } else {
        setPreviewError('Preview not available for this file type');
      }
    } catch (error) {
      setPreviewError('Failed to load preview');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (file && onDownload) {
      onDownload(file);
    }
  };

  const handleShare = () => {
    if (file && onShare) {
      onShare(file);
    }
  };

  const resetImageView = () => {
    setImageZoom(100);
    setImageRotation(0);
  };

  const getFileIcon = (file: FileUpload, size = 'h-16 w-16') => {
    if (file.is_document) return <FileText className={`${size} text-orange-500`} />;
    return <File className={`${size} text-gray-500`} />;
  };

  const renderPreviewContent = () => {
    if (!file) return null;

    if (loading) {
      return (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">Loading preview...</span>
        </div>
      );
    }

    if (previewError) {
      return (
        <div className="flex flex-col items-center justify-center h-64 text-center">
          <AlertCircle className="h-12 w-12 text-gray-400 mb-4" />
          <p className="text-gray-600 mb-2">{previewError}</p>
          <p className="text-sm text-gray-500">
            You can still download the file to view it locally.
          </p>
        </div>
      );
    }

    // Image Preview
    if (file.is_image && previewUrl) {
      return (
        <div className="relative">
          <div className="flex justify-center items-center mb-4 space-x-2">
            <button
              onClick={() => setImageZoom(Math.max(25, imageZoom - 25))}
              className="p-2 bg-gray-100 hover:bg-gray-200 rounded-md"
              title="Zoom Out"
            >
              <ZoomOut className="h-4 w-4" />
            </button>
            <span className="text-sm text-gray-600 px-2">{imageZoom}%</span>
            <button
              onClick={() => setImageZoom(Math.min(400, imageZoom + 25))}
              className="p-2 bg-gray-100 hover:bg-gray-200 rounded-md"
              title="Zoom In"
            >
              <ZoomIn className="h-4 w-4" />
            </button>
            <button
              onClick={() => setImageRotation((imageRotation + 90) % 360)}
              className="p-2 bg-gray-100 hover:bg-gray-200 rounded-md"
              title="Rotate"
            >
              <RotateCw className="h-4 w-4" />
            </button>
            <button
              onClick={resetImageView}
              className="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-md text-sm"
            >
              Reset
            </button>
          </div>
          <div className="flex justify-center overflow-auto max-h-96">
            <img
              src={previewUrl}
              alt={file.original_filename}
              style={{
                transform: `scale(${imageZoom / 100}) rotate(${imageRotation}deg)`,
                transition: 'transform 0.2s'
              }}
              className="max-w-full h-auto"
              onError={() => setPreviewError('Failed to load image')}
            />
          </div>
        </div>
      );
    }

    // Video Preview
    if (file.file_type.includes('video') && previewUrl) {
      return (
        <div className="flex justify-center">
          <video
            src={previewUrl}
            controls
            className="max-w-full max-h-96"
            onError={() => setPreviewError('Unable to play video')}
          >
            Your browser does not support video playback.
          </video>
        </div>
      );
    }

    // Audio Preview
    if (file.file_type.includes('audio') && previewUrl) {
      return (
        <div className="flex flex-col items-center space-y-4 py-8">
          <div className="w-24 h-24 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full flex items-center justify-center">
            <Volume2 className="h-8 w-8 text-blue-600" />
          </div>
          <h3 className="text-lg font-medium text-gray-900">{file.original_filename}</h3>
          <audio
            src={previewUrl}
            controls
            className="w-full max-w-md"
            onPlay={() => setAudioPlaying(true)}
            onPause={() => setAudioPlaying(false)}
            onError={() => setPreviewError('Unable to play audio')}
          />
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            {audioPlaying ? (
              <Play className="h-4 w-4" />
            ) : (
              <Pause className="h-4 w-4" />
            )}
            <span>Audio Player</span>
          </div>
        </div>
      );
    }

    // PDF Preview
    if (file.file_type.includes('pdf') && previewUrl) {
      return (
        <div className="flex justify-center">
          <iframe
            src={previewUrl}
            className="w-full h-96 border rounded-md"
            title={file.original_filename}
            onError={() => setPreviewError('Unable to display PDF')}
          />
        </div>
      );
    }

    // Text File Preview
    if ((file.file_type.includes('text') || file.file_type.includes('json') || file.file_type.includes('xml')) && previewUrl) {
      return (
        <div className="bg-gray-50 rounded-md p-4 max-h-96 overflow-auto">
          <iframe
            src={previewUrl}
            className="w-full h-80 border-none"
            title={file.original_filename}
            onError={() => setPreviewError('Unable to display text content')}
          />
        </div>
      );
    }

    // Generic File Preview
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        {getFileIcon(file)}
        <h3 className="mt-4 text-lg font-medium text-gray-900">{file.original_filename}</h3>
        <p className="mt-2 text-sm text-gray-500">{file.file_type}</p>
        <p className="text-sm text-gray-500">{file.human_readable_size}</p>
        <p className="mt-4 text-sm text-gray-600">
          Preview not available for this file type.
        </p>
      </div>
    );
  };

  if (!isOpen || !file) {
    return null;
  }

  return (
    <div className={`fixed inset-0 z-50 overflow-y-auto ${className}`}>
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center">
        <div 
          className="fixed inset-0 bg-black opacity-50 transition-opacity"
          onClick={onClose}
        />
        
        <div
          className={`
            relative bg-white rounded-lg shadow-xl transform transition-all
            ${isFullscreen 
              ? 'w-full h-full max-w-none max-h-none m-0' 
              : 'w-full max-w-4xl max-h-screen m-4'
            }
          `}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <h2 className="text-lg font-medium text-gray-900 truncate">
                {file.original_filename}
              </h2>
              <span className="text-sm text-gray-500">
                ({file.human_readable_size})
              </span>
            </div>
            
            <div className="flex items-center space-x-2">
              {onDownload && (
                <button
                  onClick={handleDownload}
                  className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md"
                  title="Download"
                >
                  <Download className="h-5 w-5" />
                </button>
              )}
              
              {onShare && (
                <button
                  onClick={handleShare}
                  className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md"
                  title="Share"
                >
                  <Share2 className="h-5 w-5" />
                </button>
              )}
              
              <button
                onClick={() => setIsFullscreen(!isFullscreen)}
                className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md"
                title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}
              >
                {isFullscreen ? (
                  <Minimize2 className="h-5 w-5" />
                ) : (
                  <Maximize2 className="h-5 w-5" />
                )}
              </button>
              
              <button
                onClick={onClose}
                className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md"
                title="Close"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="p-4 overflow-auto" style={{ maxHeight: isFullscreen ? 'calc(100vh - 80px)' : '70vh' }}>
            {renderPreviewContent()}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between p-4 border-t border-gray-200 bg-gray-50">
            <div className="text-sm text-gray-600">
              <span className="font-medium">Type:</span> {file.file_type}
              <span className="mx-2">•</span>
              <span className="font-medium">Uploaded:</span> {new Date(file.uploaded_at).toLocaleString()}
            </div>
            
            <div className="flex items-center space-x-2">
              <span className="text-xs text-gray-500">
                Press ESC to close
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FilePreview;