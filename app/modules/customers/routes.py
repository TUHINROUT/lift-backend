from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.customers.schemas import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
)
from app.modules.customers.service import CustomerService
from app.core.dependencies import require_roles
from app.modules.users.models import User

router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
)


#! Create customer
@router.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_customer(
    request: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "MANAGER")),
):
    service = CustomerService(db)

    try:
        customer = await service.create_customer(request)
        return customer

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


#! Get all customers
@router.get(
    "",
    response_model=list[CustomerResponse],
)
async def get_customers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "MANAGER")),
):
    service = CustomerService(db)
    return await service.get_customers()


#! Get customer by customer_id
@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
)
async def get_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "MANAGER")),
):
    service = CustomerService(db)

    try:
        return await service.get_customer_by_id(customer_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


#! Activate customer
@router.patch(
    "/{customer_id}/activate",
    response_model=CustomerResponse,
)
async def activate_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "MANAGER")),
):
    service = CustomerService(db)

    try:
        return await service.activate_customer(customer_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


#! Deactivate customer
@router.patch(
    "/{customer_id}/deactivate",
    response_model=CustomerResponse,
)
async def deactivate_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "MANAGER")),
):
    service = CustomerService(db)

    try:
        return await service.deactivate_customer(customer_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

#! Update customer
@router.patch(
    "/{customer_id}",
    response_model=CustomerResponse,
)
async def update_customer(
    customer_id: int,
    request: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "MANAGER")),
):
    service = CustomerService(db)

    try:
        return await service.update_customer(
            customer_id,
            request,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

#! Delete customer
@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "MANAGER")),
):
    service = CustomerService(db)

    try:
        await service.delete_customer(customer_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )