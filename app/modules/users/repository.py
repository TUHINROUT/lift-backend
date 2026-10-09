from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.modules.users.models import User
from app.modules.roles.models import Role

class UsersRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_id(
        self,
        user_id: int,
    ) -> User | None:

        stmt = (
            select(User)
            .options(
                selectinload(User.role),
                selectinload(User.department),
                selectinload(User.designation),
            )
            .where(User.id == user_id)
        )
        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_by_email(
        self,
        email: str,
    ) -> User | None:

        stmt = select(User).where(User.email == email)

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()


    async def get_last_user(
        self,
    ) -> User | None:

        stmt = (
            select(User)
            .order_by(User.id.desc())
            .limit(1)
        )

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()


    async def create(
        self,
        user: User,
    ) -> User:

        self.db.add(user)

        await self.db.commit()

        stmt = (
            select(User)
            .options(
                selectinload(User.role),
                selectinload(User.department),
                selectinload(User.designation),
            )
            .where(User.id == user.id)
        )

        result = await self.db.execute(stmt)

        return result.scalar_one()


    async def get_all(
        self,
    ) -> list[User]:

        stmt = (
            select(User)
            .options(
                selectinload(User.role),
                selectinload(User.department),
                selectinload(User.designation),
            )
            .order_by(User.first_name)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


    async def get_active_admins_and_managers(
        self,
    ) -> list[User]:
        stmt = (
            select(User)
            .join(User.role)
            .where(
                User.is_active == True,
                Role.name.in_(["ADMIN", "MANAGER"]),
            )
                .order_by(User.first_name)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def search_by_name(
        self,
        name: str,
    ) -> list[User]:

        search = f"%{name.strip()}%"

        stmt = (
            select(User)
            .options(
                selectinload(User.role),
                selectinload(User.department),
                selectinload(User.designation),
            )
            .where(
                or_(
                    User.first_name.ilike(search),
                    User.last_name.ilike(search),
                )
            )
            .order_by(User.first_name)
        )

        result = await self.db.execute(stmt)

        return list(result.scalars().all())


    async def update(
        self,
        user: User,
    ) -> User:
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete(self, user:User,)-> None:
        await self.db.delete(user)
        await self.db.commit()


    