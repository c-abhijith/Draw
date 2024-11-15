from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
import cloudinary
import cloudinary.uploader
import cloudinary.api
from config import Config
from forms import SignupForm, LoginForm, PictureForm, ToggleLikeForm
from models import db, User, Product
from utils import login_required, logout_required
import os
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__, 
    static_url_path='/static',
    static_folder='static'
)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.config.from_object(Config)
db.init_app(app)
csrf = CSRFProtect(app)
migrate = Migrate(app, db)

# Define the verification function first
def verify_cloudinary_config():
    try:
        # Test Cloudinary configuration
        cloudinary.api.ping()
        print("Cloudinary configuration verified successfully")
    except Exception as e:
        print(f"Cloudinary configuration error: {str(e)}")

# Initialize Cloudinary and verify config
cloudinary.config(
    cloud_name=app.config['CLOUDINARY_CLOUD_NAME'],
    api_key=app.config['CLOUDINARY_API_KEY'],
    api_secret=app.config['CLOUDINARY_API_SECRET']
)

# Verify Cloudinary config during app initialization
with app.app_context():
    verify_cloudinary_config()

# Function to upload image to Cloudinary
def upload_photo(file):
    if not file:
        print("No file provided")
        return None
        
    try:
        # Print Cloudinary config for debugging
        print(f"Cloudinary Config - Cloud Name: {app.config['CLOUDINARY_CLOUD_NAME']}")
        print(f"Cloudinary Config - API Key: {app.config['CLOUDINARY_API_KEY']}")
        print(f"API Secret exists: {bool(app.config['CLOUDINARY_API_SECRET'])}")
        
        # Read file data
        file_data = file.read()
        if not file_data:
            print("Empty file data")
            return None
            
        # Upload to cloudinary
        upload_result = cloudinary.uploader.upload(
            file_data,
            folder="product_images",
            resource_type="auto",
            api_key=app.config['CLOUDINARY_API_KEY'],
            api_secret=app.config['CLOUDINARY_API_SECRET'],
            cloud_name=app.config['CLOUDINARY_CLOUD_NAME']
        )
        
        print(f"Upload result: {upload_result}")  # Debug print
        
        if 'public_id' in upload_result:
            return upload_result['public_id']
        else:
            print(f"Upload failed: {upload_result}")
            return None
            
    except Exception as e:
        print(f"Detailed Cloudinary upload error: {str(e)}")
        import traceback
        traceback.print_exc()  # Print full stack trace
        return None
    finally:
        # Reset file pointer
        file.seek(0)

# Function to delete image from Cloudinary
def delete_photo(public_id):
    try:
        cloudinary.uploader.destroy(public_id)
    except Exception as e:
        print(f"An error occurred while deleting the file: {e}")

# Update database initialization
if os.getenv('VERCEL_ENV') == 'production':
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"Database initialization error: {e}")

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
@logout_required
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

# Login route
@app.route('/', methods=['GET', 'POST'])
@logout_required
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        flash('Invalid username or password.', 'error')
    return render_template('login.html', form=form)

# Home route
@app.route('/home')
@login_required
def home():
    current_user_id = session.get('user_id')
    form = ToggleLikeForm()
    search_term = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 8
    query = Product.query

    if search_term:
        query = query.filter(Product.name.ilike(f'%{search_term}%'))
    query = query.order_by(
        db.case((Product.user_id == current_user_id, 1), else_=0).desc()
    )
    products = query.paginate(page=page, per_page=per_page)
    cards = [
        {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "count": len(product.like_count),
            "users_list": product.like_count,
            "image_url": cloudinary.CloudinaryImage(product.image_file).build_url(
                width=300,
                height=300,
                crop="fill"
            ),
            "user": product.user_id
        } for product in products.items
    ]
    for i in cards:
        print(i)
    return render_template('home.html', cards=cards, search_term=search_term, products=products, form=form)

# Logout route
@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# Add product route
@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    form = PictureForm()
    if form.validate_on_submit():
        if 'image' not in request.files:
            flash('No file part', 'error')
            return render_template('product_form.html', form=form)
            
        file = request.files['image']
        if file.filename == '':
            flash('No selected file', 'error')
            return render_template('product_form.html', form=form)
            
        if not allowed_file(file.filename):
            flash('Invalid file type. Allowed types are: png, jpg, jpeg, gif', 'error')
            return render_template('product_form.html', form=form)

        try:
            print(f"Processing file: {file.filename}")
            print(f"File content type: {file.content_type}")
            print(f"File size: {file.content_length if hasattr(file, 'content_length') else 'unknown'}")
            
            file_id = upload_photo(file)
            
            if not file_id:
                flash('Error uploading image to Cloudinary. Please try again.', 'error')
                return render_template('product_form.html', form=form)

            print(f"Successfully uploaded with ID: {file_id}")
            
            new_product = Product(
                name=form.name.data,
                price=form.price.data,
                user_id=session['user_id'],
                image_file=file_id
            )
            
            db.session.add(new_product)
            db.session.commit()
            flash('Product added successfully!', 'success')
            return redirect(url_for('home'))
            
        except Exception as e:
            print(f"Error in add_product: {str(e)}")
            import traceback
            traceback.print_exc()
            flash('An error occurred while processing your request.', 'error')
            return render_template('product_form.html', form=form)

    return render_template('product_form.html', form=form)

# Add this helper function at the top of your file with other utility functions
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Update product route
@app.route('/update_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = PictureForm()

    if form.validate_on_submit():
        if 'image' in request.files and request.files['image']:
            file = request.files['image']
            if allowed_file(file.filename):
                if product.image_file:
                    delete_photo(product.image_file)
                
                file_id = upload_photo(file)
                if file_id:
                    product.image_file = file_id
                else:
                    flash('Error uploading image to Cloudinary.', 'error')
                    return render_template('product_form.html', form=form, product=product)
            else:
                flash('Invalid file type. Allowed types are: png, jpg, jpeg, gif', 'error')
                return render_template('product_form.html', form=form, product=product)

        product.name = form.name.data
        product.price = form.price.data
        db.session.commit()

        flash('Product updated successfully!', 'success')
        return redirect(url_for('home'))

    form.name.data = product.name
    form.price.data = product.price
    return render_template('product_form.html', form=form, product=product)

# Delete product route
@app.route('/delete_product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)

    if product.image_file:
        delete_photo(product.image_file)

    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('home'))

# Toggle like route
@app.route('/toggle_like/<int:product_id>', methods=['POST'])
@login_required
def toggle_like(product_id):
    product = Product.query.get_or_404(product_id)
    user_id = session['user_id']
    if user_id in product.like_count:
        product.like_count.remove(user_id)
        flash('You unliked this product.', 'success')
    else:
        product.like_count.append(user_id)
        flash('You liked this product!', 'success')
    db.session.commit()
    return redirect(url_for('home'))

# Add this route for serving static files
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    if os.getenv('VERCEL_ENV') == 'production':
        app.run()
    else:
        app.run(debug=True)
