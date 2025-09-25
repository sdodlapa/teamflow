"""
Database migration utilities for optimized auth service.
"""

import logging
import argparse
from typing import List, Dict, Any, Optional

from app.services.optimized_auth import OptimizedAuthService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("auth_migration")


def run_auth_diagnostics():
    """Run authentication service diagnostics."""
    auth_service = OptimizedAuthService()
    
    try:
        # Test database connection
        conn = auth_service.get_connection()
        logger.info("✅ Database connection successful")
        
        # Check users table existence and structure
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        if not columns:
            logger.error("❌ Users table not found in database")
            return False
        
        column_names = [col[1] for col in columns]
        required_columns = [
            "id", "email", "hashed_password", "is_verified", 
            "first_name", "last_name", "role", "status"
        ]
        
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            logger.error(f"❌ Missing required columns in users table: {missing_columns}")
            return False
        
        logger.info("✅ Users table structure verification successful")
        
        # Check for user count
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        logger.info(f"✅ Found {user_count} users in database")
        
        # Check indexes on email (critical for auth performance)
        cursor.execute("PRAGMA index_list(users)")
        indexes = cursor.fetchall()
        
        email_index_exists = False
        for idx in indexes:
            index_name = idx[1]
            cursor.execute(f"PRAGMA index_info({index_name})")
            index_columns = cursor.fetchall()
            
            if any(col[2] == "email" for col in index_columns):
                email_index_exists = True
                logger.info(f"✅ Found index on email column: {index_name}")
        
        if not email_index_exists:
            logger.warning("⚠️ No index found on email column. This will cause slow lookups.")
            logger.info("Creating index on email column...")
            
            try:
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
                conn.commit()
                logger.info("✅ Successfully created index on email column")
            except Exception as e:
                logger.error(f"❌ Failed to create index: {e}")
                return False
        
        # Test sample user lookup
        if user_count > 0:
            cursor.execute("SELECT email FROM users LIMIT 1")
            sample_email = cursor.fetchone()[0]
            
            logger.info(f"Testing user lookup with sample email: {sample_email}")
            user = auth_service.get_user_by_email(sample_email)
            
            if user:
                logger.info(f"✅ Successfully retrieved sample user: {user['first_name']} {user['last_name']}")
            else:
                logger.error("❌ Failed to retrieve sample user")
                return False
        
        auth_service.close_connection(conn)
        logger.info("✅ Authentication service diagnostics completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Auth diagnostics failed: {e}")
        return False


def compare_auth_performance(sample_size: int = 5):
    """
    Compare performance between standard SQLAlchemy and optimized direct auth.
    """
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    from app.core.config import settings
    import time
    
    # Create direct connection for standard SQLAlchemy operations
    engine = create_engine(settings.DATABASE_URL.replace("sqlite+aiosqlite", "sqlite"))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    # Get optimized auth service
    auth_service = OptimizedAuthService()
    
    # Get sample emails
    try:
        result = db.execute(text("SELECT email FROM users LIMIT :limit"), {"limit": sample_size})
        emails = [row[0] for row in result]
        
        if not emails:
            logger.error("No users found for performance comparison")
            return
        
        results = {
            "standard": [],
            "optimized": []
        }
        
        logger.info(f"Running performance comparison with {len(emails)} users...")
        
        # Test standard SQLAlchemy performance
        for email in emails:
            start_time = time.time()
            result = db.execute(
                text("SELECT id, email, hashed_password, is_verified, first_name, last_name FROM users WHERE email = :email"),
                {"email": email}
            )
            user = result.fetchone()
            duration_ms = (time.time() - start_time) * 1000
            results["standard"].append(duration_ms)
            logger.info(f"Standard lookup for {email}: {duration_ms:.2f}ms")
        
        # Test optimized direct SQLite performance
        for email in emails:
            start_time = time.time()
            user = auth_service.get_user_by_email(email)
            duration_ms = (time.time() - start_time) * 1000
            results["optimized"].append(duration_ms)
            logger.info(f"Optimized lookup for {email}: {duration_ms:.2f}ms")
        
        # Calculate averages
        std_avg = sum(results["standard"]) / len(results["standard"]) if results["standard"] else 0
        opt_avg = sum(results["optimized"]) / len(results["optimized"]) if results["optimized"] else 0
        
        improvement = ((std_avg - opt_avg) / std_avg * 100) if std_avg > 0 else 0
        
        logger.info("=== Performance Comparison Results ===")
        logger.info(f"Standard SQLAlchemy: {std_avg:.2f}ms average")
        logger.info(f"Optimized Direct SQLite: {opt_avg:.2f}ms average")
        logger.info(f"Improvement: {improvement:.1f}%")
        
        if improvement > 20:
            logger.info(
                "RECOMMENDATION: The optimized auth service shows significant "
                "performance improvements. Consider using it for authentication."
            )
        else:
            logger.info(
                "RECOMMENDATION: No significant performance difference detected. "
                "Either method should be suitable."
            )
        
    except Exception as e:
        logger.error(f"Error during performance comparison: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Authentication Service Utilities")
    parser.add_argument("--diagnose", action="store_true", help="Run auth service diagnostics")
    parser.add_argument("--compare", action="store_true", help="Compare auth performance")
    parser.add_argument("--sample", type=int, default=5, help="Sample size for performance comparison")
    
    args = parser.parse_args()
    
    if args.diagnose:
        run_auth_diagnostics()
    
    if args.compare:
        compare_auth_performance(args.sample)
    
    if not args.diagnose and not args.compare:
        logger.info("No action specified. Use --diagnose or --compare")