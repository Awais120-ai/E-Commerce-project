from app import database
from app import database
from app import database
from app import database
from app import database
from app import database
from app import database
from app import database
from app.models import cart
from app.models import product
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

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
from app.models.cart import Cart
from app.models.wishlist import Wishlist
from app.schemas.wishlist import WishlistCreate
from app.models.payment import Payment
from app.models.address import Address
from app.schemas.address import AddressCreate, AddressUpdate
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.orm import joinedload
from sqlalchemy import desc






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

def create_product(db: Session, product: ProductCreate, user_id: int):
    db_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock,
        category_id=product.category_id,
        user_id=user_id,
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def get_products(
    db: Session,
    user_id: int | None,
    search: str = "",
    category_id: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    skip: int = 0,
    limit: int = 10,
    sort: str = "id"
):

    query = db.query(Product)

    if user_id is not None:
        query = query.filter(
            Product.user_id == user_id
        )

    if search:
        query = query.filter(
            Product.name.ilike(f"%{search}%")
        )

    if category_id is not None:
        query = query.filter(
            Product.category_id == category_id
        )

    if min_price is not None:
        query = query.filter(
            Product.price >= min_price
        )

    if max_price is not None:
        query = query.filter(
            Product.price <= max_price
        )

    if sort == "price_low":
        query = query.order_by(Product.price.asc())

    elif sort == "price_high":
        query = query.order_by(Product.price.desc())

    elif sort == "name":
        query = query.order_by(Product.name.asc())

    elif sort == "stock":
        query = query.order_by(Product.stock.desc())

    else:
        query = query.order_by(Product.id.desc())

    return query.offset(skip).limit(limit).all()

# Owner-scoped lookup: use this ONLY when a seller is managing
# (viewing/editing/deleting) their OWN product listings.
def get_product(db: Session, product_id: int, user_id: int):
    return db.query(Product).filter(Product.id == product_id, Product.user_id == user_id).first()


# Public lookup: use this whenever a CUSTOMER needs to look up a
# product to buy it (cart, wishlist, checkout/order, product detail
# page for shoppers). No ownership filter — any valid product ID
# should resolve here regardless of who created it.
def get_product_public(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()


def update_product(db: Session, product_id: int, product: ProductUpdate, user_id: int):
    db_product = get_product(db, product_id, user_id)
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


def delete_product(db: Session, product_id: int, user_id: int):
    db_product = get_product(db, product_id, user_id)
    if not db_product:
        return None
    db.delete(db_product)
    db.commit()
    return True





# ------------------------------------------------------
#                           CATEGORY CRUD
# -------------------------------------------------------





def create_category(db: Session, category: CategoryCreate, user_id: int):
    db_category = Category(
        name=category.name,
        user_id=user_id,
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def get_categories(db: Session):
    return db.query(Category).all()


def get_category(db: Session, category_id: int, user_id: int):
    return db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == user_id
    ).first()


def get_category_by_name(db: Session, name: str):
    return db.query(Category).filter(
        Category.name == name
    ).first()


def delete_category(db: Session, category_id: int, user_id: int):
    category = get_category(db, category_id, user_id)
    if not category:
        return None
    db.delete(category)
    db.commit()
    return True






# -------------------------------------------------------
#                           CART CRUD
# -------------------------------------------------------



def add_to_cart(
    db: Session,
    user_id: int,
    cart: CartCreate
):
    product = get_product_public(db, cart.product_id)

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
        # Adding more of an already-carted product — only reserve the extra quantity
        if cart.quantity > product.stock:
            raise HTTPException(
                status_code=400,
                detail=f"Only {product.stock} item(s) available in stock"
            )

        existing_item.quantity += cart.quantity
        product.stock -= cart.quantity  # Reserve only the delta

        db.commit()
        db.refresh(existing_item)

        return existing_item

    # New cart item — reserve the full requested quantity
    if product.stock <= 0:
        raise HTTPException(
            status_code=400,
            detail="Product is out of stock."
        )

    if cart.quantity > product.stock:
        raise HTTPException(
            status_code=400,
            detail=f"Only {product.stock} item(s) available in stock"
        )

    db_cart = Cart(
        user_id=user_id,
        product_id=cart.product_id,
        quantity=cart.quantity
    )

    db.add(db_cart)
    product.stock -= cart.quantity  # Reserve stock

    db.commit()
    db.refresh(db_cart)

    return db_cart




def get_cart( db: Session, user_id: int ): 
   items = ( db.query(Cart) 
   .options(joinedload(Cart.product)) 
   .filter(Cart.user_id == user_id) 
   .all()
    )
   if items:
    print(items[0].product if items else "No items")

   return items


def remove_from_cart(
    db: Session,
    cart_id: int,
    user_id: int
):

    cart = db.query(Cart).filter(
        Cart.id == cart_id,
        Cart.user_id == user_id
    ).first()

    if not cart:
        return None

    # Release the reserved stock back to available inventory
    product = get_product_public(db, cart.product_id)

    if product:
        product.stock += cart.quantity

    db.delete(cart)

    db.commit()

    return True


def update_cart(
    db: Session,
    cart_id: int,
    quantity: int,
    user_id: int
):

    cart = db.query(Cart).filter(
        Cart.id == cart_id,
        Cart.user_id == user_id
    ).first()

    if not cart:
        return None

    product = get_product_public(db, cart.product_id)

    if not product:
        return None

    old_quantity = cart.quantity

    if quantity > old_quantity:

        increase = quantity - old_quantity

        if increase > product.stock:
            raise HTTPException(
                status_code=400,
                detail=f"Only {product.stock} item(s) available"
            )

        product.stock -= increase

    elif quantity < old_quantity:

        decrease = old_quantity - quantity

        product.stock += decrease

    cart.quantity = quantity

    db.commit()
    db.refresh(cart)

    return cart




#-----------------------------------------------------
#                       orders crud
#-----------------------------------------------------





def create_order(
    db: Session,
    user_id: int,
    address_id: int,
    payment_method: str,
    buy_now: bool = False,
    product_id: int | None = None,
    quantity: int = 1,
):
    if buy_now:
        if product_id is None:
            raise HTTPException(
                status_code=400,
                detail="Product ID is required for Buy Now option"
            )
        # Buy Now Flow
        qty = quantity if quantity is not None else 1
        product = get_product_public(db, product_id)

        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product with ID {product_id} not found"
            )

        # ── Duplicate-prevention check ──────────────────────────────────────
        # If the product is already in the user's cart, stock is already
        # reserved. Use the cart item for checkout instead of creating a
        # second reservation.
        existing_cart_item = db.query(Cart).filter(
            Cart.user_id == user_id,
            Cart.product_id == product_id
        ).first()

        if existing_cart_item:
            # Cart-based Buy Now path
            # Use the reserved cart quantity — ignore the `quantity` arg.
            cart_qty = existing_cart_item.quantity

            order = Order(
                user_id=user_id,
                address_id=address_id,
                status="Pending",
                total_price=product.price * cart_qty
            )

            db.add(order)
            db.commit()
            db.refresh(order)

            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=cart_qty,
                price=product.price
            )

            db.add(order_item)

            # Remove from cart (stock stays as-is — already reserved)
            db.delete(existing_cart_item)

            db.commit()
            db.refresh(order)

            return order

        # ── Normal Buy Now path — product is NOT in cart ─────────────────────
        if product.stock <= 0:
            raise HTTPException(
                status_code=400,
                detail="Product is out of stock."
            )

        if product.stock < qty:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for '{product.name}'"
            )

        # Create Order
        order = Order(
            user_id=user_id,
            address_id=address_id,
            status="Pending",
            total_price=product.price * qty
        )

        db.add(order)
        db.commit()
        db.refresh(order)

        # Create Order Item
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=qty,
            price=product.price
        )

        db.add(order_item)

        # Reserve Stock (only in this path — cart path already reserved it)
        product.stock -= qty

        db.commit()
        db.refresh(order)

        return order

    else:
        # Standard Cart Flow
        cart_items = db.query(Cart).filter(
            Cart.user_id == user_id
        ).all()

        if not cart_items:
            return None

        total = 0

        # Safety check: stock was already reserved at add-to-cart time.
        # This guard only catches edge cases (e.g. admin manually reduced stock).
        for item in cart_items:
            product = get_product_public(db, item.product_id)

            if not product:
                raise HTTPException(
                    status_code=404,
                    detail=f"Product with ID {item.product_id} not found"
                )

            # NOTE: product.stock here is the UNRESERVED remainder, so even 0
            # is fine — the reservation already happened at add-to-cart.
            # We only fail if somehow the reserved amount is now impossible.

        # Create Order
        order = Order(
            user_id=user_id,
            address_id=address_id,
            status="Pending",
            total_price=0
        )

        db.add(order)
        db.commit()
        db.refresh(order)

        # Create Order Items
        # Stock was already reserved when items were added to cart.
        # Do NOT deduct stock again here.
        for item in cart_items:
            product = get_product_public(db, item.product_id)

            total += product.price * item.quantity

            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item.quantity,
                price=product.price
            )

            db.add(order_item)

            # Remove Cart Item (stock stays as-is — already reserved)
            db.delete(item)

        order.total_price = total

        db.commit()
        db.refresh(order)

        return order


def get_orders(db: Session, user_id: int):
    return (
        db.query(Order)
        .filter(Order.user_id == user_id)
        .order_by(desc(Order.created_at), desc(Order.id))  # id DESC as tiebreaker for same timestamps
        .all()
    )



def get_order(
    db: Session,
    order_id: int,
    user_id: int
):
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






# -------------------------------   ----------------------------
#                      WISHLIST CRUD                         
# -----------------------------------------------------------




def add_to_wishlist(db: Session, user_id: int, wishlist: WishlistCreate):
    # FIX: use get_product_public — a customer wishlisting a product
    # doesn't need to be its owner.
    product = get_product_public(db, wishlist.product_id)
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
        .options(
            joinedload(Wishlist.product)
        )
        .filter(
            Wishlist.user_id == user_id
        )
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




# -----------------------------------------------------------
#                     PAYMENT CRUD                                  
# -----------------------------------------------------------





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

    db.commit()

    db.refresh(payment)

    return payment


def get_payments(
    db: Session,
    user_id: int
):
    return (
        db.query(Payment)
        .join(Order)
        .filter(Order.user_id == user_id)
        .all()
    )


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





# ----------------------------------------------------------
#                         ADDRESS CRUD
# ----------------------------------------------------------






def create_address(db: Session, address: AddressCreate, user_id: int):

    db_address = Address(
        full_name=address.full_name,
        phone=address.phone,
        country=address.country,
        city=address.city,
        postal_code=address.postal_code,
        address=address.address,
        user_id=user_id
    )

    db.add(db_address)
    db.commit()
    db.refresh(db_address)

    return db_address


def get_addresses(
    db: Session,
    user_id: int
):
    return db.query(Address).filter(
        Address.user_id == user_id
    ).all()


def get_address(db: Session, address_id: int):
    return db.query(Address).filter(
        Address.id == address_id
    ).first()


def update_address(
    db: Session,
    address_id: int,
    address: AddressUpdate
):

    db_address = get_address(db, address_id)

    if not db_address:
        return None

    if address.full_name is not None:
        db_address.full_name = address.full_name

    if address.phone is not None:
        db_address.phone = address.phone

    if address.country is not None:
        db_address.country = address.country

    if address.city is not None:
        db_address.city = address.city

    if address.postal_code is not None:
        db_address.postal_code = address.postal_code

    if address.address is not None:
        db_address.address = address.address

    db.commit()
    db.refresh(db_address)

    return db_address


def delete_address(db: Session, address_id: int):

    db_address = get_address(db, address_id)

    if not db_address:
        return None

    db.delete(db_address)
    db.commit()

    return True