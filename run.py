from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
import os
from werkzeug.utils import secure_filename
from config import Config
from forms import SignupForm, LoginForm, PictureForm, ToggleLikeForm
from models import db, User, Product  # Import models here
from utils import login_required, logout_required  # Import utility functions here

# Initialize Flask app and database
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)  # Initialize SQLAlchemy with the app
csrf = CSRFProtect(app)
migrate = Migrate(app, db)

# Ensure the upload directory exists
UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Create tables
with app.app_context():
    db.create_all()

# Route for user signup
@app.route('/signup', methods=['GET', 'POST'])
@logout_required
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)  # Hash password
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()  # Commit to the database
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

# Route for user login
@app.route('/', methods=['GET', 'POST'])
@logout_required
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()  # Get user by username
        if user and check_password_hash(user.password, form.password.data):  # Verify password
            session['user_id'] = user.id  # Store user_id in session
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        flash('Invalid username or password.', 'error')  # Show error for invalid credentials
    return render_template('login.html', form=form)

@app.route('/home')
@login_required
def home():
    current_user_id = session.get('user_id')
    form = ToggleLikeForm()
    # Get the search term from query parameters
    search_term = request.args.get('search', '').strip()

    # Set pagination variables
    page = request.args.get('page', 1, type=int)
    per_page = 8  # Number of products per page

    # Create a base query for products
    query = Product.query

    # Apply search filter if there is a search term
    if search_term:
        query = query.filter(Product.name.ilike(f'%{search_term}%'))

    # Order by user products first
    query = query.order_by(
        db.case((Product.user_id == current_user_id, 1), else_=0).desc()
    )

    # Paginate results
    products = query.paginate(page=page, per_page=per_page)
    cards = [
        {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "count": len(product.like_count),
            "users_list": product.like_count,
            "image": product.image_file,
            "user": product.user_id
        } for product in products
    ]
    # Render home template with product cards data
    return render_template('home.html', cards=cards, search_term=search_term, products=products, form=form)

# Route for logging out
@app.route('/logout')
@login_required  # Ensure the user is logged in before logging out
def logout():
    session.pop('user_id', None)  # Remove user_id from session
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# Route for adding a product
@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    form = PictureForm()

    if form.validate_on_submit():
        # Check if a file is part of the request
        if 'image' not in request.files or request.files['image'].filename == '':
            flash('No file part', 'error')
            return redirect(request.url)

        file = request.files['image']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            new_product = Product(
                name=form.name.data,
                price=form.price.data,
                user_id=session['user_id'],
                image_file=filename
            )
            db.session.add(new_product)
            db.session.commit()
            flash('Product added successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid file type. Allowed types are: png, jpg, jpeg, gif', 'error')

    return render_template('product_form.html', form=form)

@app.route('/update_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def update_product(product_id):
    product = Product.query.get_or_404(product_id)  # Get the product by ID
    form = PictureForm()

    if request.method == 'POST':
        # Handle file upload (optional, if user doesn't want to change the image)
        if 'image' in request.files and request.files['image']:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                product.image_file = filename  # Update the image file if a new one is uploaded

        # Update product fields
        product.name = form.name.data
        product.price = form.price.data
        
        db.session.commit()  # Commit changes to the database
        flash('Product updated successfully!', 'success')
        return redirect(url_for('home'))

    form.name.data = product.name  # Pre-fill the form with existing data
    form.price.data = product.price
    return render_template('product_form.html', form=form, product=product)

@app.route('/delete_product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)  # Delete product from the database
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/toggle_like/<int:product_id>', methods=['POST'])
@login_required
def toggle_like(product_id):
    product = Product.query.get_or_404(product_id)  # Fetch the product by ID
    user_id = session['user_id']  # Get the current user's ID

    if user_id in product.like_count:
        product.like_count.remove(user_id)  # Unlike the product
        flash('You unliked this product.', 'success')
    else:
        product.like_count.append(user_id)  # Like the product
        flash('You liked this product!', 'success')

    db.session.commit()  # Commit changes to the database
    return redirect(url_for('home'))

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
