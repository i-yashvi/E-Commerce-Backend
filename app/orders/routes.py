from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.auth.models import User
from app.auth.utils import get_current_user, require_role
from app.core.database import get_db
from app.cart.models import Cart
from app.orders.models import Order, OrderItem, OrderStatus
from app.orders.schemas import OrderOut, OrderSummary
from app.products.models import Product

order_router = APIRouter(prefix="/orders", tags=["Orders"])
checkout_router = APIRouter(prefix="/checkout", tags=["Orders"])


# Create order & clear cart
@checkout_router.post("/", response_model=OrderOut)
def checkout(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("user"))
):
    cart_items = db.query(Cart).filter(Cart.user_id == current_user.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total = 0
    order = Order(user_id=current_user.id)

    db.add(order)
    db.flush()  # so we get order.id

    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            continue  
        line_total = product.price * item.quantity
        total += line_total

        db.add(OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item.quantity,
            price_at_purchase=product.price
        ))

    order.total_amount = total
    order.status = OrderStatus.paid  # Simulate payment success
    db.query(Cart).filter(Cart.user_id == current_user.id).delete()
    db.commit()
    db.refresh(order)
    return order


# Order history
@order_router.get("/", response_model=List[OrderSummary])
def order_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("user"))
):
    return db.query(Order).filter(Order.user_id == current_user.id).order_by(Order.created_at.desc()).all()


# Order details
@order_router.get("/{order_id}", response_model=OrderOut)
def order_detail(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("user"))
):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
