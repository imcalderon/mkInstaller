import os
import sys
# Add the parent directory to the path so we can import our existing modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from db.session import Session, init_db
from db.models import Product, Feature, File, Shortcut, Directory
import uuid

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# Initialize the database if it doesn't exist
try:
    init_db()
    print("Database initialized")
except Exception as e:
    print(f"Database already exists: {e}")

@app.route('/')
def index():
    return render_template('index.html')

# API Routes
@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products"""
    session = Session()
    products = session.query(Product).all()
    result = []
    for product in products:
        result.append({
            'id': product.id,
            'name': product.name,
            'version': product.version,
            'description': product.description
        })
    return jsonify(result)

@app.route('/api/products', methods=['POST'])
def add_product():
    """Add a new product"""
    data = request.json
    
    if not data.get('name'):
        return jsonify({'error': 'Product name is required'}), 400
        
    session = Session()
    product = Product(
        name=data['name'],
        version=data.get('version', '1.0.0'),
        description=data.get('description', '')
    )
    session.add(product)
    session.commit()
    
    return jsonify({
        'id': product.id,
        'name': product.name,
        'version': product.version,
        'description': product.description
    }), 201

@app.route('/api/products/<int:id>', methods=['GET'])
def get_product(id):
    """Get a product by ID"""
    session = Session()
    product = session.query(Product).filter_by(id=id).first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404
        
    return jsonify({
        'id': product.id,
        'name': product.name,
        'version': product.version,
        'description': product.description
    })

@app.route('/api/products/<int:id>', methods=['PUT'])
def update_product(id):
    """Update a product"""
    data = request.json
    session = Session()
    product = session.query(Product).filter_by(id=id).first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404
        
    if 'name' in data:
        product.name = data['name']
    if 'version' in data:
        product.version = data['version']
    if 'description' in data:
        product.description = data['description']
        
    session.commit()
    
    return jsonify({
        'id': product.id,
        'name': product.name,
        'version': product.version,
        'description': product.description
    })

@app.route('/api/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    """Delete a product"""
    session = Session()
    product = session.query(Product).filter_by(id=id).first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404
        
    session.delete(product)
    session.commit()
    
    return jsonify({'message': f'Product {id} deleted successfully'})

# Feature routes
@app.route('/api/products/<int:product_id>/features', methods=['GET'])
def get_features(product_id):
    """Get all features for a product"""
    session = Session()
    features = session.query(Feature).filter_by(product_id=product_id).all()
    result = []
    for feature in features:
        result.append({
            'id': feature.id,
            'name': feature.name,
            'description': feature.description
        })
    return jsonify(result)

@app.route('/api/products/<int:product_id>/features', methods=['POST'])
def add_feature(product_id):
    """Add a new feature to a product"""
    data = request.json
    
    if not data.get('name'):
        return jsonify({'error': 'Feature name is required'}), 400
        
    session = Session()
    product = session.query(Product).filter_by(id=product_id).first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404
        
    feature = Feature(
        name=data['name'],
        description=data.get('description', ''),
        product=product
    )
    session.add(feature)
    session.commit()
    
    return jsonify({
        'id': feature.id,
        'name': feature.name,
        'description': feature.description,
        'product_id': product_id
    }), 201

# File routes
@app.route('/api/features/<int:feature_id>/files', methods=['GET'])
def get_files(feature_id):
    """Get all files for a feature"""
    session = Session()
    files = session.query(File).filter_by(feature_id=feature_id).all()
    result = []
    for file in files:
        result.append({
            'id': file.id,
            'path': file.path,
            'install_path': file.install_path
        })
    return jsonify(result)

@app.route('/api/features/<int:feature_id>/files', methods=['POST'])
def add_file(feature_id):
    """Add a new file to a feature"""
    data = request.json
    
    if not data.get('path'):
        return jsonify({'error': 'File path is required'}), 400
        
    session = Session()
    feature = session.query(Feature).filter_by(id=feature_id).first()
    if not feature:
        return jsonify({'error': 'Feature not found'}), 404
        
    file = File(
        path=data['path'],
        install_path=data.get('install_path', ''),
        feature=feature
    )
    session.add(file)
    session.commit()
    
    return jsonify({
        'id': file.id,
        'path': file.path,
        'install_path': file.install_path,
        'feature_id': feature_id
    }), 201

# Shortcut routes
@app.route('/api/features/<int:feature_id>/shortcuts', methods=['GET'])
def get_shortcuts(feature_id):
    """Get all shortcuts for a feature"""
    session = Session()
    shortcuts = session.query(Shortcut).filter_by(feature_id=feature_id).all()
    result = []
    for shortcut in shortcuts:
        result.append({
            'id': shortcut.id,
            'name': shortcut.name,
            'target': shortcut.target
        })
    return jsonify(result)

@app.route('/api/features/<int:feature_id>/shortcuts', methods=['POST'])
def add_shortcut(feature_id):
    """Add a new shortcut to a feature"""
    data = request.json
    
    if not data.get('name') or not data.get('target'):
        return jsonify({'error': 'Shortcut name and target are required'}), 400
        
    session = Session()
    feature = session.query(Feature).filter_by(id=feature_id).first()
    if not feature:
        return jsonify({'error': 'Feature not found'}), 404
        
    shortcut = Shortcut(
        name=data['name'],
        target=data['target'],
        feature=feature
    )
    session.add(shortcut)
    session.commit()
    
    return jsonify({
        'id': shortcut.id,
        'name': shortcut.name,
        'target': shortcut.target,
        'feature_id': feature_id
    }), 201

# Directory routes
@app.route('/api/directories', methods=['GET'])
def get_directories():
    """Get all installation directories"""
    session = Session()
    directories = session.query(Directory).all()
    result = []
    for directory in directories:
        result.append({
            'id': directory.id,
            'name': directory.name
        })
    return jsonify(result)

@app.route('/api/directories', methods=['POST'])
def add_directory():
    """Add a new installation directory"""
    data = request.json
    
    if not data.get('name'):
        return jsonify({'error': 'Directory name is required'}), 400
        
    session = Session()
    directory = Directory(
        name=data['name']
    )
    session.add(directory)
    session.commit()
    
    return jsonify({
        'id': directory.id,
        'name': directory.name
    }), 201

@app.route('/api/directories/<int:id>', methods=['DELETE'])
def delete_directory(id):
    """Delete a directory"""
    session = Session()
    directory = session.query(Directory).filter_by(id=id).first()
    if not directory:
        return jsonify({'error': 'Directory not found'}), 404
        
    session.delete(directory)
    session.commit()
    
    return jsonify({'message': f'Directory {id} deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
