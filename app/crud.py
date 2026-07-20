from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone
from typing import Optional, List



from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.password import hash_password
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.models.category import Category
from app.schemas.category import CategoryCreate
from app.models.cart import Cart
from app.schemas.cart import CartCreate
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.wishlist import Wishlist
from app.schemas.wishlist import WishlistCreate
from app.models.payment import Payment
from app.models.address import Address
from app.schemas.address import AddressCreate, AddressUpdate



# -------------------------------
# USER CRUD
# -------------------------------



def create_user(db: Session, user: UserCreate):
    db_user = User(
        full_name=user.full_name,
        email=user.email,
        password=hash_password(user.password),
        role="user"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_users(db: Session):
    return db.query(User).all()


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def update_user(db: Session, user_id: int, user: UserUpdate):
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    if user.full_name is not None:
        db_user.full_name = user.full_name

    if user.email is not None:
        db_user.email = user.email

    if user.password is not None:
        db_user.password = hash_password(user.password)

    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    db.delete(db_user)
    db.commit()
    return True


# -------------------------------
# PRODUCT CRUD
# -------------------------------

def create_product(db: Session, product: ProductCreate):
    db_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock,
        category_id=product.category_id
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def get_latest_products(db: Session, limit: int = 12):
    return db.query(Product).order_by(Product.id.desc()).limit(limit).all()


def get_products(
    db: Session,
    search: str = "",
    category_id: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    skip: int = 0,
    limit: int = 100,
    sort: str = "newest",
):
    query = db.query(Product)

    # --- Filters ---
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    if category_id is not None:
        query = query.filter(Product.category_id == category_id)

    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    # --- Sorting ---
    if sort == "price_low":
        query = query.order_by(Product.price.asc())
    elif sort == "price_high":
        query = query.order_by(Product.price.desc())
    elif sort == "name":
        query = query.order_by(Product.name.asc())
    else:  # default: newest
        query = query.order_by(Product.id.desc())

    return query.offset(skip).limit(limit).all()


def get_product(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()


def update_product(db: Session, product_id: int, product: ProductUpdate):
    db_product = get_product(db, product_id)
    if not db_product:
        return None

    if product.name is not None:
        db_product.name = product.name

    if product.description is not None:
        db_product.description = product.description

    if product.price is not None:
        db_product.price = product.price

    if product.stock is not None:
        db_product.stock = product.stock

    if product.category_id is not None:
        db_product.category_id = product.category_id

    if product.image is not None:
        db_product.image = product.image

    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int):
    db_product = get_product(db, product_id)
    if not db_product:
        return None
    db.delete(db_product)
    db.commit()
    return True


# ------------------------
# CATEGORY CRUD
# ------------------------

def create_category(db: Session, category: CategoryCreate):
    db_category = Category(
        name=category.name
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def get_categories(db: Session):
    return db.query(Category).all()


def get_category(db: Session, category_id: int):
    return db.query(Category).filter(
        Category.id == category_id
    ).first()


def get_category_by_name(db: Session, name: str):
    return db.query(Category).filter(
        Category.name == name
    ).first()


def delete_category(db: Session, category_id: int):
    category = get_category(db, category_id)
    if not category:
        return None
    db.delete(category)
    db.commit()
    return True



# ------------------------
# CART CRUD
# ------------------------





def add_to_cart(
    db: Session,
    user_id: int,
    cart: CartCreate
):
    product = get_product(db, cart.product_id)
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    existing_item = db.query(Cart).filter(
        Cart.user_id == user_id,
        Cart.product_id == cart.product_id
    ).first()

    if existing_item:
        # Only the additional quantity needs to be reserved
        additional = cart.quantity
        if product.stock < additional:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock. Only {product.stock} unit(s) available."
            )
        existing_item.quantity += additional
        product.stock -= additional
        db.commit()
        db.refresh(existing_item)
        return existing_item

    # New cart item
    if product.stock < cart.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient stock. Only {product.stock} unit(s) available."
        )
    if cart.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be at least 1."
        )

    product.stock -= cart.quantity
    db_cart = Cart(
        user_id=user_id,
        product_id=cart.product_id,
        quantity=cart.quantity
    )
    db.add(db_cart)
    db.commit()
    db.refresh(db_cart)
    return db_cart


def update_cart_quantity(
    db: Session,
    cart_id: int,
    new_quantity: int
):
    cart_item = db.query(Cart).filter(Cart.id == cart_id).first()
    if not cart_item:
        return None

    if new_quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be at least 1."
        )

    product = get_product(db, cart_item.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    diff = new_quantity - cart_item.quantity  # positive = increase, negative = decrease

    if diff > 0:
        # User wants more — check available stock
        if product.stock == 0:
            raise HTTPException(
                status_code=400,
                detail="Maximum available stock reached."
            )
        if product.stock < diff:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock. Only {product.stock} additional unit(s) available."
            )
        product.stock -= diff
    elif diff < 0:
        # User wants less — restore the released units
        product.stock += abs(diff)

    cart_item.quantity = new_quantity
    db.commit()
    db.refresh(cart_item)
    return cart_item


def get_cart(
    db: Session,
    user_id: int
):
    return (
        db.query(Cart)
        .options(joinedload(Cart.product))
        .filter(Cart.user_id == user_id)
        .all()
    )


def remove_from_cart(
    db: Session,
    cart_id: int
):
    cart = db.query(Cart).filter(Cart.id == cart_id).first()

    if not cart:
        return None

    # Restore reserved stock before deleting
    product = get_product(db, cart.product_id)
    if product:
        product.stock += cart.quantity

    db.delete(cart)
    db.commit()
    return True


def buy_now(
    db: Session,
    user_id: int,
    product_id: int,
    quantity: int,
    payment_method: Optional[str] = "Cash on Delivery",
    address_id: Optional[int] = None
):
    """
    Place an immediate order for a single product without requiring it to be
    in the cart beforehand.

    Strategy:
    - If the product is already in the user's cart, reuse that cart item
      (update its quantity if needed) so stock is not double-reserved, then
      checkout using ONLY that cart item. Other cart items remain untouched.
    - If it is not in the cart, add it temporarily using the normal
      add_to_cart path (which handles stock reservation), then place the
      order using only the newly added item. The order placement clears only
      the selected cart item.
    """
    if quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be at least 1."
        )

    product = get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    cart_item_ids_to_checkout = []

    # Check whether this product already lives in the user's cart.
    existing_cart_item = db.query(Cart).filter(
        Cart.user_id == user_id,
        Cart.product_id == product_id
    ).first()

    if existing_cart_item:
        # Reuse the existing cart item — adjust quantity if different.
        if existing_cart_item.quantity != quantity:
            update_cart_quantity(db, existing_cart_item.id, quantity)
        cart_item_ids_to_checkout.append(existing_cart_item.id)
    else:
        # Temporarily add the product to the cart (reserves stock).
        new_cart_item = add_to_cart(db, user_id, CartCreate(product_id=product_id, quantity=quantity))
        cart_item_ids_to_checkout.append(new_cart_item.id)

    # Place the order using only the selected cart item(s).
    # Other cart items remain in the cart untouched.
    return create_order(
        db,
        user_id,
        payment_method=payment_method,
        address_id=address_id,
        cart_item_ids=cart_item_ids_to_checkout
    )


# ---------------------------------------------
#         order crud
# --------------------------------------   ------





def create_order(
    db: Session,
    user_id: int,
    payment_method: Optional[str] = "Cash on Delivery",
    address_id: Optional[int] = None,
    cart_item_ids: Optional[List[int]] = None
):
    if cart_item_ids:
        cart_items = db.query(Cart).filter(
            Cart.user_id == user_id,
            Cart.id.in_(cart_item_ids)
        ).all()
    else:
        cart_items = db.query(Cart).filter(
            Cart.user_id == user_id
        ).all()

    if not cart_items:
        return None

    # Verify all products still exist (stock was already reserved at add-to-cart time)
    for item in cart_items:
        product = get_product(db, item.product_id)
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product with ID {item.product_id} not found"
            )

    # Resolve shipping address
    shipping_address = "N/A"
    if address_id:
        addr = db.query(Address).filter(Address.id == address_id, Address.user_id == user_id).first()
        if addr:
            shipping_address = f"{addr.street_address}, {addr.city}, {addr.state or ''}, {addr.postal_code}, {addr.country}"
    else:
        addr = db.query(Address).filter(Address.user_id == user_id).order_by(Address.id.desc()).first()
        if addr:
            shipping_address = f"{addr.street_address}, {addr.city}, {addr.state or ''}, {addr.postal_code}, {addr.country}"

    total = 0

    order = Order(
        user_id=user_id,
        status="Pending",
        created_at=datetime.now(timezone.utc),
        payment_method=payment_method or "Cash on Delivery",
        shipping_address=shipping_address
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    for item in cart_items:
        product = get_product(db, item.product_id)
        total += product.price * item.quantity
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item.quantity,
            price=product.price
        )
        # Stock was already decremented when this item was added to the cart.
        # Do NOT decrement again here.
        db.add(order_item)
        db.delete(item)

    order.total_price = total
    db.commit()
    db.refresh(order)
    return order


def get_orders(db: Session, user_id: int):
    return db.query(Order).filter(
        Order.user_id == user_id
    ).order_by(Order.created_at.desc(), Order.id.desc()).all()



def get_order(db: Session, order_id: int):

    return db.query(Order).filter(
        Order.id == order_id
    ).first()


def get_order_detail(db: Session, order_id: int, user_id: int):
    """Return a single order with all items+products eager-loaded.
    Returns None if the order doesn't exist or belongs to a different user."""
    return (
        db.query(Order)
        .options(
            joinedload(Order.items).joinedload(OrderItem.product)
        )
        .filter(
            Order.id == order_id,
            Order.user_id == user_id
        )
        .first()
    )


def update_order_status(
    db: Session,
    order_id: int,
    status: str
):

    order = get_order(db, order_id)

    if not order:
        return None

    order.status = status

    db.commit()

    db.refresh(order)

    return order



# -------------------------------
# WISHLIST CRUD
# -------------------------------


def add_to_wishlist(db: Session, user_id: int, wishlist: WishlistCreate):
    # Check if product exists
    product = get_product(db, wishlist.product_id)
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    # Check for duplicate entry
    existing = db.query(Wishlist).filter(
        Wishlist.user_id == user_id,
        Wishlist.product_id == wishlist.product_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Product already in wishlist"
        )

    db_wishlist = Wishlist(
        user_id=user_id,
        product_id=wishlist.product_id
    )

    db.add(db_wishlist)
    db.commit()
    db.refresh(db_wishlist)
    return db_wishlist


def get_wishlist(db: Session, user_id: int):
    return (
        db.query(Wishlist)
        .options(joinedload(Wishlist.product))
        .filter(Wishlist.user_id == user_id)
        .all()
    )

def get_wishlist_item(db: Session, wishlist_id: int):
    return db.query(Wishlist).filter(
        Wishlist.id == wishlist_id
    ).first()


def remove_from_wishlist(db: Session, wishlist_id: int, user_id: int):
    item = db.query(Wishlist).filter(
        Wishlist.id == wishlist_id,
        Wishlist.user_id == user_id
    ).first()

    if not item:
        return None

    db.delete(item)
    db.commit()
    return True




# _________________________________________________

#                         payment crud

# ------------------------------------------------------





def create_payment(
    db: Session,
    order_id: int,
    amount: float,
    payment_method: str
):

    payment = Payment(
        order_id=order_id,
        amount=amount,
        payment_method=payment_method,
        payment_status="Pending"
    )

    db.add(payment)

    # Sync payment_method to Order
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        order.payment_method = payment_method

    db.commit()

    db.refresh(payment)

    return payment



def get_payments(db: Session):

    return db.query(Payment).all()


def get_payment(db: Session, payment_id: int):

    return db.query(Payment).filter(
        Payment.id == payment_id
    ).first()


def update_payment_status(
    db: Session,
    payment_id: int,
    status: str
):

    payment = get_payment(
        db,
        payment_id
    )

    if not payment:
        return None

    payment.payment_status = status

    db.commit()

    db.refresh(payment)

    return payment


# -------------------------------
# ADDRESS CRUD
# -------------------------------

def create_address(db: Session, address: AddressCreate, user_id: int):
    db_address = Address(
        user_id=user_id,
        address_type=address.address_type,
        street_address=address.street_address,
        city=address.city,
        state=address.state,
        postal_code=address.postal_code,
        country=address.country,
        phone_number=address.phone_number
    )
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address


def get_addresses(db: Session, user_id: int):
    return db.query(Address).filter(Address.user_id == user_id).all()


def get_address(db: Session, address_id: int, user_id: int):
    return db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == user_id
    ).first()


def update_address(db: Session, address_id: int, address: AddressUpdate, user_id: int):
    db_address = get_address(db, address_id, user_id)
    if not db_address:
        return None

    if address.address_type is not None:
        db_address.address_type = address.address_type
    if address.street_address is not None:
        db_address.street_address = address.street_address
    if address.city is not None:
        db_address.city = address.city
    if address.state is not None:
        db_address.state = address.state
    if address.postal_code is not None:
        db_address.postal_code = address.postal_code
    if address.country is not None:
        db_address.country = address.country
    if address.phone_number is not None:
        db_address.phone_number = address.phone_number

    db.commit()
    db.refresh(db_address)
    return db_address


def delete_address(db: Session, address_id: int, user_id: int):
    db_address = get_address(db, address_id, user_id)
    if not db_address:
        return None
    db.delete(db_address)
    db.commit()
    return True
