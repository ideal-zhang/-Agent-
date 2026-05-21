from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from models.news import Category, News
from cache.news_cache import get_cache_categories, set_cache_categories, get_cache_news_list, set_cache_news_list
from schemas.base import NewsItemBase


async def get_categories(db:AsyncSession , skip: int = 0, limit: int = 100):
    cached_categories = await get_cache_categories()
    if cached_categories:
        return cached_categories

    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    categories = result.scalars().all()
    if categories:
        categories = jsonable_encoder(categories)
        await set_cache_categories(categories)
async def get_news_list(db:AsyncSession , category_id: int, skip: int = 0, limit: int = 10):

    page = skip // limit +1
    cached_list = await get_cache_news_list(category_id, page, limit)
    if cached_list:
        # return cached_list 要的是orm对象
        return [News(**item) for item in cached_list]
    # 查询的是指定分类下的所有新闻
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    news_list = result.scalars().all()
    # 先把ORM数据转换字典才能写入缓存
    # ORM转成Pydantic，再转为字典
    # by_alias=False不适用别名，保存Python风格，因为Redis数据是给后端用的
    # 写入缓存
    if news_list:
        news_data = [NewsItemBase.model_validate(item).model_dump(mode="json", by_alias=False) for item in news_list]
        await set_cache_news_list(category_id,page, limit, news_data)
    return news_list


async def get_news_count(db:AsyncSession , category_id: int):
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()

async def get_news_detail(db:AsyncSession , news_id: int):
    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def increase_news_views(db:AsyncSession ,  news_id: int):
    stmt = update(News).where(News.id == news_id).values(views = News.views + 1)
    res = await db.execute(stmt)
    await db.commit()

    return res.rowcount > 0

async def get_realated_news(db:AsyncSession , news_id: int, category_id: int, limit: int = 5):
    stmt = select(News).where(
        News.id == news_id,
        News.category_id == category_id
    ).order_by(
        News.views.desc(),
        News.publish_time.desc()
    ).limit(limit)
    result = await db.execute(stmt)
    related_news = result.scalars().all()
    return [{
        "id": news_detail.id,
        "title": news_detail.title,
        "content": news_detail.content,
        "image": news_detail.image,
        "author": news_detail.author,
        "publishTime": news_detail.publish_time,
        "categoryId": news_detail.category_id,
        "views": news_detail.views,
    }for news_detail in related_news]