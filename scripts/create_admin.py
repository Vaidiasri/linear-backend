import asyncio
import sys
import os

# Add the parent directory to sys.path to resolve 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.lib.database import AsyncSessionLocal
from app.services.user import UserService
from app.schemas.user import UserCreate
from app.model.user import UserRole
from app import crud


async def create_admin():
    async with AsyncSessionLocal() as session:
        email = "admin@example.com"
        password = "password123"
        full_name = "Admin User"

        # Check if user exists
        existing_user = await crud.user.get_by_email(session, email=email)
        if existing_user:
            print(f"User {email} already exists.")
            # Update role to ADMIN if not already
            if existing_user.role != UserRole.ADMIN:
                print(f"Updating role for {email} to ADMIN...")
                existing_user.role = UserRole.ADMIN
                session.add(existing_user)
                await session.commit()
                print("Role updated successfully!")
            else:
                print(f"User {email} is already an ADMIN.")
            return

        print(f"Creating new admin user: {email}")
        user_in = UserCreate(email=email, password=password, full_name=full_name)

        new_user = await UserService.create(session, user_in=user_in)

        # Now promote to ADMIN
        new_user.role = UserRole.ADMIN
        session.add(new_user)
        await session.commit()

        print("Admin user created successfully!")
        print(f"Email: {email}")
        print(f"Password: {password}")


if __name__ == "__main__":
    asyncio.run(create_admin())
