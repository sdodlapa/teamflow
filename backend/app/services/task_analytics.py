"""Advanced task analytics service for Day 3 implementation."""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.orm import joinedload

from app.models.task import Task, TaskStatus, TaskPriority
from app.models.task_analytics import (
    TaskProductivityMetrics, TeamPerformanceMetrics, 
    TaskComplexityEstimation, SmartAssignmentLog,
    BottleneckAnalysis, ProjectHealthMetrics,
    TaskComplexityType, BottleneckType
)
from app.models.user import User
from app.models.project import Project
from app.models.organization import Organization


class TaskAnalyticsService:
    """Service for advanced task analytics and insights."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_task_complexity(self, task_data: dict) -> Dict:
        """AI-powered task complexity estimation."""
        base_score = 3.0
        confidence = 0.8
        
        # Description complexity analysis
        description = task_data.get("description", "")
        description_length = len(description)
        
        if description_length > 1000:
            base_score += 2.5
        elif description_length > 500:
            base_score += 1.5
        elif description_length > 200:
            base_score += 0.5
        
        # Skill requirements analysis
        skills = task_data.get("skill_requirements", [])
        skill_complexity = {
            "python": 1.2, "javascript": 1.0, "react": 1.3, "vue": 1.2,
            "docker": 1.5, "kubernetes": 2.0, "aws": 1.8, "database": 1.4,
            "machine-learning": 2.5, "ai": 2.5, "blockchain": 2.2,
            "devops": 1.8, "security": 2.0, "architecture": 2.2
        }
        
        for skill in skills:
            skill_lower = skill.lower()
            base_score += skill_complexity.get(skill_lower, 1.0)
        
        # Dependencies complexity
        dependencies_count = task_data.get("dependencies_count", 0)
        if dependencies_count > 5:
            base_score += 2.0
        elif dependencies_count > 2:
            base_score += 1.0
        elif dependencies_count > 0:
            base_score += 0.5
        
        # Priority weight
        priority = task_data.get("priority", "medium")
        priority_weights = {"urgent": 1.5, "high": 1.2, "medium": 1.0, "low": 0.8}
        base_score *= priority_weights.get(priority, 1.0)
        
        # Historical similarity (mock for now - would be ML-powered)
        similar_tasks_avg = await self._get_similar_tasks_complexity(task_data)
        if similar_tasks_avg:
            base_score = (base_score + similar_tasks_avg) / 2
            confidence = min(confidence + 0.1, 0.95)
        
        # Final score normalization
        final_score = max(1, min(10, int(round(base_score))))
        
        # Determine complexity type
        if final_score <= 2:
            complexity_type = TaskComplexityType.TRIVIAL
        elif final_score <= 4:
            complexity_type = TaskComplexityType.SIMPLE
        elif final_score <= 6:
            complexity_type = TaskComplexityType.MODERATE
        elif final_score <= 8:
            complexity_type = TaskComplexityType.COMPLEX
        else:
            complexity_type = TaskComplexityType.CRITICAL
        
        return {
            "complexity_score": final_score,
            "complexity_type": complexity_type,
            "confidence_level": round(confidence, 2),
            "factors": {
                "description_complexity": min(description_length / 1000, 1.0),
                "skill_requirements_score": len(skills) / 5.0,
                "dependency_complexity": min(dependencies_count / 10, 1.0),
                "historical_similarity": similar_tasks_avg or 0.0
            }
        }
    
    async def _get_similar_tasks_complexity(self, task_data: dict) -> Optional[float]:
        """Find similar tasks and return average complexity."""
        try:
            # Simple similarity based on title keywords and skills
            title_keywords = set(task_data.get("title", "").lower().split())
            skills = set(task_data.get("skill_requirements", []))
            
            # Query for tasks with similar attributes
            query = select(TaskComplexityEstimation).join(Task).where(
                and_(
                    TaskComplexityEstimation.actual_complexity.isnot(None),
                    Task.is_active == True
                )
            ).limit(10)
            
            result = await self.db.execute(query)
            similar_estimations = result.scalars().all()
            
            if not similar_estimations:
                return None
            
            # Calculate weighted average (simplified)
            total_score = sum(est.actual_complexity for est in similar_estimations)
            return total_score / len(similar_estimations)
            
        except Exception as e:
            print(f"Error calculating similar tasks: {e}")
            return None

    async def smart_task_assignment(
        self, 
        task: Task, 
        candidate_users: List[User]
    ) -> Dict:
        """Intelligent task assignment based on multiple factors."""
        if not candidate_users:
            return {"error": "No candidate users provided"}
        
        scores = {}
        
        for user in candidate_users:
            score_details = await self._calculate_assignment_score(task, user)
            scores[user.id] = score_details
        
        # Find best candidate
        best_user_id = max(scores.keys(), key=lambda uid: scores[uid]["total_score"])
        best_user = next(u for u in candidate_users if u.id == best_user_id)
        
        return {
            "recommended_user_id": best_user_id,
            "recommended_user": best_user,
            "scores": scores,
            "confidence": scores[best_user_id]["confidence"]
        }
    
    async def _calculate_assignment_score(self, task: Task, user: User) -> Dict:
        """Calculate assignment score for a user."""
        # Skill matching (40% weight)
        skill_match = await self._calculate_skill_match(task, user)
        
        # Workload factor (30% weight)
        workload_factor = await self._calculate_workload_factor(user)
        
        # Performance score (20% weight) 
        performance_score = await self._get_user_performance_score(user, task.complexity_score)
        
        # Availability (10% weight)
        availability_score = await self._check_user_availability(user)
        
        # Calculate weighted total
        total_score = (
            skill_match * 0.4 +
            (1 - workload_factor) * 0.3 +
            performance_score * 0.2 +
            availability_score * 0.1
        )
        
        return {
            "total_score": round(total_score, 3),
            "skill_match": round(skill_match, 3),
            "workload_factor": round(workload_factor, 3),
            "performance_score": round(performance_score, 3),
            "availability_score": round(availability_score, 3),
            "confidence": min(0.9, 0.5 + total_score * 0.4)
        }
    
    async def _calculate_skill_match(self, task: Task, user: User) -> float:
        """Calculate how well user skills match task requirements."""
        if not task.skill_requirements:
            return 0.8  # Default match if no requirements specified
        
        required_skills = set(skill.lower() for skill in task.skill_requirements)
        
        # Mock user skills - in real implementation, this would come from user profile
        user_skills = {"python", "javascript", "react", "docker", "database"}  
        user_skills_lower = set(skill.lower() for skill in user_skills)
        
        if not required_skills:
            return 0.8
        
        matched_skills = required_skills.intersection(user_skills_lower)
        match_ratio = len(matched_skills) / len(required_skills)
        
        return min(1.0, match_ratio + 0.2)  # Bonus for having all skills
    
    async def _calculate_workload_factor(self, user: User) -> float:
        """Calculate current workload factor (0.0 = no load, 1.0 = overloaded)."""
        # Count active tasks assigned to user
        query = select(func.count(Task.id)).where(
            and_(
                Task.assignee_id == user.id,
                Task.status.in_([TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.IN_REVIEW]),
                Task.is_active == True
            )
        )
        result = await self.db.execute(query)
        active_tasks = result.scalar()
        
        # Normalize workload (assuming 5 tasks is normal capacity)
        normal_capacity = 5
        workload_factor = min(1.0, active_tasks / normal_capacity)
        
        return workload_factor
    
    async def _get_user_performance_score(self, user: User, task_complexity: Optional[int]) -> float:
        """Get user's performance score for similar complexity tasks."""
        if not task_complexity:
            return 0.7  # Default performance
        
        # Query recent performance metrics
        query = select(TaskProductivityMetrics).join(Task).where(
            and_(
                Task.assignee_id == user.id,
                TaskProductivityMetrics.quality_score.isnot(None),
                TaskProductivityMetrics.created_at >= datetime.utcnow() - timedelta(days=90)
            )
        ).limit(10)
        
        result = await self.db.execute(query)
        metrics = result.scalars().all()
        
        if not metrics:
            return 0.7  # Default if no history
        
        # Calculate average performance
        avg_quality = sum(m.quality_score for m in metrics if m.quality_score) / len(metrics)
        return min(1.0, avg_quality)
    
    async def _check_user_availability(self, user: User) -> float:
        """Check user availability (simplified)."""
        # In real implementation, this would check calendar, vacation, etc.
        return 0.9  # Assume most users are available
    
    async def calculate_productivity_metrics(self, task_id: int) -> Dict:
        """Calculate comprehensive productivity metrics for a task."""
        # Get task with related data
        query = select(Task).options(
            joinedload(Task.time_logs),
            joinedload(Task.activities),
            joinedload(Task.enhanced_comments)
        ).where(Task.id == task_id)
        
        result = await self.db.execute(query)
        task = result.unique().scalar_one_or_none()
        
        if not task:
            return {"error": "Task not found"}
        
        # Calculate time to completion
        time_to_completion = None
        if task.status == TaskStatus.DONE and task.created_at:
            time_to_completion = (task.updated_at - task.created_at).total_seconds() / 3600
        
        # Calculate estimation accuracy
        estimation_accuracy = None
        if task.estimated_hours and task.actual_hours:
            if task.actual_hours > 0:
                estimation_accuracy = task.estimated_hours / task.actual_hours
        
        # Calculate revision efficiency
        revision_count = task.revision_count or 0
        quality_score = task.quality_score or 0.8
        revision_efficiency = quality_score / max(1, revision_count + 1)
        
        # Create or update productivity metrics
        existing_metric = await self.db.execute(
            select(TaskProductivityMetrics).where(
                TaskProductivityMetrics.task_id == task_id
            )
        )
        metric = existing_metric.scalar_one_or_none()
        
        if not metric:
            metric = TaskProductivityMetrics(
                task_id=task_id,
                time_to_completion=time_to_completion,
                estimation_accuracy=estimation_accuracy,
                revision_count=revision_count,
                quality_score=quality_score,
                revision_efficiency=revision_efficiency,
                calculation_date=datetime.utcnow()
            )
            self.db.add(metric)
        else:
            metric.time_to_completion = time_to_completion
            metric.estimation_accuracy = estimation_accuracy
            metric.revision_count = revision_count
            metric.quality_score = quality_score
            metric.revision_efficiency = revision_efficiency
            metric.calculation_date = datetime.utcnow()
        
        await self.db.commit()
        
        return {
            "task_id": task_id,
            "time_to_completion": time_to_completion,
            "estimation_accuracy": estimation_accuracy,
            "revision_count": revision_count,
            "quality_score": quality_score,
            "revision_efficiency": revision_efficiency,
            "blocked_hours": task.blocked_hours or 0,
            "review_cycles": task.review_cycles or 0
        }
    
    async def analyze_team_performance(
        self, 
        team_identifier: str,
        period_start: datetime,
        period_end: datetime
    ) -> Dict:
        """Analyze team performance for a given period."""
        
        # Query tasks completed in period
        tasks_query = select(Task).where(
            and_(
                Task.updated_at >= period_start,
                Task.updated_at <= period_end,
                Task.status == TaskStatus.DONE,
                Task.is_active == True
            )
        )
        
        if team_identifier.startswith("project_"):
            project_id = int(team_identifier.split("_")[1])
            tasks_query = tasks_query.where(Task.project_id == project_id)
        
        result = await self.db.execute(tasks_query)
        completed_tasks = result.scalars().all()
        
        if not completed_tasks:
            return {"error": "No completed tasks found in period"}
        
        # Calculate metrics
        tasks_completed = len(completed_tasks)
        
        # Tasks completed on time
        on_time_count = sum(
            1 for task in completed_tasks 
            if task.due_date and task.updated_at <= task.due_date
        )
        
        # Average completion time
        completion_times = []
        for task in completed_tasks:
            if task.created_at:
                completion_time = (task.updated_at - task.created_at).total_seconds() / 3600
                completion_times.append(completion_time)
        
        avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else None
        
        # Average complexity
        complexities = [task.complexity_score for task in completed_tasks if task.complexity_score]
        avg_complexity = sum(complexities) / len(complexities) if complexities else None
        
        # Quality metrics
        quality_scores = [task.quality_score for task in completed_tasks if task.quality_score]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else None
        
        # Revision metrics
        revision_counts = [task.revision_count for task in completed_tasks if task.revision_count]
        avg_revisions = sum(revision_counts) / len(revision_counts) if revision_counts else 0
        
        # Bottleneck detection
        bottlenecks = await self._detect_bottlenecks(team_identifier, period_start, period_end)
        
        # Save team metrics
        team_metric = TeamPerformanceMetrics(
            team_identifier=team_identifier,
            period_start=period_start,
            period_end=period_end,
            tasks_completed=tasks_completed,
            tasks_completed_on_time=on_time_count,
            avg_task_completion_time=avg_completion_time,
            avg_complexity_score=avg_complexity,
            avg_quality_score=avg_quality,
            avg_revision_count=avg_revisions,
            bottleneck_areas=[b["type"] for b in bottlenecks],
            productivity_trend=0.05,  # Mock trend
            efficiency_score=0.8,  # Mock efficiency
            capacity_utilization=0.75  # Mock utilization
        )
        
        self.db.add(team_metric)
        await self.db.commit()
        
        return {
            "team_identifier": team_identifier,
            "period": {"start": period_start, "end": period_end},
            "tasks_completed": tasks_completed,
            "on_time_percentage": round(on_time_count / tasks_completed * 100, 1) if tasks_completed > 0 else 0,
            "avg_completion_time_hours": round(avg_completion_time, 2) if avg_completion_time else None,
            "avg_complexity_score": round(avg_complexity, 1) if avg_complexity else None,
            "avg_quality_score": round(avg_quality, 2) if avg_quality else None,
            "avg_revision_count": round(avg_revisions, 1),
            "bottlenecks": bottlenecks,
            "efficiency_indicators": {
                "productivity_trend": 5,  # 5% improvement
                "capacity_utilization": 75,  # 75% of capacity used
                "burnout_risk": 15  # 15% burnout risk
            }
        }
    
    async def _detect_bottlenecks(
        self, 
        team_identifier: str, 
        period_start: datetime, 
        period_end: datetime
    ) -> List[Dict]:
        """Detect process bottlenecks for a team."""
        bottlenecks = []
        
        # Query tasks in period
        tasks_query = select(Task).where(
            and_(
                Task.created_at >= period_start,
                Task.updated_at <= period_end,
                Task.is_active == True
            )
        )
        
        if team_identifier.startswith("project_"):
            project_id = int(team_identifier.split("_")[1])
            tasks_query = tasks_query.where(Task.project_id == project_id)
        
        result = await self.db.execute(tasks_query)
        tasks = result.scalars().all()
        
        if not tasks:
            return bottlenecks
        
        # Analyze status distribution
        status_counts = defaultdict(int)
        for task in tasks:
            status_counts[task.status] += 1
        
        total_tasks = len(tasks)
        
        # Check for review bottleneck
        if status_counts.get(TaskStatus.IN_REVIEW, 0) / total_tasks > 0.3:
            bottlenecks.append({
                "type": BottleneckType.APPROVAL,
                "severity": 0.7,
                "description": "High percentage of tasks stuck in review",
                "affected_tasks": status_counts[TaskStatus.IN_REVIEW],
                "recommendation": "Add more reviewers or streamline review process"
            })
        
        # Check for blocked tasks (high blocked_hours)
        blocked_tasks = [t for t in tasks if t.blocked_hours and t.blocked_hours > 8]
        if len(blocked_tasks) / total_tasks > 0.2:
            bottlenecks.append({
                "type": BottleneckType.DEPENDENCY,
                "severity": 0.6,
                "description": "Many tasks with significant blocked time",
                "affected_tasks": len(blocked_tasks),
                "recommendation": "Review task dependencies and resolve blockers"
            })
        
        # Check for resource bottleneck (many unassigned tasks)
        unassigned_tasks = [t for t in tasks if not t.assignee_id]
        if len(unassigned_tasks) / total_tasks > 0.4:
            bottlenecks.append({
                "type": BottleneckType.RESOURCE,
                "severity": 0.8,
                "description": "High percentage of unassigned tasks",
                "affected_tasks": len(unassigned_tasks),
                "recommendation": "Hire more team members or redistribute workload"
            })
        
        return bottlenecks
    
    async def generate_project_health_report(self, project_id: int) -> Dict:
        """Generate comprehensive project health report."""
        
        # Get project with tasks
        project_query = select(Project).options(
            joinedload(Project.tasks)
        ).where(Project.id == project_id)
        
        result = await self.db.execute(project_query)
        project = result.unique().scalar_one_or_none()
        
        if not project:
            return {"error": "Project not found"}
        
        tasks = project.tasks
        active_tasks = [t for t in tasks if t.is_active]
        
        # Calculate health scores
        velocity_score = await self._calculate_velocity_score(active_tasks)
        quality_score = await self._calculate_quality_score(active_tasks)
        risk_scores = await self._calculate_risk_scores(project, active_tasks)
        
        # Overall health score (weighted average)
        health_score = (
            velocity_score * 0.3 +
            quality_score * 0.3 +
            (1 - risk_scores["deadline_risk"]) * 0.2 +
            (1 - risk_scores["budget_risk"]) * 0.1 +
            (1 - risk_scores["resource_risk"]) * 0.1
        ) * 100
        
        # Generate recommendations
        recommendations = await self._generate_health_recommendations(
            health_score, velocity_score, quality_score, risk_scores
        )
        
        # Save health metrics
        health_metric = ProjectHealthMetrics(
            project_id=project_id,
            overall_health_score=health_score,
            velocity_score=velocity_score,
            quality_score=quality_score,
            deadline_risk=risk_scores["deadline_risk"],
            budget_risk=risk_scores["budget_risk"],
            resource_risk=risk_scores["resource_risk"],
            technical_risk=risk_scores["technical_risk"],
            health_trend=0.02,  # Mock trend
            recommendations=recommendations
        )
        
        self.db.add(health_metric)
        await self.db.commit()
        
        return {
            "project_id": project_id,
            "project_name": project.name,
            "health_score": round(health_score, 1),
            "health_level": self._get_health_level(health_score),
            "scores": {
                "velocity": round(velocity_score, 2),
                "quality": round(quality_score, 2)
            },
            "risks": {
                "deadline": round(risk_scores["deadline_risk"], 2),
                "budget": round(risk_scores["budget_risk"], 2),
                "resource": round(risk_scores["resource_risk"], 2),
                "technical": round(risk_scores["technical_risk"], 2)
            },
            "metrics": {
                "total_tasks": len(tasks),
                "active_tasks": len(active_tasks),
                "completed_tasks": len([t for t in tasks if t.status == TaskStatus.DONE]),
                "overdue_tasks": len([t for t in active_tasks if t.due_date and t.due_date < datetime.utcnow()])
            },
            "recommendations": recommendations,
            "trend": "improving"  # Mock trend
        }
    
    async def _calculate_velocity_score(self, tasks: List[Task]) -> float:
        """Calculate task completion velocity score."""
        if not tasks:
            return 0.5
        
        completed_tasks = [t for t in tasks if t.status == TaskStatus.DONE]
        completion_rate = len(completed_tasks) / len(tasks)
        
        # Factor in time performance
        on_time_tasks = [
            t for t in completed_tasks 
            if t.due_date and t.updated_at <= t.due_date
        ]
        
        on_time_rate = len(on_time_tasks) / len(completed_tasks) if completed_tasks else 0
        
        velocity_score = (completion_rate * 0.6 + on_time_rate * 0.4)
        return min(1.0, velocity_score)
    
    async def _calculate_quality_score(self, tasks: List[Task]) -> float:
        """Calculate overall quality score."""
        if not tasks:
            return 0.5
        
        quality_scores = [t.quality_score for t in tasks if t.quality_score]
        if not quality_scores:
            return 0.7  # Default quality
        
        return sum(quality_scores) / len(quality_scores)
    
    async def _calculate_risk_scores(self, project: Project, tasks: List[Task]) -> Dict:
        """Calculate various risk scores."""
        now = datetime.utcnow()
        
        # Deadline risk
        overdue_tasks = [t for t in tasks if t.due_date and t.due_date < now and t.status != TaskStatus.DONE]
        deadline_risk = min(1.0, len(overdue_tasks) / max(1, len(tasks)) * 2)
        
        # Budget risk (mock - would integrate with actual budget tracking)
        budget_risk = 0.2  # 20% budget risk
        
        # Resource risk (based on unassigned tasks)
        unassigned_tasks = [t for t in tasks if not t.assignee_id]
        resource_risk = min(1.0, len(unassigned_tasks) / max(1, len(tasks)) * 1.5)
        
        # Technical risk (based on complexity)
        high_complexity_tasks = [t for t in tasks if t.complexity_score and t.complexity_score > 7]
        technical_risk = min(1.0, len(high_complexity_tasks) / max(1, len(tasks)) * 1.2)
        
        return {
            "deadline_risk": deadline_risk,
            "budget_risk": budget_risk,
            "resource_risk": resource_risk,
            "technical_risk": technical_risk
        }
    
    async def _generate_health_recommendations(
        self, 
        health_score: float, 
        velocity_score: float, 
        quality_score: float, 
        risk_scores: Dict
    ) -> List[Dict]:
        """Generate actionable health recommendations."""
        recommendations = []
        
        if health_score < 70:
            recommendations.append({
                "type": "critical",
                "title": "Project Health Critical",
                "description": "Project health is below acceptable threshold",
                "action": "Schedule immediate team review and intervention"
            })
        
        if velocity_score < 0.6:
            recommendations.append({
                "type": "velocity",
                "title": "Improve Task Velocity",
                "description": "Task completion rate is below target",
                "action": "Review task complexity and team capacity"
            })
        
        if quality_score < 0.7:
            recommendations.append({
                "type": "quality",
                "title": "Enhance Quality Processes",
                "description": "Quality scores indicate need for improvement",
                "action": "Implement additional review processes and testing"
            })
        
        if risk_scores["deadline_risk"] > 0.5:
            recommendations.append({
                "type": "deadline",
                "title": "Address Deadline Risks",
                "description": "High risk of missing project deadlines",
                "action": "Re-evaluate timeline and resource allocation"
            })
        
        if risk_scores["resource_risk"] > 0.4:
            recommendations.append({
                "type": "resource",
                "title": "Resource Allocation Issue",
                "description": "Many tasks are unassigned",
                "action": "Balance workload and consider additional resources"
            })
        
        return recommendations
    
    def _get_health_level(self, score: float) -> str:
        """Convert health score to level."""
        if score >= 90:
            return "excellent"
        elif score >= 80:
            return "good"
        elif score >= 70:
            return "fair"
        elif score >= 60:
            return "poor"
        else:
            return "critical"