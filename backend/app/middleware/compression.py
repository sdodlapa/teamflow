"""
Response compression middleware for improved API performance.

This middleware provides intelligent compression for API responses to reduce
bandwidth usage and improve response times for clients.
"""

import gzip
import brotli
import zlib
from typing import Callable, List, Optional
from fastapi import Request, Response
from fastapi.responses import StreamingResponse
import io

from app.core.config import settings


class CompressionMiddleware:
    """
    Middleware for compressing HTTP responses based on client capabilities
    and content characteristics.
    """
    
    def __init__(
        self,
        app: Callable,
        minimum_size: int = None,
        compression_level: int = None,
        exclude_media_types: List[str] = None,
        exclude_paths: List[str] = None
    ):
        """
        Initialize compression middleware.
        
        Args:
            app: ASGI application
            minimum_size: Minimum response size to compress (bytes)
            compression_level: Compression level (1-9)
            exclude_media_types: Media types to exclude from compression
            exclude_paths: URL paths to exclude from compression
        """
        self.app = app
        self.minimum_size = minimum_size or getattr(settings, 'COMPRESSION_MIN_SIZE', 1000)
        self.compression_level = compression_level or getattr(settings, 'COMPRESSION_LEVEL', 6)
        
        # Default media types that shouldn't be compressed (already compressed)
        self.exclude_media_types = exclude_media_types or [
            'image/jpeg', 'image/png', 'image/gif', 'image/webp',
            'video/mp4', 'video/avi', 'video/mov',
            'audio/mp3', 'audio/wav', 'audio/ogg',
            'application/zip', 'application/gzip', 'application/x-rar',
            'application/pdf'  # Usually already compressed
        ]
        
        # Paths to exclude from compression
        self.exclude_paths = exclude_paths or [
            '/health',
            '/metrics',
            '/static'
        ]
        
        # Supported compression algorithms in order of preference
        self.compression_methods = {
            'br': self._compress_brotli,      # Brotli (best compression)
            'gzip': self._compress_gzip,      # Gzip (widely supported)
            'deflate': self._compress_deflate  # Deflate (basic)
        }
    
    async def __call__(self, scope, receive, send):
        """ASGI middleware implementation."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        # Check if path should be excluded
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            await self.app(scope, receive, send)
            return
        
        # Determine best compression method
        accept_encoding = request.headers.get("accept-encoding", "")
        compression_method = self._select_compression_method(accept_encoding)
        
        if not compression_method:
            await self.app(scope, receive, send)
            return
        
        # Intercept response
        response_data = io.BytesIO()
        response_headers = {}
        response_status = 200
        
        async def send_wrapper(message):
            nonlocal response_data, response_headers, response_status
            
            if message["type"] == "http.response.start":
                response_status = message["status"]
                response_headers = dict(message["headers"])
                
                # Check if response should be compressed
                content_type = response_headers.get(b"content-type", b"").decode().split(";")[0]
                if content_type in self.exclude_media_types:
                    await send(message)
                    return
                
                # Don't send headers yet, wait for body
                return
                
            elif message["type"] == "http.response.body":
                body = message.get("body", b"")
                response_data.write(body)
                
                if not message.get("more_body", False):
                    # End of response, compress if needed
                    full_body = response_data.getvalue()
                    
                    if len(full_body) >= self.minimum_size and self._should_compress(full_body, response_headers):
                        compressed_body, encoding = await self._compress_response(
                            full_body, compression_method
                        )
                        
                        if compressed_body and len(compressed_body) < len(full_body):
                            # Compression was beneficial
                            response_headers[b"content-encoding"] = encoding.encode()
                            response_headers[b"content-length"] = str(len(compressed_body)).encode()
                            
                            # Remove vary header conflicts
                            if b"vary" not in response_headers:
                                response_headers[b"vary"] = b"Accept-Encoding"
                            
                            # Send compressed response
                            await send({
                                "type": "http.response.start",
                                "status": response_status,
                                "headers": list(response_headers.items())
                            })
                            
                            await send({
                                "type": "http.response.body",
                                "body": compressed_body
                            })
                            return
                    
                    # Send uncompressed response
                    await send({
                        "type": "http.response.start",
                        "status": response_status,
                        "headers": list(response_headers.items())
                    })
                    
                    await send({
                        "type": "http.response.body",
                        "body": full_body
                    })
        
        await self.app(scope, receive, send_wrapper)
    
    def _select_compression_method(self, accept_encoding: str) -> Optional[str]:
        """Select the best compression method based on client capabilities."""
        accept_encoding = accept_encoding.lower()
        
        # Check compression methods in order of preference
        for method in self.compression_methods.keys():
            if method in accept_encoding:
                return method
        
        return None
    
    def _should_compress(self, body: bytes, headers: dict) -> bool:
        """Determine if response should be compressed."""
        # Check content type
        content_type = headers.get(b"content-type", b"").decode().split(";")[0]
        
        # Skip already compressed content
        if content_type in self.exclude_media_types:
            return False
        
        # Skip if already encoded
        if b"content-encoding" in headers:
            return False
        
        # Check if content looks like text/JSON (compressible)
        compressible_types = [
            "text/", "application/json", "application/xml", 
            "application/javascript", "application/css"
        ]
        
        return any(content_type.startswith(ctype) for ctype in compressible_types)
    
    async def _compress_response(self, body: bytes, method: str) -> tuple[Optional[bytes], str]:
        """Compress response body using specified method."""
        try:
            compress_func = self.compression_methods.get(method)
            if compress_func:
                compressed = compress_func(body)
                return compressed, method
        except Exception as e:
            print(f"Compression error with {method}: {e}")
        
        return None, ""
    
    def _compress_gzip(self, data: bytes) -> bytes:
        """Compress data using gzip."""
        return gzip.compress(data, compresslevel=self.compression_level)
    
    def _compress_brotli(self, data: bytes) -> bytes:
        """Compress data using brotli."""
        return brotli.compress(data, quality=self.compression_level)
    
    def _compress_deflate(self, data: bytes) -> bytes:
        """Compress data using deflate."""
        return zlib.compress(data, level=self.compression_level)


class SmartCompressionMiddleware:
    """
    Advanced compression middleware with intelligent compression decisions
    based on content analysis and performance metrics.
    """
    
    def __init__(self, app: Callable):
        self.app = app
        self.compression_stats = {
            'total_requests': 0,
            'compressed_requests': 0,
            'bytes_saved': 0,
            'compression_time': 0
        }
    
    async def __call__(self, scope, receive, send):
        """ASGI middleware with smart compression logic."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        self.compression_stats['total_requests'] += 1
        
        # Skip compression for specific endpoints
        if self._should_skip_compression(request):
            await self.app(scope, receive, send)
            return
        
        # Determine compression strategy
        strategy = self._select_compression_strategy(request)
        
        if not strategy:
            await self.app(scope, receive, send)
            return
        
        # Apply compression with performance tracking
        import time
        start_time = time.time()
        
        response_data = io.BytesIO()
        response_headers = {}
        response_status = 200
        
        async def send_wrapper(message):
            nonlocal response_data, response_headers, response_status
            
            if message["type"] == "http.response.start":
                response_status = message["status"]
                response_headers = dict(message["headers"])
                return
                
            elif message["type"] == "http.response.body":
                body = message.get("body", b"")
                response_data.write(body)
                
                if not message.get("more_body", False):
                    # Compress response
                    original_body = response_data.getvalue()
                    compressed_body = await self._apply_compression_strategy(
                        original_body, strategy, response_headers
                    )
                    
                    # Update statistics
                    compression_time = time.time() - start_time
                    self.compression_stats['compression_time'] += compression_time
                    
                    if compressed_body and len(compressed_body) < len(original_body):
                        self.compression_stats['compressed_requests'] += 1
                        self.compression_stats['bytes_saved'] += len(original_body) - len(compressed_body)
                        
                        # Send compressed response
                        response_headers[b"content-encoding"] = strategy['encoding'].encode()
                        response_headers[b"content-length"] = str(len(compressed_body)).encode()
                        response_headers[b"x-compression-ratio"] = f"{len(compressed_body)/len(original_body):.2f}".encode()
                        
                        await send({
                            "type": "http.response.start",
                            "status": response_status,
                            "headers": list(response_headers.items())
                        })
                        
                        await send({
                            "type": "http.response.body",
                            "body": compressed_body
                        })
                    else:
                        # Send original response
                        await send({
                            "type": "http.response.start",
                            "status": response_status,
                            "headers": list(response_headers.items())
                        })
                        
                        await send({
                            "type": "http.response.body",
                            "body": original_body
                        })
        
        await self.app(scope, receive, send_wrapper)
    
    def _should_skip_compression(self, request: Request) -> bool:
        """Determine if compression should be skipped for this request."""
        # Skip for health checks and metrics
        skip_paths = ['/health', '/metrics', '/static']
        if any(request.url.path.startswith(path) for path in skip_paths):
            return True
        
        # Skip for WebSocket upgrades
        if request.headers.get("upgrade") == "websocket":
            return True
        
        # Skip for already compressed content requests
        accept_encoding = request.headers.get("accept-encoding", "")
        if not accept_encoding:
            return True
        
        return False
    
    def _select_compression_strategy(self, request: Request) -> Optional[dict]:
        """Select optimal compression strategy based on request characteristics."""
        accept_encoding = request.headers.get("accept-encoding", "").lower()
        user_agent = request.headers.get("user-agent", "").lower()
        
        # Analyze client capabilities
        strategies = []
        
        if "br" in accept_encoding and "chrome" in user_agent:
            # Modern browsers prefer Brotli
            strategies.append({
                'method': 'brotli',
                'encoding': 'br',
                'level': 6,
                'priority': 3
            })
        
        if "gzip" in accept_encoding:
            # Universal gzip support
            strategies.append({
                'method': 'gzip',
                'encoding': 'gzip',
                'level': 6,
                'priority': 2
            })
        
        if "deflate" in accept_encoding:
            # Basic deflate support
            strategies.append({
                'method': 'deflate',
                'encoding': 'deflate',
                'level': 6,
                'priority': 1
            })
        
        # Return highest priority strategy
        return max(strategies, key=lambda x: x['priority']) if strategies else None
    
    async def _apply_compression_strategy(self, body: bytes, strategy: dict, headers: dict) -> Optional[bytes]:
        """Apply selected compression strategy to response body."""
        # Check minimum size threshold
        if len(body) < getattr(settings, 'COMPRESSION_MIN_SIZE', 1000):
            return None
        
        # Check content type
        content_type = headers.get(b"content-type", b"").decode().split(";")[0]
        compressible_types = [
            "text/", "application/json", "application/xml",
            "application/javascript", "application/css"
        ]
        
        if not any(content_type.startswith(ctype) for ctype in compressible_types):
            return None
        
        try:
            method = strategy['method']
            level = strategy['level']
            
            if method == 'gzip':
                return gzip.compress(body, compresslevel=level)
            elif method == 'brotli':
                return brotli.compress(body, quality=level)
            elif method == 'deflate':
                return zlib.compress(body, level=level)
        
        except Exception as e:
            print(f"Compression failed with {method}: {e}")
        
        return None
    
    def get_compression_stats(self) -> dict:
        """Get compression statistics."""
        total = self.compression_stats['total_requests']
        compressed = self.compression_stats['compressed_requests']
        
        return {
            'total_requests': total,
            'compressed_requests': compressed,
            'compression_ratio': (compressed / total * 100) if total > 0 else 0,
            'bytes_saved': self.compression_stats['bytes_saved'],
            'average_compression_time': (
                self.compression_stats['compression_time'] / compressed
            ) if compressed > 0 else 0
        }


# Convenience function to add compression middleware
def add_compression_middleware(app, compression_type: str = "smart"):
    """
    Add compression middleware to FastAPI application.
    
    Args:
        app: FastAPI application instance
        compression_type: Type of compression ("basic" or "smart")
    """
    if not getattr(settings, 'ENABLE_RESPONSE_COMPRESSION', True):
        return app
    
    if compression_type == "smart":
        app.add_middleware(SmartCompressionMiddleware)
    else:
        app.add_middleware(CompressionMiddleware)
    
    return app


# Export components
__all__ = [
    'CompressionMiddleware',
    'SmartCompressionMiddleware', 
    'add_compression_middleware'
]