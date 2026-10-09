from datetime import datetime, UTC
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.modules.users.models import User
from app.modules.users.repository import UsersRepository
from app.modules.users.schemas import (
    UserCreate,
    UserUpdate,
)
from app.services.email import (
    EmailSendError,
    send_email,
)


class UsersService:
    def __init__(self, db: AsyncSession):
        self.repository = UsersRepository(db)

    async def create_user(
        self,
        user_data: UserCreate,
    ) -> User:

        existing_user = await self.repository.get_by_email(
            user_data.email,
        )

        if existing_user:
            raise ValueError("Email already exists.")

        last_user = await self.repository.get_last_user()

        if last_user is None:
            next_number = 1
        else:
            last_code = last_user.employee_code

            if last_code is None:
                next_number = last_user.id + 1
            else:
                next_number = (
                    int(last_code.replace("EMP", ""))
                    + 1
                )

        employee_code = f"EMP{next_number:06d}"
        password = user_data.password

        user = User(
            employee_code=employee_code,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            password_hash=hash_password(
                user_data.password
            ),
            department_id=user_data.department_id,
            designation_id=user_data.designation_id,
            company_id=user_data.company_id,
            role_id=user_data.role_id,
            profile_photo=user_data.profile_photo,
            is_active=True,
            is_verified=True,
            is_superuser=False,
        )
        user = await self.repository.create(user)

        try:
            send_email(
                to_email=user.email,
                subject="Welcome to Lift Service",
                body=(
                    f"Hello {user.first_name} {user.last_name},\n\n"
                    "Your account has been created successfully.\n\n"
                    f"Employee Code: {user.employee_code}\n"
                    f"Email: {user.email}\n"
                    f"Password: {password}\n\n"
                    "You can now use these credentials to log in.\n\n"
                    "Regards,\n"
                    "Lift Service Team"
                ),
            )
        except EmailSendError as exc:
            raise ValueError(str(exc))

        return user

    async def get_users(self):
        return await self.repository.get_all()

    async def get_user(
        self,
        user_id: int,
    ) -> User:
        user = await self.repository.get_user_by_id(user_id)

        if user is None:
            raise ValueError("User not found.")
        return user

    async def search_users(
        self,
        name: str,
    ):
        return await self.repository.search_by_name(name)

    async def update_user(
        self,
        user_id: int,
        user_data: UserUpdate,
    ) -> User:
        user = await self.repository.get_user_by_id(user_id)

        if user is None:
            raise ValueError("User not found.")

        if user_data.first_name is not None:
            user.first_name = user_data.first_name

        if user_data.last_name is not None:
            user.last_name = user_data.last_name

        if user_data.department_id is not None:
            user.department_id = user_data.department_id

        if user_data.designation_id is not None:
            user.designation_id = user_data.designation_id

        if user_data.role_id is not None:
            user.role_id = user_data.role_id

        if user_data.profile_photo is not None:
            user.profile_photo = user_data.profile_photo

        if user_data.is_active is not None:
            user.is_active = user_data.is_active

        return await self.repository.update(user)

    async def toggle_user_status(
        self,
        user_id: int,
    ) -> User:
        user = await self.repository.get_user_by_id(user_id)
        if user is None:
            raise ValueError("User not found.")

        user.is_active = not user.is_active
        return await self.repository.update(user)

    async def activate_user(
        self,
        user_id: int,
    ) -> User:
        user = await self.repository.get_user_by_id(user_id)
        if user is None:
            raise ValueError("User not found.")

        user.is_active = True
        return await self.repository.update(user)

    async def deactivate_user(
        self,
        user_id: int,
    ) -> User:
        user = await self.repository.get_user_by_id(user_id)
        if user is None:
            raise ValueError("User not found.")

        user.is_active = False
        return await self.repository.update(user)

    async def delete_user(
        self,
        user_id: int,
    ):
        user = await self.repository.get_user_by_id(user_id)

        if user is None:
            raise ValueError("User Not Found.")

        return await self.repository.delete(user)