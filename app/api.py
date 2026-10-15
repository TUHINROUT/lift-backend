from fastapi import APIRouter

from app.modules.auth.routes import router as auth_router

from app.modules.departments.routes import router as department_router

from app.modules.designations.routes import router as designation_router

from app.modules.customers.routes import router as customer_router

from app.modules.roles.routes import router as roles_router

from app.modules.users.routes import router as users_router

from app.modules.lifts.routes import router as lifts_router

from app.modules.tasks.routes import router as tasks_router

from app.modules.tickets.routes import router as ticket_router

from app.modules.attendance.routes import router as attendance_router

from app.modules.employee_tracking.routes import router as employee_tracking_router

from app.modules.lift_phases.routes import router as lift_phases_router

from app.modules.reports.routes import router as reports_router

from app.modules.sales_visits.routes import router as sales_visits_router
from app.modules.service_reports.routes import router as service_reports_router
from app.modules.crm_leads.routes import router as crm_leads_router
api_router = APIRouter()
api_router.include_router(service_reports_router)
api_router.include_router(auth_router)

api_router.include_router(department_router)

api_router.include_router(designation_router)

api_router.include_router(customer_router)

api_router.include_router(roles_router)

api_router.include_router(users_router)

api_router.include_router(lifts_router)

api_router.include_router(tasks_router)

api_router.include_router(ticket_router)

api_router.include_router(attendance_router)

api_router.include_router(employee_tracking_router)

api_router.include_router(lift_phases_router)

api_router.include_router(reports_router)

api_router.include_router(sales_visits_router)
  
api_router.include_router(crm_leads_router)