from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os

# Flask ilovasini yaratish
app = Flask(__name__)
CORS(app)

# Ma'lumotlar bazasi konfiguratsiyasi
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False

db = SQLAlchemy(app)

# Modellar (Ma'lumotlar bazasi jadvallari)
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    category = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'stock': self.stock,
            'category': self.category,
            'created_at': self.created_at.isoformat()
        }

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'total_price': self.total_price,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

# API Endpointlar

@app.route('/')
def index():
    return jsonify({
        'message': 'Flask Table Fetching API',
        'version': '1.0',
        'endpoints': {
            'users': '/api/users',
            'products': '/api/products',
            'orders': '/api/orders',
            'tables': '/api/tables'
        }
    })

# Barcha mavjud jadvallar ro'yxatini olish
@app.route('/api/tables', methods=['GET'])
def get_tables():
    try:
        tables = db.metadata.tables.keys()
        return jsonify({
            'success': True,
            'tables': list(tables),
            'count': len(tables)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# USERS CRUD operatsiyalari
@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        users = User.query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'data': [user.to_dict() for user in users.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': users.total,
                'pages': users.pages
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        return jsonify({'success': True, 'data': user.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404

@app.route('/api/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        
        if not data.get('username') or not data.get('email'):
            return jsonify({'success': False, 'error': 'Username va email majburiy'}), 400
        
        user = User(
            username=data['username'],
            email=data['email']
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'success': True, 'data': user.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# PRODUCTS CRUD operatsiyalari
@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        category = request.args.get('category')
        
        query = Product.query
        
        if category:
            query = query.filter_by(category=category)
        
        products = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'data': [product.to_dict() for product in products.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': products.total,
                'pages': products.pages
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        return jsonify({'success': True, 'data': product.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404

@app.route('/api/products', methods=['POST'])
def create_product():
    try:
        data = request.get_json()
        
        if not data.get('name') or not data.get('price'):
            return jsonify({'success': False, 'error': 'Name va price majburiy'}), 400
        
        product = Product(
            name=data['name'],
            price=data['price'],
            stock=data.get('stock', 0),
            category=data.get('category')
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({'success': True, 'data': product.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ORDERS CRUD operatsiyalari
@app.route('/api/orders', methods=['GET'])
def get_orders():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        
        query = Order.query
        
        if status:
            query = query.filter_by(status=status)
        
        orders = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'data': [order.to_dict() for order in orders.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': orders.total,
                'pages': orders.pages
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    try:
        order = Order.query.get_or_404(order_id)
        return jsonify({'success': True, 'data': order.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404

@app.route('/api/orders', methods=['POST'])
def create_order():
    try:
        data = request.get_json()
        
        required_fields = ['user_id', 'product_id', 'quantity', 'total_price']
        if not all(field in data for field in required_fields):
            return jsonify({'success': False, 'error': 'Barcha majburiy maydonlarni to\'ldiring'}), 400
        
        order = Order(
            user_id=data['user_id'],
            product_id=data['product_id'],
            quantity=data['quantity'],
            total_price=data['total_price'],
            status=data.get('status', 'pending')
        )
        
        db.session.add(order)
        db.session.commit()
        
        return jsonify({'success': True, 'data': order.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Xato xabarlarini boshqarish
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Resurs topilmadi'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Server xatosi'}), 500

# Ma'lumotlar bazasini yaratish
def init_db():
    with app.app_context():
        db.create_all()
        print("Ma'lumotlar bazasi yaratildi!")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)