"""
Demo script for testing file management functionality.
Tests file upload, download, sharing, and management operations.
"""

import asyncio
import httpx
import os
from pathlib import Path
from typing import Dict, Any


class FileManagementTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        self.access_token = None
        self.headers = {}
        
    async def authenticate(self, email: str = "admin@teamflow.dev", password: str = "admin123"):
        """Authenticate and get access token."""
        async with httpx.AsyncClient() as client:
            # Login
            response = await client.post(
                f"{self.api_url}/auth/login",
                json={"email": email, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.headers = {"Authorization": f"Bearer {self.access_token}"}
                print("✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.text}")
                return False
    
    async def create_test_file(self, filename: str, content: str) -> str:
        """Create a test file for upload."""
        test_dir = Path("./test_files")
        test_dir.mkdir(exist_ok=True)
        
        file_path = test_dir / filename
        with open(file_path, "w") as f:
            f.write(content)
        
        return str(file_path)
    
    async def test_file_upload(self) -> Dict[str, Any]:
        """Test file upload functionality."""
        print("\n📤 Testing File Upload...")
        
        # Create test file
        test_content = "This is a test document for TeamFlow file management.\n\nFeatures tested:\n- File upload\n- Security validation\n- Metadata extraction"
        test_file_path = await self.create_test_file("test_document.txt", test_content)
        
        async with httpx.AsyncClient() as client:
            # Upload file
            with open(test_file_path, "rb") as f:
                files = {"file": ("test_document.txt", f, "text/plain")}
                data = {
                    "description": "Test document for file management demo",
                    "visibility": "public"
                }
                
                response = await client.post(
                    f"{self.api_url}/files/upload",
                    headers=self.headers,
                    files=files,
                    data=data
                )
            
            if response.status_code == 200:
                file_data = response.json()
                print(f"✅ File uploaded successfully")
                print(f"   File ID: {file_data['id']}")
                print(f"   Filename: {file_data['filename']}")
                print(f"   Size: {file_data['human_readable_size']}")
                print(f"   Type: {file_data['file_type']}")
                return file_data
            else:
                print(f"❌ File upload failed: {response.text}")
                return {}
    
    async def test_file_list(self):
        """Test file listing and search."""
        print("\n📋 Testing File Listing...")
        
        async with httpx.AsyncClient() as client:
            # List all files
            response = await client.get(
                f"{self.api_url}/files/",
                headers=self.headers,
                params={"page": 1, "page_size": 10}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ File list retrieved successfully")
                print(f"   Total files: {data['total_count']}")
                print(f"   Files on page: {len(data['files'])}")
                
                for file in data['files'][:3]:  # Show first 3 files
                    print(f"   - {file['original_filename']} ({file['human_readable_size']})")
                
                return data
            else:
                print(f"❌ File list failed: {response.text}")
                return {}
    
    async def test_file_details(self, file_id: int):
        """Test getting detailed file information."""
        print(f"\n🔍 Testing File Details (ID: {file_id})...")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/files/{file_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                file_data = response.json()
                print(f"✅ File details retrieved successfully")
                print(f"   Original filename: {file_data['original_filename']}")
                print(f"   Upload date: {file_data['uploaded_at']}")
                print(f"   Description: {file_data.get('description', 'No description')}")
                print(f"   Downloads: {file_data.get('download_count', 0)}")
                print(f"   Scan status: {file_data['scan_status']}")
                return file_data
            else:
                print(f"❌ File details failed: {response.text}")
                return {}
    
    async def test_file_download(self, file_id: int):
        """Test file download."""
        print(f"\n⬇️ Testing File Download (ID: {file_id})...")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/files/{file_id}/download",
                headers=self.headers
            )
            
            if response.status_code == 200:
                content = response.content
                print(f"✅ File downloaded successfully")
                print(f"   Content length: {len(content)} bytes")
                print(f"   Content type: {response.headers.get('content-type')}")
                return content
            else:
                print(f"❌ File download failed: {response.text}")
                return None
    
    async def test_file_sharing(self, file_id: int):
        """Test file sharing functionality."""
        print(f"\n🔗 Testing File Sharing (ID: {file_id})...")
        
        async with httpx.AsyncClient() as client:
            # Create share link
            share_data = {
                "expires_in_hours": 24,
                "max_downloads": 10,
                "allow_preview": True,
                "allow_download": True,
                "require_login": False
            }
            
            response = await client.post(
                f"{self.api_url}/files/{file_id}/share",
                headers=self.headers,
                json=share_data
            )
            
            if response.status_code == 200:
                share_info = response.json()
                print(f"✅ Share link created successfully")
                print(f"   Share token: {share_info['share_token']}")
                print(f"   Share URL: {share_info['share_url']}")
                print(f"   Expires: {share_info['expires_at']}")
                print(f"   Max downloads: {share_info['max_downloads']}")
                
                # Test accessing shared file
                await self.test_shared_file_access(share_info['share_token'])
                
                return share_info
            else:
                print(f"❌ File sharing failed: {response.text}")
                return {}
    
    async def test_shared_file_access(self, share_token: str):
        """Test accessing a shared file."""
        print(f"\n🌐 Testing Shared File Access...")
        
        async with httpx.AsyncClient() as client:
            # Access shared file (no authentication required)
            response = await client.get(
                f"{self.api_url}/files/shared/{share_token}",
                params={"action": "preview"}
            )
            
            if response.status_code == 200:
                print(f"✅ Shared file accessed successfully")
                print(f"   Content type: {response.headers.get('content-type')}")
                print(f"   Content length: {len(response.content)} bytes")
            else:
                print(f"❌ Shared file access failed: {response.text}")
    
    async def test_file_search(self):
        """Test file search functionality."""
        print("\n🔍 Testing File Search...")
        
        async with httpx.AsyncClient() as client:
            # Search for text files
            response = await client.get(
                f"{self.api_url}/files/",
                headers=self.headers,
                params={
                    "file_type": ["txt"],
                    "sort_by": "uploaded_at",
                    "sort_order": "desc"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ File search completed successfully")
                print(f"   Found {data['total_count']} text files")
                
                for file in data['files'][:2]:  # Show first 2 results
                    print(f"   - {file['original_filename']} (uploaded: {file['uploaded_at'][:10]})")
                
                return data
            else:
                print(f"❌ File search failed: {response.text}")
                return {}
    
    async def test_file_statistics(self):
        """Test file statistics."""
        print("\n📊 Testing File Statistics...")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/files/statistics",
                headers=self.headers
            )
            
            if response.status_code == 200:
                stats = response.json()
                print(f"✅ File statistics retrieved successfully")
                print(f"   Total files: {stats['total_files']}")
                print(f"   Total storage: {stats['total_size_readable']}")
                print(f"   Recent uploads (7d): {stats['recent_uploads']}")
                print(f"   Recent downloads (7d): {stats['recent_downloads']}")
                
                if stats['files_by_type']:
                    print(f"   Files by type:")
                    for file_type, count in stats['files_by_type'].items():
                        print(f"     - {file_type}: {count}")
                
                return stats
            else:
                print(f"❌ File statistics failed: {response.text}")
                return {}
    
    async def cleanup_test_files(self):
        """Clean up test files."""
        try:
            import shutil
            test_dir = Path("./test_files")
            if test_dir.exists():
                shutil.rmtree(test_dir)
                print("\n🧹 Test files cleaned up")
        except Exception as e:
            print(f"⚠️ Failed to clean up test files: {e}")
    
    async def run_demo(self):
        """Run the complete file management demo."""
        print("🚀 Starting TeamFlow File Management Demo")
        print("=" * 50)
        
        # Authenticate
        if not await self.authenticate():
            print("❌ Demo failed - could not authenticate")
            return
        
        try:
            # Test file upload
            uploaded_file = await self.test_file_upload()
            if not uploaded_file:
                print("❌ Demo failed - could not upload file")
                return
            
            file_id = uploaded_file['id']
            
            # Test file operations
            await self.test_file_list()
            await self.test_file_details(file_id)
            await self.test_file_download(file_id)
            await self.test_file_sharing(file_id)
            await self.test_file_search()
            await self.test_file_statistics()
            
            print("\n" + "=" * 50)
            print("✅ File Management Demo completed successfully!")
            print("\nFeatures demonstrated:")
            print("• Secure file upload with validation")
            print("• File listing with pagination and filters")
            print("• Detailed file information retrieval")
            print("• Secure file download with access logging")
            print("• File sharing with configurable permissions")
            print("• Public shared file access")
            print("• Advanced file search and filtering")
            print("• Comprehensive file usage statistics")
            
        except Exception as e:
            print(f"\n❌ Demo failed with error: {e}")
        
        finally:
            # Cleanup
            await self.cleanup_test_files()


async def main():
    """Main demo function."""
    tester = FileManagementTester()
    await tester.run_demo()


if __name__ == "__main__":
    asyncio.run(main())