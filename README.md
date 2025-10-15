# Humanitarian Projects Management (scaffold)

This is a minimal FastAPI scaffold implementing three modules:

- Personnel management (users, roles, assignments, KPI)
- Warehouse management (commodities, TTN, inventory, stock card)
- Planning (distribution plans that check available stock)

Run locally:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt; uvicorn app.main:app --reload
```

Quick endpoints:
- `POST /personnel/users` create user
- `POST /warehouse/commodities` create commodity
- `POST /planning/plans` create plan (checks stock)
