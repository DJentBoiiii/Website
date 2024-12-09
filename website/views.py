from flask import Blueprint, render_template, flash, redirect, request, jsonify, url_for
from .models import Product, Cart, Order, Wishlist
from flask_login import login_required, current_user
from . import db
from intasend import APIService
from .post_handler import NovaPoshtaAPI


from sqlalchemy import or_


views = Blueprint('views', __name__)

API_KEY = 'Key'


@views.route('/')
def home():
    # Отримуємо списки для бокової панелі
    tool_categories = Product.query.filter_by(is_product_instrument=True).with_entities(Product.product_type).distinct().all()
    accessory_categories = Product.query.filter_by(is_product_instrument=False).with_entities(Product.product_type).distinct().all()
    tool_manufacturers = Product.query.filter_by(is_product_instrument=True).with_entities(Product.product_manufacturer).distinct().all()
    accessory_manufacturers = Product.query.filter_by(is_product_instrument=False).with_entities(Product.product_manufacturer).distinct().all()
    
    # Отримуємо всі продукти
    items = Product.query.all()
    
    return render_template(
        'home.html',
        items=items,
        tool_categories=tool_categories,
        accessory_categories=accessory_categories,
        tool_manufacturers=tool_manufacturers,
        accessory_manufacturers=accessory_manufacturers,
        cart=Cart.query.filter_by(customer_link=current_user.id).all()
                            if current_user.is_authenticated else []
    )








@views.route('/category/<string:category>')
def category_list(category):
    
    tool_categories = Product.query.filter_by(is_product_instrument=True).with_entities(Product.product_type).distinct().all()
    accessory_categories = Product.query.filter_by(is_product_instrument=False).with_entities(Product.product_type).distinct().all()
    tool_manufacturers = Product.query.filter_by(is_product_instrument=True).with_entities(Product.product_manufacturer).distinct().all()
    accessory_manufacturers = Product.query.filter_by(is_product_instrument=False).with_entities(Product.product_manufacturer).distinct().all()
    
    items = Product.query.filter_by(product_type=category).all()
    
    return render_template(
        'home.html',
        items=items,
        tool_categories=tool_categories,
        accessory_categories=accessory_categories,
        tool_manufacturers=tool_manufacturers,
        accessory_manufacturers=accessory_manufacturers,
        cart=Cart.query.filter_by(customer_link=current_user.id).all()
                            if current_user.is_authenticated else []
    )
    
    
@views.route('/manufacturer/<string:manufacturer>')
def manufacrurer_list(manufacturer):
    
    tool_categories = Product.query.filter_by(is_product_instrument=True).with_entities(Product.product_type).distinct().all()
    accessory_categories = Product.query.filter_by(is_product_instrument=False).with_entities(Product.product_type).distinct().all()
    tool_manufacturers = Product.query.filter_by(is_product_instrument=True).with_entities(Product.product_manufacturer).distinct().all()
    accessory_manufacturers = Product.query.filter_by(is_product_instrument=False).with_entities(Product.product_manufacturer).distinct().all()
    
    items = Product.query.filter_by(product_manufacturer=manufacturer).all()
    
    return render_template(
        'home.html',
        items=items,
        tool_categories=tool_categories,
        accessory_categories=accessory_categories,
        tool_manufacturers=tool_manufacturers,
        accessory_manufacturers=accessory_manufacturers,
        cart=Cart.query.filter_by(customer_link=current_user.id).all()
                            if current_user.is_authenticated else []
    )

@views.route('/add-to-cart/<int:item_id>')
@login_required
def add_to_cart(item_id):
    item_to_add = Product.query.get(item_id)
    item_exists = Cart.query.filter_by(product_link=item_id, customer_link=current_user.id).first()
    if item_exists:
        try:
            item_exists.quantity = item_exists.quantity + 1
            db.session.commit()
            flash(f' Quantity of { item_exists.product.product_name } has been updated')
            return redirect(request.referrer)
        except Exception as e:
            print('Quantity not Updated', e)
            flash(f'Quantity of { item_exists.product.product_name } not updated')
            return redirect(request.referrer)

    new_cart_item = Cart()
    new_cart_item.quantity = 1
    new_cart_item.product_link = item_to_add.id
    new_cart_item.customer_link = current_user.id

    try:
        db.session.add(new_cart_item)
        db.session.commit()
        flash(f'{new_cart_item.product.product_name} added to cart')
    except Exception as e:
        print('Item not added to cart', e)
        flash(f'{new_cart_item.product.product_name} has not been added to cart')

    return redirect(request.referrer)


@views.route('/wishlist/<int:item_id>')
@login_required
def add_to_wishlist(item_id):
    item_to_add = Product.query.get(item_id)
    item_exists = Wishlist.query.filter_by(customer_link=current_user.id, product_link=item_id).first()
    if item_exists:
        try:
            
            db.session.commit()
            flash(f' Quantity of { item_exists.product.product_name } has been updated')
            return redirect(request.referrer)
        except Exception as e:
            print('Quantity not Updated', e)
            flash(f'Quantity of { item_exists.product.product_name } not updated')
            return redirect(request.referrer)
        
    new_wishlist_item = Wishlist()
    new_wishlist_item.quantity = 1
    new_wishlist_item.customer_link = current_user.id
    new_wishlist_item.product_link = item_to_add.id
    
    try:
        db.session.add(new_wishlist_item)
        db.session.commit()
        flash(f'{new_wishlist_item.product.product_name} added to wishlist')
    except Exception as e:
        print('Item not added to wishlist', e)
        flash(f'{new_wishlist_item.product.product_name} has not been added to wishlist')
        
    return redirect(request.referrer)





@views.route('/cart')
@login_required
def show_cart():
    cart = Cart.query.filter_by(customer_link=current_user.id).all()
    amount = 0
    for item in cart:
        amount += item.product.current_price * item.quantity

    return render_template('cart.html', cart=cart, amount=amount, total=amount+200)



@views.route('/wishlist')
@login_required
def show_wishlist():
    wishlist = Wishlist.query.filter_by(customer_link=current_user.id).all()
    
    return render_template('wishlist.html', wishlist=wishlist)


@views.route('/pluscart')
@login_required
def plus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        cart_item.quantity = cart_item.quantity + 1
        db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()

        amount = 0

        for item in cart:
            amount += item.product.current_price * item.quantity

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 200
        }

        return jsonify(data)


@views.route('/minuscart')
@login_required
def minus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        cart_item.quantity = cart_item.quantity - 1
        db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()

        amount = 0

        for item in cart:
            amount += item.product.current_price * item.quantity

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 200
        }

        return jsonify(data)


@views.route('removecart')
@login_required
def remove_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        db.session.delete(cart_item)
        db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()

        amount = 0

        for item in cart:
            amount += item.product.current_price * item.quantity

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 200
        }

        return jsonify(data)
    
    
    
@views.route('/removewishlist')
@login_required
def remove_wishlist():
    try:
        wishlist_id = request.args.get('wishlist_id')
        if not wishlist_id:
            return jsonify({'success': False, 'error': 'Missing wishlist ID'}), 400

        wishlist_item = Wishlist.query.filter_by(id=wishlist_id, customer_link=current_user.id).first()

        if not wishlist_item:
            return jsonify({'success': False, 'error': 'Item not found or unauthorized'}), 404

        db.session.delete(wishlist_item)
        db.session.commit()

        return jsonify({'success': True}), 200

    except Exception as e:
        print(f"Error: {e}")  # Лог для діагностики
        return jsonify({'success': False, 'error': 'Internal server error'}), 500






@views.route('/place-order')
@login_required
def place_order():
    customer_cart = Cart.query.filter_by(customer_link=current_user.id).all()
    if customer_cart:
        try:
            total = 0
            for item in customer_cart:
                total += item.product.current_price * item.quantity

            service = NovaPoshtaAPI(api_key=API_KEY)
            create_order_response = service.create_order(
                recipient_name=f'{current_user.username}',
                recipient_phone='+380505555555',
                city='Київ',  # Замініть на місто користувача
                address='вул. Хрещатик, 22',  # Замініть на адресу користувача
                cost=total + 200
            )

            if create_order_response.get('success'):
                for item in customer_cart:
                    new_order = Order()
                    new_order.quantity = item.quantity
                    new_order.price = item.product.current_price
                    new_order.status = 'Processed'
                    new_order.payment_id = create_order_response['data'][0]['Ref']

                    new_order.product_link = item.product_link
                    new_order.customer_link = item.customer_link

                    db.session.add(new_order)

                    product = Product.query.get(item.product_link)
                    product.in_stock -= item.quantity

                    db.session.delete(item)

                    db.session.commit()

                flash('Order Placed Successfully')
                return redirect('/orders')
            else:
                flash('Order not placed: ' + create_order_response.get('errors')[0])
                return redirect('/')
        except Exception as e:
            print(e)
            flash('Order not placed')
            return redirect('/')
    else:
        flash('Your cart is Empty')
        return redirect('/')


@views.route('/orders')
@login_required
def order():
    orders = Order.query.filter_by(customer_link=current_user.id).all()
    return render_template('orders.html', orders=orders)


@views.route('/', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form.get('search')
        print(f"Search Query: {search_query}")  # Debug statement
        
        # Modify the query to search in name, description, or type
        items = Product.query.filter(
            or_(
                Product.product_name.ilike(f'%{search_query}%'),
                Product.product_description.ilike(f'%{search_query}%'),
                Product.product_type.ilike(f'%{search_query}%'),
                Product.product_manufacturer.ilike(f'%{search_query}%')
            )
        ).all()

        tool_categories = Product.query.filter_by(is_product_instrument=True).with_entities(Product.product_type).distinct().all()
        accessory_categories = Product.query.filter_by(is_product_instrument=False).with_entities(Product.product_type).distinct().all()
        tool_manufacturers = Product.query.filter_by(is_product_instrument=True).with_entities(Product.product_manufacturer).distinct().all()
        accessory_manufacturers = Product.query.filter_by(is_product_instrument=False).with_entities(Product.product_manufacturer).distinct().all()
        print(f"Items Found: {len(items)} items")  # Debug statement
        
        return render_template(
            'home.html',
            items=items,
            tool_categories=tool_categories,
            accessory_categories=accessory_categories,
            tool_manufacturers=tool_manufacturers,
            accessory_manufacturers=accessory_manufacturers,
            cart=Cart.query.filter_by(customer_link=current_user.id).all()
                            if current_user.is_authenticated else []
    )

    return render_template('search.html')


@views.route('/info/<int:item_id>')
def product_info(item_id):
    item = Product.query.get(item_id)
    return render_template('product_info.html', item=item)
