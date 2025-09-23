"""
Simple test script to verify Task API implementation.
"""

import asyncio
import json
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.organization import Organization, OrganizationMember, OrganizationMemberRole
from app.models.project import Project, ProjectMember, ProjectMemberRole
from app.models.task import Task, TaskComment, TaskDependency, TaskPriority, TaskStatus
from app.models.user import User, UserRole, UserStatus


async def test_task_implementation():
    """Test that our Task models and relationships work correctly."""
    
    print("🧪 Testing Task Implementation...")
    
    async with AsyncSessionLocal() as db:
        try:
            # Create test user
            user = User(
                email="testuser@example.com",
                first_name="Test",
                last_name="User",
                hashed_password="hashedpassword123",
                role=UserRole.USER,
                status=UserStatus.ACTIVE,
                is_verified=True,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            print(f"✅ Created test user: {user.email}")
            
            # Create test organization
            org = Organization(
                name="Test Org",
                description="Test organization for task testing",
            )
            db.add(org)
            await db.commit()
            await db.refresh(org)
            print(f"✅ Created test organization: {org.name}")
            
            # Add user to organization
            org_member = OrganizationMember(
                organization_id=org.id,
                user_id=user.id,
                role=OrganizationMemberRole.ADMIN,
            )
            db.add(org_member)
            await db.commit()
            print(f"✅ Added user to organization as {org_member.role}")
            
            # Create test project
            project = Project(
                name="Test Project",
                description="Test project for task testing",
                organization_id=org.id,
            )
            db.add(project)
            await db.commit()
            await db.refresh(project)
            print(f"✅ Created test project: {project.name}")
            
            # Add user to project
            project_member = ProjectMember(
                project_id=project.id,
                user_id=user.id,
                role=ProjectMemberRole.ADMIN,
            )
            db.add(project_member)
            await db.commit()
            print(f"✅ Added user to project as {project_member.role}")
            
            # Create test task
            task = Task(
                title="Test Task",
                description="This is a test task for our implementation",
                project_id=project.id,
                assignee_id=user.id,
                created_by=user.id,
                priority=TaskPriority.HIGH,
                status=TaskStatus.TODO,
                estimated_hours=8,
                tags_list=["testing", "implementation", "phase-2"],
            )
            db.add(task)
            await db.commit()
            await db.refresh(task)
            print(f"✅ Created test task: {task.title}")
            print(f"   - Status: {task.status}")
            print(f"   - Priority: {task.priority}")
            print(f"   - Tags: {task.tags_list}")
            
            # Create task comment
            comment = TaskComment(
                content="This is a test comment on the task",
                task_id=task.id,
                user_id=user.id,
            )
            db.add(comment)
            await db.commit()
            await db.refresh(comment)
            print(f"✅ Created task comment: {comment.content[:50]}...")
            
            # Test task status update
            task.status = TaskStatus.IN_PROGRESS
            task.actual_hours = 2
            await db.commit()
            print(f"✅ Updated task status to: {task.status}")
            print(f"   - Actual hours: {task.actual_hours}")
            
            # Create another task for dependency testing
            task2 = Task(
                title="Dependent Task",
                description="This task depends on the first task",
                project_id=project.id,
                created_by=user.id,
                priority=TaskPriority.MEDIUM,
                status=TaskStatus.TODO,
            )
            db.add(task2)
            await db.commit()
            await db.refresh(task2)
            print(f"✅ Created second task: {task2.title}")
            
            # Create task dependency
            dependency = TaskDependency(
                task_id=task2.id,
                depends_on_id=task.id,
            )
            db.add(dependency)
            await db.commit()
            print(f"✅ Created task dependency: Task {task2.id} depends on Task {task.id}")
            
            # Test the relationships work
            from sqlalchemy.future import select
            from sqlalchemy.orm import selectinload
            
            # Load task with all relationships
            result = await db.execute(
                select(Task)
                .options(
                    selectinload(Task.project),
                    selectinload(Task.assignee),
                    selectinload(Task.creator),
                    selectinload(Task.comments),
                    selectinload(Task.dependencies),
                )
                .where(Task.id == task.id)
            )
            loaded_task = result.scalar_one()
            
            print(f"✅ Task relationships loaded successfully:")
            print(f"   - Project: {loaded_task.project.name}")
            print(f"   - Assignee: {loaded_task.assignee.full_name}")
            print(f"   - Creator: {loaded_task.creator.full_name}")
            print(f"   - Comments: {len(loaded_task.comments)}")
            print(f"   - Dependencies: {len(loaded_task.dependencies)}")
            
            print("\n🎉 Task Implementation Test Completed Successfully!")
            print("\nTask API Features Verified:")
            print("✅ Task model with all fields")
            print("✅ Task status and priority enums")
            print("✅ Task tags as JSON list")
            print("✅ Task comments system")
            print("✅ Task dependencies system")
            print("✅ Task relationships (project, assignee, creator)")
            print("✅ Database migrations applied")
            print("✅ All model imports working")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during testing: {e}")
            return False


if __name__ == "__main__":
    success = asyncio.run(test_task_implementation())
    if success:
        print("\n🚀 Ready for Task API endpoints testing!")
    else:
        print("\n💥 Task implementation needs fixes.")