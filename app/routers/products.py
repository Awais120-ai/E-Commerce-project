from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.user import User
import app.crud as crud
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse

import os
import shutil

from fastapi import UploadFile, File

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.post("/", response_model=ProductResponse)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if product.category_id is not None:
        category = crud.get_category(db, product.category_id, current_user.id)
        if not category:
            raise HTTPException(
                status_code=404,
                detail="Category not found"
            )
    return crud.create_product(db, product, current_user.id)


@router.get("/", response_model=list[ProductResponse])
def get_products(
    search: str = "",
    skip: int = 0,
    limit: int = 10,
    sort: str = "id",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return crud.get_products(
        db=db,
        user_id=current_user.id,
        search=search,
        skip=skip,
        limit=limit,
        sort=sort
    )

@router.get("", response_model=list[ProductResponse])
def list_products_alias(
    search: str = "",
    skip: int = 0,
    limit: int = 10,
    sort: str = "id",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Alias for `/products/` to handle requests without trailing slash.
    Calls the same logic as `get_products`.
    """
    return crud.get_products(
        db=db,
        user_id=current_user.id,
        search=search,
        skip=skip,
        limit=limit,
        sort=sort,
    )

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = crud.get_product(db, product_id, current_user.id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if product.category_id is not None:
        category = crud.get_category(db, product.category_id, current_user.id)
        if not category:
            raise HTTPException(
                status_code=400,
                detail="Category not found"
            )
    updated = crud.update_product(db, product_id, product, current_user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    deleted = crud.delete_product(db, product_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}


@router.post("/{product_id}/image")
def upload_product_image(
    product_id: int,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    product = crud.get_product(db, product_id, current_user.id)

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    os.makedirs("uploads/products", exist_ok=True)

    filename = f"{product_id}_{image.filename}"

    filepath = os.path.join(
        "uploads/products",
        filename
    )

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    product.image = filename

    db.commit()

    return {
        "message": "Image uploaded successfully",
        "image": filename
    }