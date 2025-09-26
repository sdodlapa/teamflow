#!/usr/bin/env python3
"""
Create test template for end-to-end testing
"""
import asyncio
import sys
import json
import uuid
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append('/Users/sanjeevadodlapati/Downloads/Repos/teamflow/backend')

from app.core.database import get_async_session_maker
from sqlalchemy import text

async def create_test_template():
    """Create a test template for testing"""
    try:
        async_session_maker = get_async_session_maker()
        async with async_session_maker() as db:
            
            # Create a sample domain config
            domain_config = {
                "name": "e_commerce_test",
                "title": "E-Commerce Test Platform",
                "description": "Test e-commerce platform with basic entities",
                "domain_type": "e_commerce",
                "version": "1.0.0",
                "logo": "🛒",
                "color_scheme": "blue",
                "theme": "default"
            }
            
            # Create sample entities
            entities = [
                {
                    "name": "product",
                    "title": "Product",
                    "description": "Product entity with basic fields",
                    "fields": [
                        {"name": "name", "title": "Name", "type": "string", "required": True},
                        {"name": "price", "title": "Price", "type": "decimal", "required": True},
                        {"name": "description", "title": "Description", "type": "text", "required": False}
                    ]
                }
            ]
            
            # Create sample relationships
            relationships = []
            
            # Insert template
            template_id = str(uuid.uuid4())
            await db.execute(text("""
                INSERT INTO templates (uuid, name, description, domain_config, entities, relationships, 
                                     version, status, tags, is_public, is_active, user_id, 
                                     created_at, updated_at)
                VALUES (:uuid, :name, :description, :domain_config, :entities, :relationships,
                        :version, :status, :tags, :is_public, :is_active, :user_id,
                        :created_at, :updated_at)
            """), {
                'uuid': template_id,
                'name': 'Test E-Commerce Template',
                'description': 'A test template for e-commerce platform',
                'domain_config': json.dumps(domain_config),
                'entities': json.dumps(entities),
                'relationships': json.dumps(relationships),
                'version': 1,
                'status': 'published',
                'tags': json.dumps(['test', 'e-commerce', 'demo']),
                'is_public': True,
                'is_active': True,
                'user_id': '7',  # The test user we created
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            })
            
            await db.commit()
            
            print("✅ Test template created successfully:")
            print(f"   Name: Test E-Commerce Template")
            print(f"   ID: {template_id}")
            print(f"   Status: published")
            print(f"   User ID: 7")
            print(f"   Public: True")
            
            return template_id
            
    except Exception as e:
        print(f"❌ Failed to create test template: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    """Main function"""
    print("🔧 Creating Test Template")
    print("=" * 30)
    
    template_id = await create_test_template()
    
    print("\n" + "=" * 30)
    if template_id:
        print("🎉 Template created successfully!")
        print("\nTo test:")
        print("1. Test endpoint: curl http://localhost:8000/api/v1/templates/test")
        print("2. Should now show 1 template found")
    else:
        print("❌ Template creation failed")

if __name__ == "__main__":
    asyncio.run(main())