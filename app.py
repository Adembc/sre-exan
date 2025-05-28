from flask import Flask, render_template, request, redirect, url_for, session
from prometheus_client import Counter, generate_latest, Histogram
import time
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Product catalog with numeric codes
products = {
    1: {'description': 'Apple', 'price': 0.5, 'image': 'apple.png'},
    2: {'description': 'Banana', 'price': 0.3, 'image': 'banana.png'},
    3: {'description': 'Orange', 'price': 0.4, 'image': 'orange.png'},
    4: {'description': 'Mango', 'price': 1.0, 'image': 'mango.png'}
}

product_sales = Counter('Buy_By_Product', 'Number of sales per product', ['product'])
card_duration = Histogram('Cart_Duration', 'Time spent processing /card requests')

@app.route('/')
def index():
    return render_template('index.html', products=products)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_code = int(request.form['product'])
    product_info = products.get(product_code)
    quantity = int(request.form['quantity'])
    if 'cart' not in session:
        session['cart'] = []
    product_sales.labels(product=product_info['description']).inc()
    session['cart'].append({'code': product_info['description'], 'quantity': quantity})
    session.modified = True
    return redirect(url_for('index'))

@app.route('/cart')
@card_duration.time()
def cart():
    cart_items = session.get('cart', [])
    total = sum(products[item['code']]['price'] * item['quantity'] for item in cart_items)
    return render_template('cart.html', cart=cart_items, products=products, total=total)

@app.route('/clear_cart')
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('index'))
@app.route('/metrics')
def metrics():
    return generate_latest()


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
