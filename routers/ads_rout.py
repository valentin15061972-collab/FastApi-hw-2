from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query, status
from app.schemas import Advertisement, AdvertisementCreate
from app.dependencies import get_ad, update_ad, delete_ad, search_ads, create_ad
from app.dependencies import get_current_user


router = APIRouter()


@router.post("/advertisement", response_model=Advertisement, summary="Create advertisement")
async def create_advertisement(advertisement: AdvertisementCreate, current_user: dict = Depends(get_current_user),):
    new_ad = await create_ad(
        title=advertisement.title,
        author=current_user["name"],
        description=advertisement.description,
        price=advertisement.price,
    )
    return new_ad


@router.get("/advertisement/{advertisement_id}", response_model=Advertisement, summary="Get advertisement")
async def get_advertisement_id(advertisement_id: int):
    result = await get_ad(advertisement_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return result


@router.get("/advertisement", summary="Search advertisements by query parameters")
async def search_advertisements_by_fields(
    id: int | None = Query(None, description="Search by id"),
    title: str | None = Query(None, description="Search by title"),
    description: str | None = Query(None, description="Search by description"),
    price: float | None = Query(None, description="Search by price"),
    author: str | None = Query(None, description="Search by author"),
    created_at: datetime | None = Query(None, description="Search by created_at"),
):
    return await search_ads(
        id=id,
        title=title,
        description=description,
        price=price,
        author=author,
        created_at=created_at,
    )


@router.patch("/advertisement/{advertisement_id}", response_model=Advertisement, summary="Update advertisement")
async def update_advertisement(advertisement_id: int, advertisement_data: AdvertisementCreate, current_user: dict = Depends(get_current_user)):
    existing = await get_ad(advertisement_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="advertisement not found")
    if current_user["group"] != "admin" and existing["author"] != current_user["name"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own advertisements",
        )
    updated = await update_ad(advertisement_id, advertisement_data.model_dump())
    return updated


@router.delete("/advertisement/{advertisement_id}", summary="Delete advertisement")
async def delete_ad_route(advertisement_id: int, current_user: dict = Depends(get_current_user)):
    existing = await get_ad(advertisement_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="advertisement not found")
    if current_user["group"] != "admin" and existing["author"] != current_user["name"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own advertisements",
        )
    deleted = await delete_ad(advertisement_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="advertisement not found")
    return {"message": "advertisement deleted"}


