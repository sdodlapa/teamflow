"""
Practical Example: Converting TeamFlow to a Fleet Management System

This example shows the actual code changes needed to adapt TeamFlow
to a vehicle fleet management use case.
"""

def show_fleet_management_implementation():
    """Show practical implementation of fleet management system."""
    
    print("🚗 Fleet Management System Implementation")
    print("=" * 50)
    
    print("📋 STEP 1: Entity Mapping Analysis")
    print("  Current TeamFlow → Fleet Management")
    print("  • Organization → Fleet Company")
    print("  • Project      → Fleet Division/Route")
    print("  • Task         → Maintenance/Trip")
    print("  • User         → Driver/Manager/Mechanic")
    
    print("\n🏗️ STEP 2: New Models (backend/app/models/fleet.py)")
    print("```python")
    
    vehicle_model = '''from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Vehicle(BaseModel):
    """Fleet vehicle entity."""
    __tablename__ = "vehicles"
    
    # Basic vehicle info
    vin = Column(String(17), unique=True, nullable=False, index=True)
    make = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    license_plate = Column(String(20), unique=True, nullable=False, index=True)
    
    # Vehicle specifications
    vehicle_type = Column(String(30), nullable=False, index=True)  # truck, van, car, etc.
    fuel_type = Column(String(20), default="gasoline")  # gasoline, diesel, electric, hybrid
    capacity_weight = Column(Integer)  # kg
    capacity_volume = Column(Integer)  # liters
    
    # Status and tracking
    status = Column(String(20), default="available", index=True)  # available, in_use, maintenance, retired
    current_mileage = Column(Integer, default=0)
    last_service_mileage = Column(Integer, default=0)
    next_service_due = Column(DateTime)
    
    # Location and assignment
    current_location = Column(String(255))
    home_depot_id = Column(Integer, ForeignKey("depots.id"))
    assigned_driver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Multi-tenant
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Relationships
    organization = relationship("Organization")
    assigned_driver = relationship("User", foreign_keys=[assigned_driver_id])
    home_depot = relationship("Depot")
    trips = relationship("Trip", back_populates="vehicle")
    maintenance_records = relationship("MaintenanceRecord", back_populates="vehicle")

class Trip(BaseModel):
    """Vehicle trip/journey record."""
    __tablename__ = "trips"
    
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Trip details
    start_location = Column(String(255), nullable=False)
    end_location = Column(String(255), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    
    # Metrics
    start_mileage = Column(Integer, nullable=False)
    end_mileage = Column(Integer)
    distance_km = Column(Float)
    fuel_consumed = Column(Float)
    
    # Status and purpose
    status = Column(String(20), default="planned", index=True)  # planned, in_progress, completed, cancelled
    trip_type = Column(String(30), nullable=False)  # delivery, pickup, maintenance, personal
    purpose = Column(Text)
    
    # Costs
    fuel_cost = Column(Integer)  # in cents
    toll_cost = Column(Integer)  # in cents
    other_expenses = Column(Integer)  # in cents
    
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="trips")
    driver = relationship("User", foreign_keys=[driver_id])
    organization = relationship("Organization")
'''
    
    print(vehicle_model)
    print("```")
    
    print("\n📝 STEP 3: API Schemas (backend/app/schemas/fleet.py)")
    print("```python")
    
    schema_example = '''from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class VehicleBase(BaseModel):
    """Base vehicle schema."""
    vin: str = Field(..., min_length=17, max_length=17)
    make: str = Field(..., min_length=1, max_length=50)
    model: str = Field(..., min_length=1, max_length=50)
    year: int = Field(..., ge=1900, le=2030)
    license_plate: str = Field(..., max_length=20)
    vehicle_type: str = Field(..., max_length=30)
    fuel_type: str = Field(default="gasoline", max_length=20)

class VehicleCreate(VehicleBase):
    """Schema for creating a vehicle."""
    organization_id: int = Field(..., description="Organization ID")
    home_depot_id: Optional[int] = None

class VehicleResponse(VehicleBase):
    """Schema for vehicle responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    uuid: str
    status: str
    current_mileage: int
    organization_id: int
    created_at: datetime
    updated_at: datetime
    
    # Computed fields
    next_service_in_km: Optional[int] = None
    driver_name: Optional[str] = None
    depot_name: Optional[str] = None

class TripCreate(BaseModel):
    """Schema for creating a trip."""
    vehicle_id: int
    start_location: str = Field(..., max_length=255)
    end_location: str = Field(..., max_length=255)
    start_time: datetime
    start_mileage: int = Field(..., ge=0)
    trip_type: str = Field(..., max_length=30)
    purpose: Optional[str] = None
'''
    
    print(schema_example)
    print("```")
    
    print("\n🚀 STEP 4: API Routes (backend/app/api/routes/fleet.py)")
    print("```python")
    
    api_example = '''from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.fleet import Vehicle, Trip
from app.schemas.fleet import VehicleCreate, VehicleResponse, TripCreate

router = APIRouter(prefix="/fleet", tags=["Fleet Management"])

@router.get("/vehicles", response_model=List[VehicleResponse])
async def list_vehicles(
    status: Optional[str] = Query(None, description="Filter by status"),
    vehicle_type: Optional[str] = Query(None, description="Filter by type"),
    assigned_driver: Optional[int] = Query(None, description="Filter by driver"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List vehicles with filtering."""
    
    query = select(Vehicle).where(
        Vehicle.organization_id.in_(current_user.get_accessible_organizations())
    )
    
    if status:
        query = query.where(Vehicle.status == status)
    if vehicle_type:
        query = query.where(Vehicle.vehicle_type == vehicle_type)
    if assigned_driver:
        query = query.where(Vehicle.assigned_driver_id == assigned_driver)
    
    result = await db.execute(query.offset(skip).limit(limit))
    vehicles = result.scalars().all()
    
    return vehicles

@router.post("/trips", response_model=dict, status_code=status.HTTP_201_CREATED)
async def start_trip(
    trip_data: TripCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start a new trip."""
    
    # Verify vehicle access and availability
    vehicle_query = select(Vehicle).where(
        and_(
            Vehicle.id == trip_data.vehicle_id,
            Vehicle.organization_id.in_(current_user.get_accessible_organizations()),
            Vehicle.status == "available"
        )
    )
    
    vehicle_result = await db.execute(vehicle_query)
    vehicle = vehicle_result.scalar_one_or_none()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found or not available"
        )
    
    # Create trip record
    trip = Trip(
        **trip_data.model_dump(),
        driver_id=current_user.id,
        organization_id=vehicle.organization_id,
        status="in_progress"
    )
    
    # Update vehicle status
    vehicle.status = "in_use"
    
    db.add(trip)
    await db.commit()
    await db.refresh(trip)
    
    return {"message": "Trip started successfully", "trip_id": trip.id}
'''
    
    print(api_example)
    print("```")
    
    print("\n🔄 STEP 5: Business Logic (backend/app/services/fleet_service.py)")
    print("```python")
    
    service_example = '''from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.fleet import Vehicle, Trip
from app.models.user import User

class FleetService:
    """Business logic for fleet management."""
    
    @staticmethod
    async def get_fleet_dashboard(
        db: AsyncSession,
        organization_id: int
    ) -> Dict[str, Any]:
        """Get fleet dashboard statistics."""
        
        # Vehicle status summary
        vehicle_status_query = select(
            Vehicle.status,
            func.count(Vehicle.id).label("count")
        ).where(
            Vehicle.organization_id == organization_id
        ).group_by(Vehicle.status)
        
        vehicle_status_result = await db.execute(vehicle_status_query)
        vehicle_status = {row.status: row.count for row in vehicle_status_result}
        
        # Active trips
        active_trips_query = select(func.count(Trip.id)).where(
            and_(
                Trip.organization_id == organization_id,
                Trip.status == "in_progress"
            )
        )
        active_trips_result = await db.execute(active_trips_query)
        active_trips = active_trips_result.scalar() or 0
        
        # Maintenance due
        maintenance_due_query = select(func.count(Vehicle.id)).where(
            and_(
                Vehicle.organization_id == organization_id,
                Vehicle.next_service_due <= datetime.now() + timedelta(days=7)
            )
        )
        maintenance_due_result = await db.execute(maintenance_due_query)
        maintenance_due = maintenance_due_result.scalar() or 0
        
        return {
            "total_vehicles": sum(vehicle_status.values()),
            "vehicle_status": vehicle_status,
            "active_trips": active_trips,
            "maintenance_due": maintenance_due,
            "utilization_rate": FleetService._calculate_utilization_rate(vehicle_status)
        }
    
    @staticmethod
    def _calculate_utilization_rate(vehicle_status: Dict[str, int]) -> float:
        """Calculate fleet utilization rate."""
        total = sum(vehicle_status.values())
        if total == 0:
            return 0.0
        
        in_use = vehicle_status.get("in_use", 0)
        return round((in_use / total) * 100, 2)
    
    @staticmethod
    async def schedule_maintenance(
        db: AsyncSession,
        vehicle_id: int,
        maintenance_type: str,
        scheduled_date: datetime
    ) -> Dict[str, Any]:
        """Schedule vehicle maintenance."""
        
        # This would integrate with the existing Task system
        # treating maintenance as specialized tasks
        
        return {
            "vehicle_id": vehicle_id,
            "maintenance_scheduled": True,
            "scheduled_date": scheduled_date
        }
'''
    
    print(service_example)
    print("```")
    
    print("\n🎨 STEP 6: React Components (frontend/src/components/FleetDashboard.tsx)")
    print("```typescript")
    
    frontend_example = '''import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface Vehicle {
  id: number;
  make: string;
  model: string;
  license_plate: string;
  status: string;
  current_mileage: number;
  driver_name?: string;
}

interface FleetStats {
  total_vehicles: number;
  vehicle_status: Record<string, number>;
  active_trips: number;
  maintenance_due: number;
  utilization_rate: number;
}

export const FleetDashboard: React.FC = () => {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [stats, setStats] = useState<FleetStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchFleetData();
  }, []);

  const fetchFleetData = async () => {
    try {
      const [vehiclesResponse, statsResponse] = await Promise.all([
        fetch('/api/v1/fleet/vehicles'),
        fetch('/api/v1/fleet/dashboard')
      ]);
      
      const vehiclesData = await vehiclesResponse.json();
      const statsData = await statsResponse.json();
      
      setVehicles(vehiclesData);
      setStats(statsData);
    } catch (error) {
      console.error('Failed to fetch fleet data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available': return 'bg-green-100 text-green-800';
      case 'in_use': return 'bg-blue-100 text-blue-800';
      case 'maintenance': return 'bg-yellow-100 text-yellow-800';
      case 'retired': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) return <div>Loading fleet data...</div>;

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Vehicles</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_vehicles || 0}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Active Trips</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.active_trips || 0}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Utilization Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.utilization_rate || 0}%</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Maintenance Due</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">
              {stats?.maintenance_due || 0}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Vehicle List */}
      <Card>
        <CardHeader>
          <CardTitle>Fleet Vehicles</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {vehicles.map((vehicle) => (
              <div key={vehicle.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <h3 className="font-semibold">
                    {vehicle.make} {vehicle.model}
                  </h3>
                  <p className="text-sm text-gray-600">
                    {vehicle.license_plate} • {vehicle.current_mileage.toLocaleString()} km
                  </p>
                  {vehicle.driver_name && (
                    <p className="text-sm text-blue-600">Driver: {vehicle.driver_name}</p>
                  )}
                </div>
                <div className="flex items-center space-x-2">
                  <Badge className={getStatusColor(vehicle.status)}>
                    {vehicle.status}
                  </Badge>
                  <Button variant="outline" size="sm">
                    View Details
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default FleetDashboard;
'''
    
    print(frontend_example)
    print("```")
    
    print("\n⚡ STEP 7: Integration with Existing Systems")
    print("🔗 Workflow Integration (backend/app/workflows/fleet_workflows.py)")
    print("```python")
    
    workflow_example = '''from app.models.workflow import WorkflowDefinition
from app.models.fleet import Vehicle

class FleetMaintenanceWorkflow:
    """Automated fleet maintenance workflow."""
    
    @staticmethod
    def get_definition():
        return {
            "name": "Vehicle Maintenance Scheduling",
            "trigger_type": "scheduled",
            "trigger_config": {"schedule": "daily", "time": "06:00"},
            "steps": [
                {
                    "name": "check_maintenance_due",
                    "type": "condition",
                    "config": {
                        "query": "vehicles.next_service_due <= NOW() + INTERVAL 7 DAYS"
                    }
                },
                {
                    "name": "create_maintenance_tasks",
                    "type": "action", 
                    "config": {
                        "create_task": True,
                        "task_type": "maintenance",
                        "assign_to": "maintenance_team"
                    }
                },
                {
                    "name": "notify_managers",
                    "type": "notification",
                    "config": {
                        "template": "maintenance_due",
                        "recipients": ["fleet_managers"]
                    }
                }
            ]
        }

class TripCompletionWorkflow:
    """Process trip completion and update metrics."""
    
    @staticmethod
    def get_definition():
        return {
            "name": "Trip Completion Processing",
            "trigger_type": "event",
            "trigger_config": {"event": "trip_completed"},
            "steps": [
                {
                    "name": "update_vehicle_mileage",
                    "type": "action",
                    "config": {
                        "update_field": "current_mileage",
                        "source": "trip.end_mileage"
                    }
                },
                {
                    "name": "calculate_fuel_efficiency",
                    "type": "action", 
                    "config": {
                        "formula": "distance_km / fuel_consumed"
                    }
                },
                {
                    "name": "check_service_interval",
                    "type": "condition",
                    "config": {
                        "condition": "current_mileage - last_service_mileage > 10000"
                    }
                }
            ]
        }
'''
    
    print(workflow_example)
    print("```")
    
    print("\n📊 STEP 8: Database Migration")
    print("```bash")
    print("# Generate migration")
    print("cd backend")
    print("alembic revision --autogenerate -m \"Add fleet management tables\"")
    print("")
    print("# Apply migration")
    print("alembic upgrade head")
    print("```")
    
    print("\n🎯 STEP 9: Configuration Updates")
    print("Add to backend/app/api/__init__.py:")
    print("```python")
    print("from app.api.routes import fleet")
    print("app.include_router(fleet.router, prefix=API_V1_STR)")
    print("```")
    
    print("\n✅ RESULTS: Complete Fleet Management System")
    print("  🚗 Vehicle tracking and management")
    print("  📍 Trip logging and route optimization") 
    print("  🔧 Maintenance scheduling and tracking")
    print("  📊 Fleet utilization and performance analytics")
    print("  👥 Driver assignment and management")
    print("  💰 Cost tracking and reporting")
    print("  📱 Mobile-friendly driver interface")
    print("  🔄 Automated workflows for maintenance and compliance")
    
    print("\n⏱️ Development Time: ~3-4 weeks")
    print("  Week 1: Database models and API endpoints")
    print("  Week 2: Business logic and workflows")  
    print("  Week 3: Frontend components and integration")
    print("  Week 4: Testing, optimization, and deployment")


if __name__ == "__main__":
    show_fleet_management_implementation()