from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query, status
from app.schemas import Ad, AdCreate
from app.db import ads_database
from app.dependencies import get_current_user

router = APIRouter()


@router.post("/advertisement", response_model=Ad, summary="Create ad")
def create_ad(
    ad: AdCreate,
    current_user: dict = Depends(get_current_user),
):
    new_ad = ad.model_dump()
    new_ad["id"] = len(ads_database) + 1
    new_ad["author"] = current_user["name"]
    new_ad["created_at"] = datetime.now()
    ads_database.append(new_ad)
    return new_ad


@router.get("/advertisement/{advertisement_id}", response_model=Ad, summary="Get ad")
def get_ad(ad_id: int):
    for idx, el in enumerate(ads_database):
        if el["id"] == ad_id:
            return el
    raise HTTPException(status_code=404, detail="Ad not found")


@router.patch("/advertisement/{advertisement_id}", response_model=Ad, summary="Update ad")
def update_ad(
    ad_id: int,
    ad: AdCreate,
    current_user: dict = Depends(get_current_user),
):
    for idx, el in enumerate(ads_database):
        if el["id"] == ad_id:
            if current_user["group"] != "admin" and el["author"] != current_user["name"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only update your own ads",
                )
            updated_ad = ad.model_dump()
            updated_ad["id"] = ad_id
            updated_ad["author"] = el["author"]
            updated_ad["created_at"] = el["created_at"]
            ads_database[idx] = updated_ad
            return updated_ad
    raise HTTPException(status_code=404, detail="Ad not found")


@router.delete("/advertisement/{advertisement_id}", summary="Delete ad")
def delete_ad(
    ad_id: int,
    current_user: dict = Depends(get_current_user),
):
    for idx, el in enumerate(ads_database):
        if el["id"] == ad_id:
            if current_user["group"] != "admin" and el["author"] != current_user["name"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only delete your own ads",
                )
            del ads_database[idx]
            return {"message": "Ad deleted"}
    raise HTTPException(status_code=404, detail="Ad not found")


@router.get("/advertisement", summary="Search ads by query parameters")
def search_ads(
    id: int | None = Query(None, description="Search ads by id"),
    title: str | None = Query(None, description="Search by title"),
    description: str | None = Query(None, description="Search by description"),
    price: float | None = Query(None, description="Search by price"),
    author: str | None = Query(None, description="Search by author"),
    created_at: datetime | None = Query(None, description="Search by created_at"),
):
    results = []
    for ad in ads_database:
        match = True
        if id is not None and ad["id"] != id:
            match = False
        if title is not None and title.lower() not in ad["title"].lower():
            match = False
        if description is not None and ad.get("description") and description.lower() not in ad["description"].lower():
            match = False
        if price is not None and ad.get("price") != price:
            match = False
        if author is not None and author.lower() not in ad["author"].lower():
            match = False
        if created_at is not None:
            ad_date = ad.get("created_at")
            if ad_date and hasattr(ad_date, "date"):
                if ad_date.date() < created_at.date():
                    match = False
            elif ad_date:
                if ad_date < created_at:
                    match = False
            else:
                match = False
        if match:
            results.append(ad)
    return results
