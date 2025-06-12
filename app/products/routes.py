from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.logger import logger
from app.products.schemas import ProductCreate, ProductOut, ProductUpdate
from app.products.models import Product
from app.auth.utils import require_role
from app.auth.models import User

admin_router = APIRouter(prefix="/admin/products", tags=["Admin Products"])
public_router = APIRouter(prefix="/products", tags=["Public Products"])


# APIs can be accessed by Admins only
# Create product
@admin_router.post("/", response_model=ProductOut)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    new_product = Product(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    logger.info(f"Admin {current_user.email} created new product: {product.name}")
    return new_product


# Get all products (paginated)
@admin_router.get("/", response_model=List[ProductOut])
def get_all_products(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    logger.info(f"Admin {current_user.email} fetching all products | skip={skip} limit={limit}")
    return db.query(Product).offset(skip).limit(limit).all()


# Get product by ID
@admin_router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    logger.info(f"Admin {current_user.email} fetching product ID: {product_id}")
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        logger.warning(f"Product not found: ID {product_id}")
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# Update product details
@admin_router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    updated_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    logger.info(f"Admin {current_user.email} updating product ID: {product_id}")
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        logger.warning(f"Product not found for update: ID {product_id}")
        raise HTTPException(status_code=404, detail="Product not found")

    logger.debug(f"Updating fields: {updated_data.model_dump(exclude_unset=True)}")
    for field, value in updated_data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    logger.info(f"Product updated successfully: ID {product_id}")
    return product


# Delete product
@admin_router.delete("/{product_id}")
def delete_product(
    product_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role("admin"))
):
    logger.info(f"Admin {current_user.email} deleting product ID: {product_id}")
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        logger.warning(f"Delete failed - Product not found: ID {product_id}")
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    logger.info(f"Product deleted: ID {product_id}")
    return {"message": "Product deleted successfully"}


# APIs can be accessed by Anyone
# Get All Products (with pagination, sort, filter)
@public_router.get("/", response_model=List[ProductOut])
def public_get_products(
    skip: int = 0,  # Pagination
    limit: int = 10,  
    category: Optional[str] = None,  # Filtering
    sort_by: Optional[str] = Query(None, enum=["price", "name"]),  # Sorting
    order: Optional[str] = Query("asc", enum=["asc", "desc"]),  # Order direction
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db)
):
    logger.info(f"Fetching public products | category={category} min_price={min_price} max_price={max_price} sort_by={sort_by} order={order}")
    query = db.query(Product)

    if category:
        query = query.filter(Product.category == category)
    if sort_by:
        column = getattr(Product, sort_by)
        query = query.order_by(column.asc() if order == "asc" else column.desc())
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
        
    products = query.offset(skip).limit(limit).all()
    return products


# Search Products by Name or Category
@public_router.get("/search", response_model=List[ProductOut])
def search_products(
    keyword: str,
    db: Session = Depends(get_db)
):
    logger.info(f"Searching products with keyword: '{keyword}'")
    query = db.query(Product).filter(
        (Product.name.ilike(f"%{keyword}%")) |
        (Product.category.ilike(f"%{keyword}%"))
    )
    return query.all()


# Get Product by ID
@public_router.get("/{product_id}", response_model=ProductOut)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching public product ID: {product_id}")
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        logger.warning(f"Product not found: ID {product_id}")
        raise HTTPException(status_code=404, detail="Product not found")
    return product
