from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields
import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/ecom_app'

db - SQLAlchemy(app)
ma = Marshmallow(app)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)

class CustomerAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    customer = db.relationship('Customer', backref=db.backref('accounts', lazy=True))


class Product(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        price = db.Column(db.Float, nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    customer = db.relationship('Customer', backref=db.backref('orders', lazy=True))
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = db.relationship('Product')
    quantity = db.Column(db.Integer, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Str(required=True)
    phone_number = fields.Str()

class CustomerAccountSchema(ma.SQLAlchemyAutoSchema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    customer_id = fields.Int(required=True)

class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)

class OrderItemSchema(Schema):
    id = fields.Int(dump_only=True)
    product_id = fields.Int(required=True)
    quantity = fields.Int(required=True)

class OrderSchema(Schema):
    id = fields.Int(dump_only=True)
    order_date = fields.DateTime(format='%Y-%m-%dT%H:%M:%S', required=True)
    customer_id = fields.Int(required=True)
    items = fields.List(fields.Nested(OrderItemSchema), dump_only=True)

with app.app_context():
    db.create_all()


#mini project task 1

@app.route('/customers', methods=['POST'])
def create_customer():
    try:
        data = request.json
        new_customer = Customer(
            name=data['name'],
            email=data['email'],
            phone_number=data.get('phone_number')
        )
        db.session.add(new_customer)
        db.session.commit()
        result = CustomerSchema().dump(new_customer)
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    

@app.route('/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        result = CustomerSchema().dump(customer)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@app.route('/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    try:
        data = request.json
        customer = Customer.query.get_or_404(customer_id)
        customer.name = data.get('name', customer.name)
        customer.email = data.get('email', customer.email)
        customer.phone_number = data.get('phone_number', customer.phone_number)
        db.session.commit()
        result = CustomerSchema().dump(customer)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400    


@app.route('/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        db.session.delete(customer)
        db.session.commit()
        return jsonify({'message': 'Customer deleted successfully'}), 204
    except Exception as e:
        return jsonify({'error': str(e)}), 404
    

@app.route('/customer-accounts', methods=['POST'])
def create_customer_account():
    try:
        data = request.json
        new_account = CustomerAccount(
            username=data['username'],
            password=data['password'],
            customer_id=data['customer_id']
        )
        db.session.add(new_account)
        db.session.commit()
        result = CustomerAccountSchema().dump(new_account)
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    

@app.route('/customer-accounts/<int:account_id>', methods=['GET'])
def get_customer_account(account_id):
    try:
        account = CustomerAccount.query.get_or_404(account_id)
        result = CustomerAccountSchema().dump(account)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404
    

@app.route('/customer-accounts/<int:account_id>', methods=['PUT'])
def update_customer_account(account_id):
    try:
        data = request.json
        account = CustomerAccount.query.get_or_404(account_id)
        if 'username' in data:
            account.username = data['username']
        if 'password' in data:
            account.password = data['password']
        db.session.commit()
        result = CustomerAccountSchema().dump(account)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    

@app.route('/customer-accounts/<int:account_id>', methods=['DELETE'])
def delete_customer_account(account_id):
    try:
        account = CustomerAccount.query.get_or_404(account_id)
        db.session.delete(account)
        db.session.commit()
        return jsonify({'message': 'Account deleted successfully'}), 204
    except Exception as e:
        return jsonify({'error': str(e)}), 404
    

# mini project task 2

@app.route('/products', methods=['POST'])
def create_product():
    data = request.json
    try:
        name = data['name']
        price = data['price']
        if not name or price <= 0:
            return jsonify({'error': 'Invalid product data'}), 400
        
        new_product = Product(name=name, price=price)
        db.session.add(new_product)
        db.session.commit()
        return jsonify({'id': new_product.id, 'name': new_product.name, 'price': new_product.price}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        product_schema = ProductSchema()
        result = product_schema.dump(product)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404
    

@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.json
    try:
        product = Product.query.get_or_404(product_id)
        product_schema = ProductSchema()
        updated_product = product_schema.load(data, partial=True)
        for key, value in updated_product.items():
            setattr(product, key, value)
        db.session.commit()
        result = product_schema.dump(product)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    

@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted successfully'}), 204
    except Exception as e:
        return jsonify({'error': str(e)}), 404
    

@app.route('/products', methods=['GET'])
def list_products():
    try:
        products = Product.query.all()
        product_schema = ProductSchema(many=True)
        result = product_schema.dump(products)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

# mini project task 3

@app.route('/orders', methods=['POST'])
def place_order():
    data = request.json
    try:
        customer_id = data['customer_id']
        items = data['items']
        order_date = datetime.datetime.utcnow()

        new_order = Order(order_date=order_date, customer_id=customer_id)
        db.session.add(new_order)
        db.session.commit()

        for item in items:
            order_item = OrderItem(
                product_id=item['product_id'],
                quantity=item['quantity'],
                order_id=new_order.id
            )
            db.session.add(order_item)
        
        db.session.commit()
        order_schema = OrderSchema()
        result = order_schema.dump(new_order)
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    data = request.json
    try:
        order = Order.query.get_or_404(order_id)
        if 'order_date' in data:
            order.order_date = datetime.datetime.fromisoformat(data['order_date'])
        if 'customer_id' in data:
            order.customer_id = data['customer_id']
        db.session.commit()
        order_schema = OrderSchema()
        result = order_schema.dump(order)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    try:
        order = Order.query.get_or_404(order_id)
        db.session.delete(order)
        db.session.commit()
        return jsonify({'message': 'Order deleted successfully'}), 204
    except Exception as e:
        return jsonify({'error': str(e)}), 404
    
@app.route('/orders/track/<int:order_id>', methods=['GET']) 
def track_order(order_id):
    try:
        order = Order.query.get_or_404(order_id)
        order_schema = OrderSchema()
        result = order_schema.dump(order)
        return jsonify({
            'order': result,
            'expected_delivery': (order.order_date + datetime.timedelta(days=7)).isoformat()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404
    

@app.route('/orders', methods=['GET'])
def list_orders():
    try:
        orders = Order.query.all()
        order_schema = OrderSchema(many=True)
        result = order_schema.dump(orders)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

if __name__ == '__main__':
    app.run(debug=True)
