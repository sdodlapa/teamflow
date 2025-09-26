#!/usr/bin/env python3
"""
Create test user for template system testing
"""
import asyncio
import sys
import os
import uuid
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append('/Users/sanjeevadodlapati/Downloads/Repos/teamflow/backend')

from app.core.database import get_async_session_maker
from app.models.user import User
from app.models.organization import Organization
from app.core.security import get_password_hash
from sqlalchemy import text

async def create_test_user():
    """Create a test user for template system testing"""
    try:
        async_session_maker = get_async_session_maker()
        async with async_session_maker() as db:
            # Check if test user already exists
            result = await db.execute(text("SELECT * FROM users WHERE email = 'template@test.com'"))
            existing_user = result.fetchone()
            
            if existing_user:
                print("✅ Test user already exists:")
                print(f"   Email: template@test.com")
                print(f"   ID: {existing_user[0]}")  # assuming id is first column
                return str(existing_user[0])  # Convert to string for consistency
            
            # Create test user
            # Note: Using auto-increment id for users table
            hashed_password = get_password_hash("template123")
            
            # Insert user directly with SQL to avoid model issues
            await db.execute(text("""
                INSERT INTO users (email, first_name, last_name, hashed_password, role, status, is_verified, created_at, updated_at)
                VALUES (:email, :first_name, :last_name, :hashed_password, :role, :status, :is_verified, :created_at, :updated_at)
            """), {
                'email': 'template@test.com',
                'first_name': 'Template',
                'last_name': 'Tester',
                'hashed_password': hashed_password,
                'role': 'admin',
                'status': 'active',
                'is_verified': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            })
            
            await db.commit()
            
            # Get the created user's ID
            result = await db.execute(text("SELECT id FROM users WHERE email = 'template@test.com'"))
            user_record = result.fetchone()
            user_id = user_record[0] if user_record else None
            
            await db.commit()
            
            print("✅ Test user created successfully:")
            print(f"   Email: template@test.com")
            print(f"   Password: template123")
            print(f"   ID: {user_id}")
            print(f"   Role: admin")
            
            return str(user_id)  # Convert to string for consistency
            
    except Exception as e:
        print(f"❌ Failed to create test user: {e}")
        import traceback
        traceback.print_exc()
        return None

async def create_test_organization(user_id):
    """Create a test organization"""
    try:
        async_session_maker = get_async_session_maker()
        async with async_session_maker() as db:
            # Check if test org already exists
            result = await db.execute(text("SELECT * FROM organizations WHERE name = 'Template Test Org'"))
            existing_org = result.fetchone()
            
            if existing_org:
                print("✅ Test organization already exists")
                return existing_org[0]
            
            # Create test organization
            org_id = str(uuid.uuid4())
            
            await db.execute(text("""
                INSERT INTO organizations (id, uuid, name, description, created_at, updated_at)
                VALUES (:id, :uuid, :name, :description, :created_at, :updated_at)
            """), {
                'id': org_id,
                'uuid': org_id,
                'name': 'Template Test Org',
                'description': 'Test organization for template system',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            })
            
            await db.commit()
            
            print("✅ Test organization created:")
            print(f"   Name: Template Test Org")
            print(f"   ID: {org_id}")
            
            return org_id
            
    except Exception as e:
        print(f"❌ Failed to create test organization: {e}")
        return None

async def main():
    """Main setup function"""
    print("🔧 Setting up Template System Authentication")
    print("=" * 50)
    
    # Create test user
    user_id = await create_test_user()
    if not user_id:
        print("❌ Failed to create user, exiting")
        return
    
    # Create test organization
    org_id = await create_test_organization(user_id)
    
    print("\n" + "=" * 50)
    print("🎉 Setup Complete!")
    print("\nTo test template system:")
    print("1. Login: curl -X POST 'http://localhost:8000/api/v1/auth/login/json' \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"email\": \"template@test.com\", \"password\": \"template123\"}'")
    print("2. Use the access_token in Authorization header for template APIs")

if __name__ == "__main__":
    asyncio.run(main())