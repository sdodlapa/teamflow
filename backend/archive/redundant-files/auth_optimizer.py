#!/usr/bin/env python3
"""
Optimized Authentication Setup Tool

This script helps diagnose authentication performance issues and migrate
to the optimized authentication service.

Usage:
  python auth_optimizer.py --diagnose  # Run diagnostics on the auth system
  python auth_optimizer.py --compare   # Compare standard and optimized auth performance
  python auth_optimizer.py --help      # Show help
"""

import sys
import os
import logging
import argparse

# Add the parent directory to the Python path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("auth_optimizer")


def main():
    """Main entry point for the auth optimizer tool."""
    parser = argparse.ArgumentParser(
        description="Authentication Optimization Tool"
    )
    
    parser.add_argument(
        "--diagnose", 
        action="store_true", 
        help="Run diagnostics on the authentication system"
    )
    
    parser.add_argument(
        "--compare", 
        action="store_true", 
        help="Compare standard and optimized authentication performance"
    )
    
    parser.add_argument(
        "--sample", 
        type=int, 
        default=5,
        help="Sample size for performance comparison (default: 5)"
    )
    
    args = parser.parse_args()
    
    if not (args.diagnose or args.compare):
        parser.print_help()
        return
    
    logger.info("Authentication Optimization Tool")
    logger.info("--------------------------------")
    
    try:
        from app.services.auth_migration import run_auth_diagnostics, compare_auth_performance
        
        if args.diagnose:
            logger.info("Running authentication diagnostics...")
            success = run_auth_diagnostics()
            
            if success:
                logger.info("✅ Authentication system is properly configured.")
            else:
                logger.error("❌ Authentication system has issues. Please check the logs above.")
        
        if args.compare:
            logger.info(f"Comparing authentication performance (sample size: {args.sample})...")
            compare_auth_performance(args.sample)
    
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        logger.error("Please make sure you're running this script from the root directory of the project.")
        return
    
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return


if __name__ == "__main__":
    main()