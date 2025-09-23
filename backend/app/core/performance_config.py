"""
Advanced performance configuration and tuning system
"""
import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

from app.core.config import settings


@dataclass
class DatabasePerformanceConfig:
    """Database performance configuration"""
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600
    query_timeout: int = 30
    slow_query_threshold_ms: float = 100.0
    enable_query_logging: bool = True
    enable_connection_pooling: bool = True
    
    
@dataclass 
class CachePerformanceConfig:
    """Cache performance configuration"""
    redis_pool_size: int = 50
    redis_timeout: int = 5
    default_ttl: int = 300
    max_ttl: int = 3600
    enable_compression: bool = True
    compression_threshold: int = 1024
    hit_ratio_target: float = 80.0
    
    
@dataclass
class APIPerformanceConfig:
    """API performance configuration"""
    default_page_size: int = 20
    max_page_size: int = 100
    request_timeout: int = 30
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    enable_response_compression: bool = True
    compression_min_size: int = 1000
    compression_level: int = 6
    rate_limit_requests: int = 1000
    rate_limit_window: int = 3600
    
    
@dataclass
class CompressionConfig:
    """Response compression configuration"""
    enable_gzip: bool = True
    enable_brotli: bool = True
    enable_deflate: bool = True
    minimum_size: int = 1000
    compression_level: int = 6
    exclude_media_types: list = None
    exclude_paths: list = None
    
    def __post_init__(self):
        if self.exclude_media_types is None:
            self.exclude_media_types = [
                'image/jpeg', 'image/png', 'image/gif', 'image/webp',
                'video/mp4', 'video/avi', 'video/mov',
                'audio/mp3', 'audio/wav', 'audio/ogg',
                'application/zip', 'application/gzip', 'application/x-rar',
                'application/pdf'
            ]
        
        if self.exclude_paths is None:
            self.exclude_paths = ['/health', '/metrics', '/static']


@dataclass
class MonitoringConfig:
    """Performance monitoring configuration"""
    enable_metrics_collection: bool = True
    metrics_retention_minutes: int = 60
    enable_profiling: bool = False
    profiling_sample_rate: float = 0.01
    enable_tracing: bool = True
    trace_sample_rate: float = 0.1
    alert_thresholds: Dict[str, float] = None
    
    def __post_init__(self):
        if self.alert_thresholds is None:
            self.alert_thresholds = {
                'response_time_ms': 1000.0,
                'error_rate_percent': 5.0,
                'memory_usage_percent': 85.0,
                'cpu_usage_percent': 80.0,
                'disk_usage_percent': 90.0
            }


@dataclass
class OptimizationConfig:
    """Automatic optimization configuration"""
    enable_auto_optimization: bool = False
    optimization_interval_minutes: int = 60
    enable_query_optimization: bool = True
    enable_cache_optimization: bool = True
    enable_connection_optimization: bool = True
    safety_mode: bool = True  # Prevents aggressive optimizations
    backup_before_optimization: bool = True


class PerformanceConfigurationManager:
    """Manages performance configuration across the application"""
    
    def __init__(self, config_file_path: Optional[str] = None):
        self.config_file_path = config_file_path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "performance.json"
        )
        
        # Initialize default configurations
        self.database_config = DatabasePerformanceConfig()
        self.cache_config = CachePerformanceConfig()
        self.api_config = APIPerformanceConfig()
        self.compression_config = CompressionConfig()
        self.monitoring_config = MonitoringConfig()
        self.optimization_config = OptimizationConfig()
        
        # Load configuration from file if exists
        self.load_configuration()
    
    def load_configuration(self) -> bool:
        """Load configuration from file"""
        try:
            config_path = Path(self.config_file_path)
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                
                # Update configurations with loaded data
                if 'database' in config_data:
                    self.database_config = DatabasePerformanceConfig(**config_data['database'])
                
                if 'cache' in config_data:
                    self.cache_config = CachePerformanceConfig(**config_data['cache'])
                
                if 'api' in config_data:
                    self.api_config = APIPerformanceConfig(**config_data['api'])
                
                if 'compression' in config_data:
                    self.compression_config = CompressionConfig(**config_data['compression'])
                
                if 'monitoring' in config_data:
                    self.monitoring_config = MonitoringConfig(**config_data['monitoring'])
                
                if 'optimization' in config_data:
                    self.optimization_config = OptimizationConfig(**config_data['optimization'])
                
                print(f"Performance configuration loaded from {self.config_file_path}")
                return True
            
        except Exception as e:
            print(f"Error loading performance configuration: {e}")
        
        return False
    
    def save_configuration(self) -> bool:
        """Save current configuration to file"""
        try:
            config_data = {
                'database': asdict(self.database_config),
                'cache': asdict(self.cache_config),
                'api': asdict(self.api_config),
                'compression': asdict(self.compression_config),
                'monitoring': asdict(self.monitoring_config),
                'optimization': asdict(self.optimization_config)
            }
            
            # Ensure config directory exists
            config_path = Path(self.config_file_path)
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            print(f"Performance configuration saved to {self.config_file_path}")
            return True
            
        except Exception as e:
            print(f"Error saving performance configuration: {e}")
            return False
    
    def update_database_config(self, **kwargs) -> bool:
        """Update database performance configuration"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.database_config, key):
                    setattr(self.database_config, key, value)
            
            return self.save_configuration()
        except Exception as e:
            print(f"Error updating database config: {e}")
            return False
    
    def update_cache_config(self, **kwargs) -> bool:
        """Update cache performance configuration"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.cache_config, key):
                    setattr(self.cache_config, key, value)
            
            return self.save_configuration()
        except Exception as e:
            print(f"Error updating cache config: {e}")
            return False
    
    def update_api_config(self, **kwargs) -> bool:
        """Update API performance configuration"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.api_config, key):
                    setattr(self.api_config, key, value)
            
            return self.save_configuration()
        except Exception as e:
            print(f"Error updating API config: {e}")
            return False
    
    def get_all_configurations(self) -> Dict[str, Any]:
        """Get all performance configurations"""
        return {
            'database': asdict(self.database_config),
            'cache': asdict(self.cache_config),
            'api': asdict(self.api_config),
            'compression': asdict(self.compression_config),
            'monitoring': asdict(self.monitoring_config),
            'optimization': asdict(self.optimization_config)
        }
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate current configuration and return recommendations"""
        validation_results = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'recommendations': []
        }
        
        # Validate database config
        if self.database_config.pool_size > 100:
            validation_results['warnings'].append(
                "Database pool size is very high (>100). Consider reducing for better resource usage."
            )
        
        if self.database_config.slow_query_threshold_ms < 10:
            validation_results['warnings'].append(
                "Slow query threshold is very low (<10ms). This may generate excessive logs."
            )
        
        # Validate cache config
        if self.cache_config.default_ttl > 3600:
            validation_results['recommendations'].append(
                "Consider reducing default cache TTL for more dynamic data updates."
            )
        
        # Validate API config
        if self.api_config.max_page_size > 1000:
            validation_results['warnings'].append(
                "Maximum page size is very high (>1000). This may impact performance."
            )
        
        # Validate compression config
        if not self.compression_config.enable_gzip and not self.compression_config.enable_brotli:
            validation_results['errors'].append(
                "No compression algorithms enabled. Enable at least gzip for better performance."
            )
            validation_results['valid'] = False
        
        # Validate monitoring config
        if not self.monitoring_config.enable_metrics_collection:
            validation_results['recommendations'].append(
                "Enable metrics collection for better performance insights."
            )
        
        return validation_results
    
    def apply_performance_preset(self, preset_name: str) -> bool:
        """Apply predefined performance configuration preset"""
        presets = {
            'development': {
                'database': {
                    'pool_size': 5,
                    'max_overflow': 10,
                    'query_timeout': 60,
                    'enable_query_logging': True
                },
                'cache': {
                    'default_ttl': 60,
                    'enable_compression': False
                },
                'api': {
                    'default_page_size': 10,
                    'max_page_size': 50,
                    'enable_response_compression': False
                },
                'monitoring': {
                    'enable_profiling': True,
                    'profiling_sample_rate': 1.0
                }
            },
            'production': {
                'database': {
                    'pool_size': 20,
                    'max_overflow': 30,
                    'query_timeout': 30,
                    'enable_query_logging': False
                },
                'cache': {
                    'default_ttl': 300,
                    'enable_compression': True
                },
                'api': {
                    'default_page_size': 20,
                    'max_page_size': 100,
                    'enable_response_compression': True
                },
                'monitoring': {
                    'enable_profiling': False,
                    'profiling_sample_rate': 0.01
                }
            },
            'high_performance': {
                'database': {
                    'pool_size': 50,
                    'max_overflow': 100,
                    'query_timeout': 15,
                    'slow_query_threshold_ms': 50.0
                },
                'cache': {
                    'default_ttl': 600,
                    'redis_pool_size': 100,
                    'enable_compression': True
                },
                'api': {
                    'default_page_size': 50,
                    'max_page_size': 200,
                    'enable_response_compression': True,
                    'compression_level': 9
                },
                'optimization': {
                    'enable_auto_optimization': True,
                    'optimization_interval_minutes': 30
                }
            }
        }
        
        if preset_name not in presets:
            print(f"Unknown preset: {preset_name}")
            return False
        
        try:
            preset_config = presets[preset_name]
            
            # Apply database config
            if 'database' in preset_config:
                for key, value in preset_config['database'].items():
                    if hasattr(self.database_config, key):
                        setattr(self.database_config, key, value)
            
            # Apply cache config
            if 'cache' in preset_config:
                for key, value in preset_config['cache'].items():
                    if hasattr(self.cache_config, key):
                        setattr(self.cache_config, key, value)
            
            # Apply API config
            if 'api' in preset_config:
                for key, value in preset_config['api'].items():
                    if hasattr(self.api_config, key):
                        setattr(self.api_config, key, value)
            
            # Apply monitoring config
            if 'monitoring' in preset_config:
                for key, value in preset_config['monitoring'].items():
                    if hasattr(self.monitoring_config, key):
                        setattr(self.monitoring_config, key, value)
            
            # Apply optimization config
            if 'optimization' in preset_config:
                for key, value in preset_config['optimization'].items():
                    if hasattr(self.optimization_config, key):
                        setattr(self.optimization_config, key, value)
            
            self.save_configuration()
            print(f"Applied performance preset: {preset_name}")
            return True
            
        except Exception as e:
            print(f"Error applying preset {preset_name}: {e}")
            return False
    
    def export_configuration(self, export_path: str) -> bool:
        """Export configuration to specified path"""
        try:
            config_data = self.get_all_configurations()
            
            with open(export_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            print(f"Configuration exported to {export_path}")
            return True
            
        except Exception as e:
            print(f"Error exporting configuration: {e}")
            return False
    
    def import_configuration(self, import_path: str) -> bool:
        """Import configuration from specified path"""
        try:
            with open(import_path, 'r') as f:
                config_data = json.load(f)
            
            # Backup current config
            backup_path = f"{self.config_file_path}.backup"
            self.export_configuration(backup_path)
            
            # Apply imported config
            if 'database' in config_data:
                self.database_config = DatabasePerformanceConfig(**config_data['database'])
            
            if 'cache' in config_data:
                self.cache_config = CachePerformanceConfig(**config_data['cache'])
            
            if 'api' in config_data:
                self.api_config = APIPerformanceConfig(**config_data['api'])
            
            if 'compression' in config_data:
                self.compression_config = CompressionConfig(**config_data['compression'])
            
            if 'monitoring' in config_data:
                self.monitoring_config = MonitoringConfig(**config_data['monitoring'])
            
            if 'optimization' in config_data:
                self.optimization_config = OptimizationConfig(**config_data['optimization'])
            
            self.save_configuration()
            print(f"Configuration imported from {import_path}")
            return True
            
        except Exception as e:
            print(f"Error importing configuration: {e}")
            return False


# Global configuration manager instance
performance_config = PerformanceConfigurationManager()


# Export key components
__all__ = [
    'DatabasePerformanceConfig',
    'CachePerformanceConfig', 
    'APIPerformanceConfig',
    'CompressionConfig',
    'MonitoringConfig',
    'OptimizationConfig',
    'PerformanceConfigurationManager',
    'performance_config'
]