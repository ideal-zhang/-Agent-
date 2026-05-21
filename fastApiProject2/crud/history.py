from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from models.history import History
from models.news import News


async def add_history(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    query = select(History).where(History.user_id == user_id, History.news_id == news_id)
    res = await db.execute(query)
    existing_history = res.scalar_one_or_none()
    if existing_history:
        existing_history.view_time = datetime.now()
        await db.commit()
        await db.refresh(existing_history)
        return existing_history
    else:
        histroy = History(user_id=user_id, news_id=news_id)
        db.add(histroy)
        await db.commit()
        await db.refresh(histroy)
        return histroy

async def get_history_list(
        db: AsyncSession,
        user_id: int,
        page: int=1,
        page_size: int=10
):
    offset = (page - 1) * page_size
    count_query = select(func.count(History.id)).where(History.user_id == user_id)
    count_res = await db.execute(count_query)
    count_total = count_res.scalar_one()

    query = (
        select(News, History.view_time.label("view_time"), History.id.label("history_id"))
        .join(History, History.news_id == News.id)
        .where(History.user_id == user_id)
        .order_by(History.view_time.desc())
        .offset(offset).limit(page_size)
    )
    res = await db.execute(query)
    rows = res.all()
    return rows, count_total

async def delete_history(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    stmt = delete(History).where(History.user_id == user_id, History.news_id == news_id)
    res = await db.execute(stmt)
    await db.commit()
    return res.rowcount > 0

async def clear_history(
        db: AsyncSession,
        user_id: int
):
    stmt = delete(History).where(History.user_id == user_id)
    res = await db.execute(stmt)
    await db.commit()
    return res.rowcount or 0

