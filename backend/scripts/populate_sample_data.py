#!/usr/bin/env python3
"""
Sample data population script for TeamFlow
Creates test users, organizations, projects, and tasks
"""

import asyncio
import datetime
import uuid

from app.core.database import get_async_session
from app.core.security import get_password_hash
from app.models.organization import Organization, OrganizationMember, OrganizationMemberRole, OrganizationPlan
from app.models.project import Project, ProjectMember, ProjectMemberRole, ProjectPriority, ProjectStatus
from app.models.task import Task, TaskPriority, TaskStatus
from app.models.user import User, UserRole

async def _create_sample_data():
    """Create sample data for testing and development"""
    
    print("🔹 Creating sample data...")
    
    async with get_async_session() as session:
        # Create users
        print("🔹 Creating users...")
        admin_user = User(
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            hashed_password=get_password_hash("admin123"),
            is_verified=True,
            role=UserRole.ADMIN,
            bio="System administrator",
        )
        
        test_user = User(
            email="user@example.com",
            first_name="Test",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_verified=True,
            role=UserRole.USER,
            bio="Regular user account",
        )
        
        dev_user = User(
            email="dev@example.com",
            first_name="Developer",
            last_name="User",
            hashed_password=get_password_hash("dev123"),
            is_verified=True,
            role=UserRole.USER,
            bio="Developer account",
        )
        
        manager_user = User(
            email="manager@example.com",
            first_name="Manager",
            last_name="User",
            hashed_password=get_password_hash("manager123"),
            is_verified=True,
            role=UserRole.USER,
            bio="Manager account",
        )
        
        session.add_all([admin_user, test_user, dev_user, manager_user])
        await session.flush()
        
        # Create organization
        print("🔹 Creating organizations...")
        org1 = Organization(
            name="Acme Corporation",
            description="A global technology company",
            plan=OrganizationPlan.ENTERPRISE,
            is_active=True,
            website="https://acme.example.com",
        )
        
        org2 = Organization(
            name="Startup Inc.",
            description="An innovative startup",
            plan=OrganizationPlan.FREE,
            is_active=True,
            website="https://startup.example.com",
        )
        
        session.add_all([org1, org2])
        await session.flush()
        
        # Create organization members
        print("🔹 Creating organization members...")
        org1_admin = OrganizationMember(
            user_id=admin_user.id,
            organization_id=org1.id,
            role=OrganizationMemberRole.OWNER,
        )
        
        org1_user = OrganizationMember(
            user_id=test_user.id,
            organization_id=org1.id,
            role=OrganizationMemberRole.MEMBER,
        )
        
        org1_dev = OrganizationMember(
            user_id=dev_user.id,
            organization_id=org1.id,
            role=OrganizationMemberRole.ADMIN,
        )
        
        org1_manager = OrganizationMember(
            user_id=manager_user.id,
            organization_id=org1.id,
            role=OrganizationMemberRole.ADMIN,
        )
        
        org2_owner = OrganizationMember(
            user_id=test_user.id,
            organization_id=org2.id,
            role=OrganizationMemberRole.OWNER,
        )
        
        org2_member = OrganizationMember(
            user_id=dev_user.id,
            organization_id=org2.id,
            role=OrganizationMemberRole.MEMBER,
        )
        
        session.add_all([
            org1_admin, org1_user, org1_dev, org1_manager,
            org2_owner, org2_member
        ])
        await session.flush()
        
        # Create projects
        print("🔹 Creating projects...")
        project1 = Project(
            name="Website Redesign",
            description="Redesign the company website",
            organization_id=org1.id,
            status=ProjectStatus.ACTIVE,
            priority=ProjectPriority.HIGH,
            start_date=datetime.datetime.now(),
            end_date=datetime.datetime.now() + datetime.timedelta(days=30),
        )
        
        project2 = Project(
            name="Mobile App Development",
            description="Develop a new mobile app",
            organization_id=org1.id,
            status=ProjectStatus.ACTIVE,
            priority=ProjectPriority.MEDIUM,
            start_date=datetime.datetime.now(),
            end_date=datetime.datetime.now() + datetime.timedelta(days=60),
        )
        
        project3 = Project(
            name="MVP Development",
            description="Develop minimum viable product",
            organization_id=org2.id,
            status=ProjectStatus.ACTIVE,
            priority=ProjectPriority.HIGH,
            start_date=datetime.datetime.now(),
            end_date=datetime.datetime.now() + datetime.timedelta(days=45),
        )
        
        session.add_all([project1, project2, project3])
        await session.flush()
        
        # Create project members
        print("🔹 Creating project members...")
        # Project 1 members
        pm1_manager = ProjectMember(
            user_id=manager_user.id,
            project_id=project1.id,
            role=ProjectMemberRole.OWNER,
        )
        
        pm1_dev = ProjectMember(
            user_id=dev_user.id,
            project_id=project1.id,
            role=ProjectMemberRole.DEVELOPER,
        )
        
        pm1_user = ProjectMember(
            user_id=test_user.id,
            project_id=project1.id,
            role=ProjectMemberRole.VIEWER,
        )
        
        # Project 2 members
        pm2_manager = ProjectMember(
            user_id=manager_user.id,
            project_id=project2.id,
            role=ProjectMemberRole.OWNER,
        )
        
        pm2_dev = ProjectMember(
            user_id=dev_user.id,
            project_id=project2.id,
            role=ProjectMemberRole.DEVELOPER,
        )
        
        # Project 3 members
        pm3_owner = ProjectMember(
            user_id=test_user.id,
            project_id=project3.id,
            role=ProjectMemberRole.OWNER,
        )
        
        pm3_dev = ProjectMember(
            user_id=dev_user.id,
            project_id=project3.id,
            role=ProjectMemberRole.DEVELOPER,
        )
        
        session.add_all([
            pm1_manager, pm1_dev, pm1_user,
            pm2_manager, pm2_dev,
            pm3_owner, pm3_dev
        ])
        await session.flush()
        
        # Create tasks
        print("🔹 Creating tasks...")
        # Project 1 tasks
        tasks = [
            Task(
                title="Design mockups",
                description="Create design mockups for the website",
                project_id=project1.id,
                status=TaskStatus.IN_PROGRESS,
                priority=TaskPriority.HIGH,
                assignee_id=dev_user.id,
                created_by=manager_user.id,
                due_date=datetime.datetime.now() + datetime.timedelta(days=5),
                estimated_hours=8,
            ),
            Task(
                title="Frontend implementation",
                description="Implement the frontend based on designs",
                project_id=project1.id,
                status=TaskStatus.TODO,
                priority=TaskPriority.MEDIUM,
                assignee_id=dev_user.id,
                created_by=manager_user.id,
                due_date=datetime.datetime.now() + datetime.timedelta(days=10),
                estimated_hours=16,
            ),
            Task(
                title="Backend integration",
                description="Integrate frontend with backend APIs",
                project_id=project1.id,
                status=TaskStatus.TODO,
                priority=TaskPriority.MEDIUM,
                assignee_id=dev_user.id,
                created_by=manager_user.id,
                due_date=datetime.datetime.now() + datetime.timedelta(days=15),
                estimated_hours=12,
            ),
            Task(
                title="QA and testing",
                description="Test the website for bugs and issues",
                project_id=project1.id,
                status=TaskStatus.TODO,
                priority=TaskPriority.MEDIUM,
                assignee_id=test_user.id,
                created_by=manager_user.id,
                due_date=datetime.datetime.now() + datetime.timedelta(days=20),
                estimated_hours=8,
            ),
            Task(
                title="Deployment",
                description="Deploy the website to production",
                project_id=project1.id,
                status=TaskStatus.TODO,
                priority=TaskPriority.HIGH,
                assignee_id=manager_user.id,
                created_by=manager_user.id,
                due_date=datetime.datetime.now() + datetime.timedelta(days=25),
                estimated_hours=4,
            ),
            # Project 2 tasks
            Task(
                title="App wireframes",
                description="Create wireframes for the mobile app",
                project_id=project2.id,
                status=TaskStatus.DONE,
                priority=TaskPriority.HIGH,
                assignee_id=dev_user.id,
                created_by=manager_user.id,
                due_date=datetime.datetime.now() - datetime.timedelta(days=5),
                estimated_hours=8,
                actual_hours=10,
            ),
            Task(
                title="UI design",
                description="Design the UI for the mobile app",
                project_id=project2.id,
                status=TaskStatus.IN_PROGRESS,
                priority=TaskPriority.HIGH,
                assignee_id=dev_user.id,
                created_by=manager_user.id,
                due_date=datetime.datetime.now() + datetime.timedelta(days=5),
                estimated_hours=16,
            ),
            Task(
                title="Frontend development",
                description="Develop the mobile app frontend",
                project_id=project2.id,
                status=TaskStatus.TODO,
                priority=TaskPriority.MEDIUM,
                assignee_id=dev_user.id,
                created_by=manager_user.id,
                due_date=datetime.datetime.now() + datetime.timedelta(days=20),
                estimated_hours=40,
            ),
            # Project 3 tasks
            Task(
                title="Market research",
                description="Conduct market research for the MVP",
                project_id=project3.id,
                assignee_id=dev_user.id,
                created_by=test_user.id,
                status=TaskStatus.DONE,
                priority=TaskPriority.MEDIUM,
                estimated_hours=16,
                actual_hours=14,
            ),
            Task(
                title="MVP features",
                description="Define MVP features and scope",
                project_id=project3.id,
                assignee_id=test_user.id,
                created_by=test_user.id,
                status=TaskStatus.DONE,
                priority=TaskPriority.MEDIUM,
                estimated_hours=8,
                actual_hours=6,
            ),
            Task(
                title="Core functionality",
                description="Implement core functionality for MVP",
                project_id=project3.id,
                status=TaskStatus.IN_PROGRESS,
                priority=TaskPriority.HIGH,
                assignee_id=dev_user.id,
                created_by=test_user.id,
                due_date=datetime.datetime.now() + datetime.timedelta(days=10),
                estimated_hours=24,
            ),
        ]
        
        session.add_all(tasks)
        await session.commit()
        
        print("✅ Sample data created successfully!")
        return True


def populate_sample_data():
    """Run the async sample data creation function"""
    try:
        asyncio.run(_create_sample_data())
        return True
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return False


if __name__ == "__main__":
    populate_sample_data()