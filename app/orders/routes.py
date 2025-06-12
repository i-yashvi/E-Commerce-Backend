from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.logger import logger
from app.auth.models import User
from app.auth.utils import get_current_user, require_role
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
    logger.info(f"[{current_user.email}] - Checkout initiated")
    cart_items = db.query(Cart).filter(Cart.user_id == current_user.id).all()
    if not cart_items:
        logger.warning(f"Checkout failed - Cart empty for user {current_user.email}")
        raise HTTPException(status_code=400, detail="Cart is empty")

    total = 0
    order = Order(user_id=current_user.id)
    db.add(order)
    db.flush()  # so we get order.id

    for item in cart_items:  # For every product in the cart
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product ID {item.product_id} not found")
        
        logger.debug(f"Checking product stock for {product.name} - Requested: {item.quantity}, Available: {product.stock}") 
        if product.stock < item.quantity:  # If enough stock not exist as mentioned in cart, then don't checkout that item
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for product '{product.name}'. Available: {product.stock}, Requested: {item.quantity}"
            )
        
        # Deduct stock here AFTER validation, and checkout
        product.stock -= item.quantity
        db.add(OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item.quantity,
            price_at_purchase=product.price
        ))
        total += product.price * item.quantity

    order.total_amount = total
    order.status = OrderStatus.paid  # Simulate payment success (Dummy payment)
    db.query(Cart).filter(Cart.user_id == current_user.id).delete()
    
    db.commit()
    db.refresh(order)
    logger.info(f"Order #{order.id} placed by user {current_user.email} | Total: {order.total_amount}")
    return order


# Order history of the user
@order_router.get("/", response_model=List[OrderSummary])
def order_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("user"))
):
    logger.info(f"[{current_user.email}] - Fetching order history")
    return db.query(Order).filter(Order.user_id == current_user.id).order_by(Order.created_at.desc()).all()


# Particular order details
@order_router.get("/{order_id}", response_model=OrderOut)
def order_detail(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("user"))
):
    logger.info(f"[{current_user.email}] - Fetching details for Order ID {order_id}")
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        logger.warning(f"Order not found: ID {order_id} for user {current_user.email}")
        raise HTTPException(status_code=404, detail="Order not found")
    return order
