from flask import Flask, render_template, request, redirect, url_for, flash, session,jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
import os
from werkzeug.utils import secure_filename
from config import Config
from forms import SignupForm, LoginForm, PictureForm, ToggleLikeForm
from models import db, User, Product
from utils import login_required, logout_required
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload

# Initialize Flask app and load configurations

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
csrf = CSRFProtect(app)
migrate = Migrate(app, db)

# Create upload directory if it doesn't exist
UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']
# <<<<<<< HEAD
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# =======
# # if not os.path.exists(UPLOAD_FOLDER):
# #     os.makedirs(UPLOAD_FOLDER)
# # dropbox_client = dropbox.Dropbox(Config.DROPBOX_ACCESS_TOKEN)
# >>>>>>> cf581f5815b0b7ccf5ed63cab182948f02d0a864

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# <<<<<<< HEAD
# Google Drive API functions
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'service_account.json'
PARENT_FOLDER_ID = "1K81Cm3JEKDjArJq2MGNWLbvz26S7-KCT"  # Replace with your folder ID from Google Drive

def authenticate():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return creds

def upload_photo(file_path, filename):
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {
        'name': filename,  # Set file name dynamically
        'parents': [PARENT_FOLDER_ID]  # Specifies the folder in which the file will be uploaded
    }

    media = MediaFileUpload(file_path, mimetype='image/jpeg')  # Set the MIME type for the image

    try:
        # Upload the file
        file = service.files().create(
            body=file_metadata,
            media_body=media
        ).execute()

        # Update sharing permissions to make the file public
        service.permissions().create(
            fileId=file['id'],
            body={'role': 'reader', 'type': 'anyone'}
        ).execute()

        return file.get('id')  # Return the file ID from Google Drive
    except Exception as e:
        print(f"An error occurred: {e}")
        return None  # Handle error gracefully

def delete_google_drive_file(file_id):
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)
    try:
        service.files().delete(fileId=file_id).execute()
    except Exception as e:
        print(f"An error occurred while deleting the file: {e}")

# =======
# def get_dropbox_shared_link(file_path):
#     try:
#         if not file_path.startswith('/'):
#             file_path = '/' + file_path  # Prefix with '/' if missing
#         shared_link_metadata = dbx.sharing_create_shared_link_with_settings(file_path)
#         return shared_link_metadata.url.replace("?dl=0", "?raw=1")  # Modify to make it a direct link
#     except dropbox.exceptions.ApiError as e:
#         print(f"Error getting shared link: {e}")
#         return None
    
# # Create tables
# >>>>>>> cf581f5815b0b7ccf5ed63cab182948f02d0a864
with app.app_context():
    db.create_all()

# User Signup Route
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

# User Login Route
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
            "image_url": f"https://drive.google.com/thumbnail?id={product.image_file}",  # Google Drive Image URL
            "user": product.user_id
        } for product in products.items
    ]

    return render_template('home.html', cards=cards, search_term=search_term, products=products, form=form)

@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    form = PictureForm()
    if form.validate_on_submit():
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
# <<<<<<< HEAD
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
# =======
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

#             new_product = Product(
#                 name=form.name.data,
#                 price=form.price.data,
#                 user_id=session['user_id'],
#                 image_file=filename
#             )
#             db.session.add(new_product)
#             db.session.commit()
#             flash('Product added successfully!', 'success')
#             return redirect(url_for('home'))
#         else:
#             flash('Invalid file type. Allowed types are: png, jpg, jpeg, gif', 'error')
    

#     return render_template('product_form.html', form=form)@app.route('/add_product', methods=['GET', 'POST'])
# @login_required
# def add_product():
#     form = PictureForm()

#     if form.validate_on_submit():
#         if 'image' not in request.files or request.files['image'].filename == '':
#             flash('No file part', 'error')
#             return redirect(request.url)

#         file = request.files['image']
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file_path = f"/products/{filename}"
#             # Upload to Dropbox
#             try:
#                 dbx.files_upload(file.read(), file_path)
#                 new_product = Product(
#                     name=form.name.data,
#                     price=form.price.data,
#                     user_id=session['user_id'],
#                     image_file=file_path
#                 )
#                 db.session.add(new_product)
#                 db.session.commit()
#                 flash('Product added successfully!', 'success')
#                 return redirect(url_for('home'))
#             except dropbox.exceptions.ApiError as e:
#                 flash(f"Error uploading file to Dropbox: {e}", 'error')
#         else:
#             flash('Invalid file type. Allowed types are: png, jpg, jpeg, gif', 'error')
# >>>>>>> cf581f5815b0b7ccf5ed63cab182948f02d0a864

            # Upload the image to Google Drive and get the file ID
            file_id = upload_photo(file_path, filename)
            if file_id:
                new_product = Product(
                    name=form.name.data,
                    price=form.price.data,
                    user_id=session['user_id'],
                    image_file=file_id  # Store the Google Drive file ID in the database
                )
                db.session.add(new_product)
                db.session.commit()
                flash('Product added successfully!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Error uploading image to Google Drive.', 'error')
        flash('Invalid file type. Allowed types are: png, jpg, jpeg, gif', 'error')
    return render_template('product_form.html', form=form)

@app.route('/update_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = PictureForm()

    # Store the current image file ID (Google Drive ID)
    old_image_file_id = product.image_file

    if form.validate_on_submit():
        if 'image' in request.files and request.files['image']:
            file = request.files['image']
            if file and allowed_file(file.filename):
                # Delete the old image from Google Drive before replacing it
                if old_image_file_id:
                    delete_google_drive_file(old_image_file_id)

                # Save the new image locally
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                # Upload the new image to Google Drive and update the file ID
                file_id = upload_photo(os.path.join(app.config['UPLOAD_FOLDER'], filename), filename)
                if file_id:
                    product.image_file = file_id  # Update the Google Drive file ID

        # Update product details (name, price, etc.)
        product.name = form.name.data
        product.price = form.price.data
        db.session.commit()
        
        flash('Product updated successfully!', 'success')
        return redirect(url_for('home'))

    form.name.data = product.name
    form.price.data = product.price
    return render_template('product_form.html', form=form, product=product)

@app.route('/delete_product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Delete the image from Google Drive before deleting the product
    if product.image_file:
        delete_google_drive_file(product.image_file)

    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('home'))

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

# <<<<<<< HEAD
# =======


# @app.route('/delete_all_users_and_products', methods=['GET'])
# def delete_all_users_and_products():
#     products = Product.query.all()
#     for product in products:
#         db.session.delete(product)  
#     users = User.query.all()
#     for user in users:
#         db.session.delete(user)  
#     db.session.commit()

    
#     return jsonify({"message": "All users and products deleted successfully"}), 200


# # Run the application
# >>>>>>> cf581f5815b0b7ccf5ed63cab182948f02d0a864
if __name__ == '__main__':
    app.run(debug=True)
