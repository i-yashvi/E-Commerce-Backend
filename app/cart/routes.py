from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
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
    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.stock == 0:  # Can't add product to cart, if don't have enough stock
        raise HTTPException(
            status_code=400,
            detail=f"Product is out of stock."
        )
    elif item.quantity > product.stock:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot add {item.quantity} units to cart. Only {product.stock} left in stock."
        )

    cart_item = db.query(Cart).filter_by(
        user_id=current_user.id,
        product_id=item.product_id
    ).first()

    if cart_item:  # If item already exist in cart, just increase the quantity
        cart_item.quantity += item.quantity
    else:
        cart_item = Cart(
            user_id=current_user.id,
            product_id=item.product_id,
            quantity=item.quantity
        )
        db.add(cart_item)

    db.commit()
    db.refresh(cart_item)
    return cart_item


# View all items in cart
@router.get("/", response_model=list[CartItemOut])
def view_cart(db: Session = Depends(get_db), current_user: User = Depends(require_role("user"))):
    return db.query(Cart).filter_by(user_id=current_user.id).all()


# Update quantity of item in cart
@router.put("/{product_id}", response_model=CartItemOut)
def update_quantity(
    product_id: int, 
    update: CartItemUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role("user"))
    ):
    cart_item = db.query(Cart).filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found")

    if update.quantity == 0:  # If the updated quantity is 0, remove the item from cart
        db.delete(cart_item)
    
    cart_item.quantity = update.quantity
    db.commit()
    db.refresh(cart_item)
    return cart_item


# Remove item from cart
@router.delete("/{product_id}")
def remove_item(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("user"))):
    cart_item = db.query(Cart).filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(cart_item)
    db.commit()
    return {"message": "Item removed from cart"}
