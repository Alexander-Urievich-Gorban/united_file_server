from fastapi import Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import User


async def get_current_user(
    secret: str = Header(None),
    db: AsyncSession = Depends(get_db)
) -> User:
    if not secret:
        raise HTTPException(status_code=401, detail="SECRET header missing")

    result = await db.execute(
        select(User).where(User.api_key == secret)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=403, detail="Invalid API key")

    return user
