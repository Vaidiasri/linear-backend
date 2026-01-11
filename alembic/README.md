# 🗄️ Alembic Database Migrations Guide

Ye folder database migrations ke liye hai. Alembic automatically tumhare models ko track karta hai aur database schema ko update karta hai.

---

## 📁 Folder Structure

```
alembic/
├── versions/          # Saari migration files yahan hongi
├── env.py            # Main configuration file (already configured ✅)
├── script.py.mako    # Migration template
└── README.md         # Ye file
```

---

## 🚀 Quick Start

### **Normal Server Run (Koi Model Change Nahi)**

```bash
python main.py
```

### **Model Change Ke Baad (4 Steps)**

⚠️ **IMPORTANT:** Agar server chal raha hai toh pehle **STOP** karo (Ctrl+C)

```bash
# Step 1: Server STOP karo (agar chal raha hai)
# Terminal mein Ctrl+C press karo

# Step 2: Migration create karo (server band hona chahiye)
python -m alembic revision --autogenerate -m "Your change description"

# Step 3: Migration apply karo (server band hai)
python -m alembic upgrade head

# Step 4: Server wapas start karo
python main.py
```

---

## 📝 Common Commands

⚠️ **RECOMMENDED:** Hamesha `python -m alembic` use karo (virtual environment issues avoid karne ke liye)

### **Migration Create Karna**

```bash
python -m alembic revision --autogenerate -m "Added phone_number to User table"
```

### **Migration Apply Karna (Database Update)**

```bash
python -m alembic upgrade head
```

### **Migration History Dekhna**

```bash
python -m alembic history
```

### **Current Version Check Karna**

```bash
python -m alembic current
```

### **Rollback Karna (Ek Step Peeche)**

```bash
python -m alembic downgrade -1
```

### **Complete Rollback (Sabse Pehle Wale State Pe)**

```bash
python -m alembic downgrade base
```

### **Specific Version Pe Jaana**

```bash
python -m alembic upgrade <revision_id>
# Example: python -m alembic upgrade 91185e2ee860
```

---

## 💡 Real World Example

### **Scenario: User Model Mein Phone Number Add Karna**

**Step 1: Model Edit Karo**

```python
# app/model/model.py
class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    hashed_password = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)  # 👈 Naya column
```

**Step 2: Server STOP Karo (Agar Chal Raha Hai)**

```bash
# Terminal mein Ctrl+C press karo
```

**Step 3: Migration Create Karo**

```bash
python -m alembic revision --autogenerate -m "Added phone_number to User"
```

**Step 4: Migration Apply Karo**

```bash
python -m alembic upgrade head
```

**Step 5: Server Start Karo**

```bash
python main.py
```

---

## 🔍 Migration File Kaise Dikhti Hai

```python
"""Added phone_number to User

Revision ID: abc123def456
Revises: 91185e2ee860
Create Date: 2026-01-11 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Database ko update karne ka code
    op.add_column('users', sa.Column('phone_number', sa.String(), nullable=True))

def downgrade():
    # Rollback karne ka code
    op.drop_column('users', 'phone_number')
```

---

## ⚠️ Important Notes

### **DO's ✅**

- ✅ Hamesha model change ke baad migration create karo
- ✅ Migration files ko git mein commit karo
- ✅ Production mein migrate karne se pehle backup lo
- ✅ Migration message descriptive rakho

### **DON'Ts ❌**

- ❌ Migration files ko manually edit mat karo (unless you know what you're doing)
- ❌ Migration files ko delete mat karo
- ❌ Directly database mein changes mat karo
- ❌ `app/main.py` mein `Base.metadata.create_all()` use mat karo (already disabled hai)

---

## 🐛 Common Issues & Solutions

### **Issue 1: "Target database is not up to date"**

```bash
# Solution: Database ko current version pe stamp karo
alembic stamp head
```

### **Issue 2: "Can't locate revision identified by 'xyz'"**

```bash
# Solution: History check karo aur head pe upgrade karo
alembic history
alembic upgrade head
```

### **Issue 3: Models detect nahi ho rahe**

- Check karo `alembic/env.py` mein `from app.model import model` properly import hua hai
- Check karo `Base.metadata` set hai

### **Issue 4: Async/Sync Database URL Error**

- Already fixed hai! `env.py` automatically async URL ko sync mein convert karta hai
- `postgresql+asyncpg://` → `postgresql+psycopg2://`

### **Issue 5: "ModuleNotFoundError: No module named 'psycopg2'"**

Ye error tab aata hai jab virtual environment properly load nahi hota.

**❌ Problem:**

```bash
alembic revision --autogenerate -m "message"
# Error: ModuleNotFoundError: No module named 'psycopg2'
```

**✅ Solution: `python -m` use karo**

```bash
# Hamesha ye commands use karo:
python -m alembic revision --autogenerate -m "message"
python -m alembic upgrade head
python -m alembic current
python -m alembic history
```

**Kyun?** `python -m alembic` proper Python module ke through run karta hai aur virtual environment correctly load hota hai.

---

## 🔄 Workflow Diagram

```
┌─────────────────────────────────────────────────────────┐
│  Model Change Kiya? (app/model/model.py)               │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ├─── NO ──→ python main.py (Done! ✅)
                    │
                    └─── YES ──→ Follow these steps:
                                 │
                                 ├─ 1. Server STOP karo (Ctrl+C)
                                 │
                                 ├─ 2. python -m alembic revision --autogenerate -m "message"
                                 │
                                 ├─ 3. python -m alembic upgrade head
                                 │
                                 └─ 4. python main.py (Server wapas start)
```

---

## 📚 Additional Resources

- **Alembic Documentation:** https://alembic.sqlalchemy.org/
- **SQLAlchemy Documentation:** https://docs.sqlalchemy.org/

---

## 🎯 Quick Reference Card

| Task              | Command                                                  |
| ----------------- | -------------------------------------------------------- |
| Create Migration  | `python -m alembic revision --autogenerate -m "message"` |
| Apply Migration   | `python -m alembic upgrade head`                         |
| View History      | `python -m alembic history`                              |
| Current Version   | `python -m alembic current`                              |
| Rollback One Step | `python -m alembic downgrade -1`                         |
| Rollback All      | `python -m alembic downgrade base`                       |
| Specific Version  | `python -m alembic upgrade <revision_id>`                |

---

## 💬 Need Help?

Agar koi issue aaye toh:

1. Migration history check karo: `alembic history`
2. Current version check karo: `alembic current`
3. Error message carefully padho
4. Agar phir bhi issue ho toh team se poocho!

---

**Happy Migrating! 🚀**

_Last Updated: 2026-01-11_
