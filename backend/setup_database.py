#!/usr/bin/env python3
"""
Database setup script - create tables without hanging
"""
import sys
import os
import time
import argparse

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Setup database tables."""
    parser = argparse.ArgumentParser(description="TeamFlow Database Setup")
    parser.add_argument("--reset", action="store_true", help="Drop existing tables before creating new ones")
    parser.add_argument("--sample-data", action="store_true", help="Populate with sample data")
    args = parser.parse_args()
    
    print("🚀 TeamFlow Database Setup")
    print("-" * 50)
    
    # Import here to prevent circular imports
    from app.core.database import ensure_database_ready, drop_tables
    
    # Import models to make sure they're registered
    from app.models import (
        User, Organization, Project, Task, TaskComment, 
        FileUpload, WorkflowDefinition
    )
    
    start_time = time.time()
    
    if args.reset:
        print("🗑️  Dropping existing tables...")
        # Since this is a synchronous script, we can just use sync methods
        try:
            # Use create_sync_engine and drop all tables synchronously
            from app.core.database import create_sync_engine, Base
            sync_engine = create_sync_engine()
            Base.metadata.drop_all(bind=sync_engine)
            print("✅ Tables dropped successfully")
        except Exception as e:
            print(f"⚠️ Error dropping tables: {e}")
            print("Continuing with table creation...")
    
    print("📊 Creating database tables...")
    success = ensure_database_ready()
    
    if success:
        if args.sample_data:
            try:
                print("🔄 Populating sample data...")
                # Import and run the sample data script
                from scripts.populate_sample_data import populate_sample_data
                populate_sample_data()
                print("✅ Sample data created successfully!")
            except Exception as e:
                print(f"⚠️ Error creating sample data: {e}")
                print("✅ Database tables were created but sample data could not be added")
        
        elapsed = time.time() - start_time
        print(f"✅ Database setup completed successfully in {elapsed:.2f} seconds!")
        print("🎉 You can now start the server with:")
        print("   cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return 0
    else:
        print("❌ Database setup failed!")
        print("🔍 Check error messages above for details")
        return 1

if __name__ == "__main__":
    exit(main())