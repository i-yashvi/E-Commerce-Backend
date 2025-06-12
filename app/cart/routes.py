from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.logger import logger
from app.auth.utils import get_current_user, require_role
from app.auth.models import User
from app.cart.models import Cart
from app.cart.schemas import CartItemOut, CartItemCreate, CartItemUpdate
from app.products.models import Product

router = APIRouter(prefix="/cart", tags=["Cart"])


# Add item to cart
@router.post("/", response_model=CartItemOut)
def add_to_cart(
    item: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("user"))
):
    logger.info(f"[{current_user.email}] → POST /cart → Adding product {item.product_id} x {item.quantity}")

    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        logger.warning(f"Product not found: ID {item.product_id}")
        raise HTTPException(status_code=404, detail="Product not found")

    if product.stock == 0:  # Can't add product to cart, if don't have enough stock
        logger.warning(f"Out of stock: Product {product.name} (ID {item.product_id})")
        raise HTTPException(
            status_code=400,
            detail=f"Product is out of stock."
        )
    
    if item.quantity > product.stock:
        logger.warning(f"Requested quantity {item.quantity} exceeds stock {product.stock} for product {product.name}")
        raise HTTPException(
            status_code=400,
            detail=f"Cannot add {item.quantity} units to cart. Only {product.stock} left in stock."
        )

    cart_item = db.query(Cart).filter_by(
        user_id=current_user.id,
        product_id=item.product_id
    ).first()

    if cart_item:  # If item already exist in cart, just increase the quantity
        logger.debug(f"Existing cart item found. Increasing quantity from {cart_item.quantity} to {cart_item.quantity + item.quantity}")
        cart_item.quantity += item.quantity
    else:
        logger.debug(f"Creating new cart item for product {item.product_id}")
        cart_item = Cart(
            user_id=current_user.id,
            product_id=item.product_id,
            quantity=item.quantity
        )
        db.add(cart_item)

    db.commit()
    logger.info(f"[{current_user.email}] - Cart updated successfully for product {item.product_id}")
    db.refresh(cart_item)
    return cart_item


# View all items in cart
@router.get("/", response_model=list[CartItemOut])
def view_cart(db: Session = Depends(get_db), current_user: User = Depends(require_role("user"))):
    logger.info(f"[{current_user.email}] - Viewing cart")
    return db.query(Cart).filter_by(user_id=current_user.id).all()


# Update quantity of item in cart
@router.put("/{product_id}", response_model=CartItemOut)
def update_quantity(
    product_id: int, 
    update: CartItemUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role("user"))
    ):
    logger.info(f"[{current_user.email}] - Updating cart item: Product ID {product_id} to quantity {update.quantity}")
    cart_item = db.query(Cart).filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()

    if not cart_item:
        logger.warning(f"Cart item not found for user {current_user.email} and product ID {product_id}")
        raise HTTPException(status_code=404, detail="Item not found")

    if update.quantity == 0:
        db.delete(cart_item)
        db.commit()
        logger.info(f"Removing item from cart (quantity set to 0): Product ID {product_id}")
        return JSONResponse(content={"detail": "Item removed from cart"}, status_code=status.HTTP_200_OK)
    else:
        cart_item.quantity = update.quantity
        db.commit()
        db.refresh(cart_item)
        logger.debug(f"Cart quantity updated to {update.quantity} for product ID {product_id}")
        return cart_item


# Remove item from cart
@router.delete("/{product_id}")
def remove_item(
    product_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role("user"))
):
    logger.info(f"[{current_user.email}] - Removing item from cart: Product ID {product_id}")
    cart_item = db.query(Cart).filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()

    if not cart_item:
        logger.warning(f"Cart item not found for deletion: Product ID {product_id}")
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(cart_item)
    db.commit()
    logger.info(f"Item removed from cart: Product ID {product_id}")
    return {"message": "Item removed from cart"}
