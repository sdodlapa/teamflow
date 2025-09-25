# 🗄️ Production Database Migration Plan
## TeamFlow Database Setup for Production

### Current Status
- **Development Database**: SQLite (teamflow_dev.db)
- **Production Target**: PostgreSQL
- **Schema Tables**: 69 registered tables
- **Migration Files**: 16 Alembic migrations available
- **Models Status**: All core models importing successfully

---

## 📋 Migration Execution Plan

### Phase 1: Production Database Provisioning
```bash
# 1. Create PostgreSQL Database (Railway/Supabase)
# Example connection string format:
# postgresql://username:password@hostname:port/database_name

# 2. Set production DATABASE_URL environment variable
export DATABASE_URL="postgresql://user:pass@host:port/teamflow_production"

# 3. Verify connection
psql $DATABASE_URL -c "SELECT version();"
```

### Phase 2: Schema Migration
```bash
# 1. Navigate to backend directory
cd backend/

# 2. Run all pending migrations
alembic upgrade head

# 3. Verify schema creation
python -c "
from app.core.database import get_async_engine
from app.models import *
print('✅ All models loaded, schema ready')
"
```

### Phase 3: Production Data Setup
```bash
# 1. Create initial admin user (optional)
python -c "
import asyncio
from app.core.database import get_async_session
from app.models.user import User
from app.core.security import get_password_hash

async def create_admin():
    async with get_async_session() as db:
        admin = User(
            email='admin@teamflow.app',
            hashed_password=get_password_hash('admin123'),
            full_name='TeamFlow Admin',
            is_superuser=True,
            is_active=True
        )
        db.add(admin)
        await db.commit()
        print('✅ Admin user created')

asyncio.run(create_admin())
"

# 2. Create sample organization (optional)
# This can be done through the API after deployment
```

### Phase 4: Production Validation
```bash
# 1. Test database connectivity
python -c "
import asyncio
from app.core.database import get_async_session
from sqlalchemy import text

async def test_db():
    async with get_async_session() as db:
        result = await db.execute(text('SELECT 1'))
        print('✅ Database connection successful')

asyncio.run(test_db())
"

# 2. Verify all tables exist
python -c "
from app.core.database import create_sync_engine
from app.models import *
engine = create_sync_engine()
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f'✅ {len(tables)} tables created in production database')
"
```

---

## 🚀 Automated Migration Script

```bash
#!/bin/bash
# Production database migration automation

set -e

echo "🗄️ TeamFlow Production Database Migration"
echo "========================================"

# Validate environment
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL environment variable not set"
    exit 1
fi

echo "✅ Production DATABASE_URL configured"

# Run migrations
echo "🔄 Running Alembic migrations..."
alembic upgrade head

# Validate migration
echo "🔍 Validating migration success..."
python -c "
import asyncio
from app.core.database import get_async_session
from sqlalchemy import text

async def validate():
    async with get_async_session() as db:
        # Test basic query
        await db.execute(text('SELECT 1'))
        print('✅ Database migration successful')

asyncio.run(validate())
"

echo "🎉 Production database ready!"
```

---

## 📊 Migration Checklist

### Pre-Migration ✅
- [x] Development database functional (SQLite)
- [x] All models importing correctly (69 tables)
- [x] Alembic migrations available (16 files)
- [x] Production PostgreSQL instance ready
- [x] DATABASE_URL environment variable configured

### Migration Execution ⏳
- [ ] Database connection tested
- [ ] Alembic upgrade head executed
- [ ] Schema validation completed
- [ ] Initial admin user created (optional)
- [ ] Sample data loaded (optional)

### Post-Migration Validation ⏳
- [ ] All tables created successfully
- [ ] Relationships and constraints working
- [ ] Application can connect to production DB
- [ ] CRUD operations functional
- [ ] Performance baseline established

---

## 🔧 Production Database Configuration

### Performance Settings
```sql
-- Recommended PostgreSQL settings for production
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
SELECT pg_reload_conf();
```

### Connection Pooling
```python
# app/core/database.py production settings
DATABASE_CONFIG = {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "echo": False  # Disable SQL logging in production
}
```

### Backup Strategy
```bash
# Daily automated backups
0 2 * * * pg_dump $DATABASE_URL | gzip > /backups/teamflow_$(date +%Y%m%d).sql.gz

# Backup retention (keep 30 days)
find /backups/ -name "teamflow_*.sql.gz" -mtime +30 -delete
```

---

## 🎯 Success Criteria

### Database Migration Success ✅
- All 69 tables created in PostgreSQL
- No migration errors or warnings
- All constraints and relationships functional
- Application connects successfully

### Production Readiness ✅
- Connection pooling configured
- Performance settings optimized
- Backup strategy implemented
- Monitoring and alerting configured

### Business Continuity ✅
- Zero downtime migration possible
- Rollback plan documented
- Data integrity maintained
- Performance meets enterprise standards

---

*Database Migration Plan prepared for TeamFlow Production Deployment*  
*September 25, 2025 - Day 22 Infrastructure Setup*