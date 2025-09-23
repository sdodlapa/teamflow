"""
Real-time notification service for integrating WebSocket updates with existing APIs.
Automatically triggers WebSocket notifications when data changes occur.
"""
from typing import Dict, Any, Optional, List
import json
import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.task import Task
from app.models.user import User
from app.models.project import Project

# Avoid circular imports - we'll use dynamic imports for WebSocket functions

logger = logging.getLogger(__name__)


class RealTimeNotificationService:
    """Service for triggering real-time notifications via WebSocket."""
    
    @staticmethod
    async def task_created(
        task: Task,
        created_by_user: User,
        db: AsyncSession
    ) -> None:
        """Trigger notifications when a task is created."""
        try:
            from app.core.websocket import connection_manager, MessageType
            
            await connection_manager.broadcast_to_project(
                task.project_id,
                MessageType.TASK_CREATED,
                {
                    "task_id": task.id,
                    "task_title": task.title,
                    "project_id": task.project_id,
                    "created_by": created_by_user.id,
                    "assignee_id": task.assignee_id,
                    "status": task.status,
                    "priority": task.priority,
                    "timestamp": task.created_at.isoformat() if task.created_at else None
                },
                exclude_user=created_by_user.id
            )
            logger.info(f"Real-time notification sent: Task {task.id} created by user {created_by_user.id}")
        except Exception as e:
            logger.error(f"Failed to send task creation notification: {e}")
    
    @staticmethod
    async def task_updated(
        task: Task,
        updated_by_user: User,
        old_values: Dict[str, Any],
        new_values: Dict[str, Any],
        db: AsyncSession
    ) -> None:
        """Trigger notifications when a task is updated."""
        try:
            # Calculate what actually changed
            changes = {}
            for field, new_value in new_values.items():
                old_value = old_values.get(field)
                if old_value != new_value:
                    changes[field] = {
                        "old": old_value,
                        "new": new_value
                    }
            
            if changes:
                await notify_task_updated(task, updated_by_user.id, changes)
                
                # Handle specific change types
                if "status" in changes:
                    await notify_task_status_changed(
                        task,
                        changes["status"]["old"],
                        changes["status"]["new"],
                        updated_by_user.id
                    )
                
                if "assignee_id" in changes:
                    await notify_task_assigned(
                        task,
                        changes["assignee_id"]["old"],
                        changes["assignee_id"]["new"],
                        updated_by_user.id
                    )
                
                logger.info(f"Real-time notification sent: Task {task.id} updated by user {updated_by_user.id}")
        except Exception as e:
            logger.error(f"Failed to send task update notification: {e}")
    
    @staticmethod
    async def comment_created(
        comment_data: Dict[str, Any],
        task: Task,
        user: User,
        db: AsyncSession
    ) -> None:
        """Trigger notifications when a comment is added."""
        try:
            # Enhance comment data with user information
            enhanced_comment_data = {
                **comment_data,
                "user_name": user.full_name
            }
            
            await notify_comment_added(enhanced_comment_data, task)
            logger.info(f"Real-time notification sent: Comment added to task {task.id} by user {user.id}")
        except Exception as e:
            logger.error(f"Failed to send comment notification: {e}")
    
    @staticmethod
    async def mention_created(
        mention_data: Dict[str, Any],
        task: Task,
        mentioned_by_user: User,
        mentioned_user: User,
        db: AsyncSession
    ) -> None:
        """Trigger notifications when a user is mentioned."""
        try:
            # Enhance mention data with user information
            enhanced_mention_data = {
                **mention_data,
                "mentioned_by_name": mentioned_by_user.full_name,
                "mentioned_user_name": mentioned_user.full_name
            }
            
            await notify_mention_created(enhanced_mention_data, task)
            logger.info(f"Real-time notification sent: User {mentioned_user.id} mentioned in task {task.id}")
        except Exception as e:
            logger.error(f"Failed to send mention notification: {e}")
    
    @staticmethod
    async def time_tracking_started(
        time_log_data: Dict[str, Any],
        task: Task,
        user: User,
        db: AsyncSession
    ) -> None:
        """Trigger notifications when time tracking starts."""
        try:
            from app.core.websocket import connection_manager, MessageType
            
            # Enhance time log data with user information
            enhanced_time_log_data = {
                **time_log_data,
                "user_name": user.full_name,
                "task_title": task.title
            }
            
            await connection_manager.broadcast_to_project(
                task.project_id,
                MessageType.TIME_TRACKING_STARTED,
                enhanced_time_log_data,
                exclude_user=user.id
            )
            logger.info(f"Real-time notification sent: Time tracking started for task {task.id} by user {user.id}")
        except Exception as e:
            logger.error(f"Failed to send time tracking start notification: {e}")
    
    @staticmethod
    async def time_tracking_stopped(
        time_log_data: Dict[str, Any],
        task: Task,
        user: User,
        db: AsyncSession
    ) -> None:
        """Trigger notifications when time tracking stops."""
        try:
            # Enhance time log data with user information
            enhanced_time_log_data = {
                **time_log_data,
                "user_name": user.full_name
            }
            
            await notify_time_tracking_stopped(enhanced_time_log_data, task)
            logger.info(f"Real-time notification sent: Time tracking stopped for task {task.id} by user {user.id}")
        except Exception as e:
            logger.error(f"Failed to send time tracking stop notification: {e}")
    
    @staticmethod
    async def project_updated(
        project: Project,
        updated_by_user: User,
        changes: Dict[str, Any],
        db: AsyncSession
    ) -> None:
        """Trigger notifications when a project is updated."""
        try:
            from app.core.websocket import connection_manager, MessageType
            
            await connection_manager.broadcast_to_project(
                project.id,
                MessageType.PROJECT_UPDATED,
                {
                    "project_id": project.id,
                    "project_name": project.name,
                    "updated_by": updated_by_user.id,
                    "updated_by_name": updated_by_user.full_name,
                    "changes": changes,
                    "timestamp": datetime.utcnow().isoformat()
                },
                exclude_user=updated_by_user.id
            )
            
            logger.info(f"Real-time notification sent: Project {project.id} updated by user {updated_by_user.id}")
        except Exception as e:
            logger.error(f"Failed to send project update notification: {e}")
    
    @staticmethod
    async def project_member_added(
        project: Project,
        new_member: User,
        added_by_user: User,
        db: AsyncSession
    ) -> None:
        """Trigger notifications when a member is added to a project."""
        try:
            from app.core.websocket import connection_manager, MessageType
            
            await connection_manager.broadcast_to_project(
                project.id,
                MessageType.PROJECT_MEMBER_ADDED,
                {
                    "project_id": project.id,
                    "project_name": project.name,
                    "new_member_id": new_member.id,
                    "new_member_name": new_member.full_name,
                    "added_by": added_by_user.id,
                    "added_by_name": added_by_user.full_name,
                    "timestamp": datetime.utcnow().isoformat()
                },
                exclude_user=added_by_user.id
            )
            
            # Send direct notification to the new member
            await connection_manager.send_to_user(
                new_member.id,
                MessageType.NOTIFICATION,
                {
                    "type": "project_invitation",
                    "message": f"You have been added to project '{project.name}'",
                    "project_id": project.id,
                    "project_name": project.name,
                    "added_by": added_by_user.full_name,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"Real-time notification sent: User {new_member.id} added to project {project.id}")
        except Exception as e:
            logger.error(f"Failed to send project member addition notification: {e}")
    
    @staticmethod
    async def send_system_notification(
        user_ids: List[int],
        notification_type: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Send system notifications to specific users."""
        try:
            from app.core.websocket import connection_manager, MessageType
            
            notification_data = {
                "type": notification_type,
                "title": title,
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if data:
                notification_data.update(data)
            
            for user_id in user_ids:
                await connection_manager.send_to_user(
                    user_id,
                    MessageType.NOTIFICATION,
                    notification_data
                )
            
            logger.info(f"System notification sent to {len(user_ids)} users: {title}")
        except Exception as e:
            logger.error(f"Failed to send system notification: {e}")
    
    @staticmethod
    async def broadcast_maintenance_notification(
        message: str,
        scheduled_time: Optional[datetime] = None
    ) -> None:
        """Broadcast maintenance notifications to all connected users."""
        try:
            from app.core.websocket import connection_manager, MessageType
            
            notification_data = {
                "type": "maintenance",
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if scheduled_time:
                notification_data["scheduled_time"] = scheduled_time.isoformat()
            
            # Send to all connected users
            for user_id, connections in connection_manager.active_connections.items():
                for connection_id, websocket in connections.items():
                    try:
                        await connection_manager.send_message(
                            websocket,
                            MessageType.NOTIFICATION,
                            notification_data
                        )
                    except Exception as e:
                        logger.error(f"Failed to send maintenance notification to user {user_id}: {e}")
            
            logger.info(f"Maintenance notification broadcasted: {message}")
        except Exception as e:
            logger.error(f"Failed to broadcast maintenance notification: {e}")


# Convenience functions for integration with existing API endpoints

async def trigger_task_created_notification(
    task: Task,
    created_by_user: User,
    db: AsyncSession
) -> None:
    """Convenience function to trigger task creation notifications."""
    await RealTimeNotificationService.task_created(task, created_by_user, db)


async def trigger_task_updated_notification(
    task: Task,
    updated_by_user: User,
    old_values: Dict[str, Any],
    new_values: Dict[str, Any],
    db: AsyncSession
) -> None:
    """Convenience function to trigger task update notifications."""
    await RealTimeNotificationService.task_updated(
        task, updated_by_user, old_values, new_values, db
    )


async def trigger_comment_created_notification(
    comment_data: Dict[str, Any],
    task: Task,
    user: User,
    db: AsyncSession
) -> None:
    """Convenience function to trigger comment creation notifications."""
    await RealTimeNotificationService.comment_created(comment_data, task, user, db)


async def trigger_mention_created_notification(
    mention_data: Dict[str, Any],
    task: Task,
    mentioned_by_user: User,
    mentioned_user: User,
    db: AsyncSession
) -> None:
    """Convenience function to trigger mention notifications."""
    await RealTimeNotificationService.mention_created(
        mention_data, task, mentioned_by_user, mentioned_user, db
    )


async def trigger_time_tracking_notification(
    time_log_data: Dict[str, Any],
    task: Task,
    user: User,
    action: str,  # "started" or "stopped"
    db: AsyncSession
) -> None:
    """Convenience function to trigger time tracking notifications."""
    if action == "started":
        await RealTimeNotificationService.time_tracking_started(time_log_data, task, user, db)
    elif action == "stopped":
        await RealTimeNotificationService.time_tracking_stopped(time_log_data, task, user, db)


# Global notification service instance
notification_service = RealTimeNotificationService()