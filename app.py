from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime  # Add this import at the top of your file
from flask import abort

#from time import sleep
#from functools import lru_cache
import logging

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

logging.basicConfig(filename='app.log', 
                    level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///foodshelter.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(100), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    website = db.Column(db.String(200), nullable=True)
    contact = db.Column(db.String(100), nullable=True)
    notes = db.relationship('Note', backref='user', lazy=True)
    volunteers = db.relationship('Volunteer', backref='user', lazy=True)
    budget_entries = db.relationship('Budget', backref='user', lazy=True)
    donations = db.relationship('Donation', backref='user', lazy=True)
    role = db.Column(db.String(20), nullable=False, default='user')
    donation_link = db.Column(db.String(200), nullable=True)


class FoodStock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class ShelterLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Volunteer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    availability = db.Column(db.String(200), nullable=True)
    skills = db.Column(db.String(200), nullable=True)
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    donor_name = db.Column(db.String(100), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    users = User.query.all()
    shelter_info = []
    for user in users:
        locations = ShelterLocation.query.filter_by(user_id=user.id).all()
        shelter_info.append({
            'name': user.name,
            'bio': user.bio,
            'website': user.website,
            'contact': user.contact,
            'donation_link': user.donation_link,
            'locations': [{'address': loc.address, 'latitude': loc.latitude, 'longitude': loc.longitude} for loc in locations]
        })
    return render_template('home.html', shelter_info=shelter_info)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    if request.method == 'POST':
        current_user.name = request.form.get('name') or None
        current_user.bio = request.form.get('bio') or None
        current_user.website = request.form.get('website') or None
        current_user.contact = request.form.get('contact') or None
        current_user.donation_link = request.form.get('donation_link') or None
        db.session.commit()
        flash('Profile updated successfully!')
        return redirect(url_for('dashboard'))
    return render_template('update_profile.html')


@app.route('/dashboard')
@login_required
def dashboard():
    food_stock = FoodStock.query.filter_by(user_id=current_user.id).all()
    shelter_locations = ShelterLocation.query.filter_by(user_id=current_user.id).all()
    notes = Note.query.filter_by(user_id=current_user.id).all()
    budget_entries = Budget.query.filter_by(user_id=current_user.id).all()
    volunteers = Volunteer.query.filter_by(user_id=current_user.id).all()
    donations = Donation.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', food_stock=food_stock, shelter_locations=shelter_locations, 
                           notes=notes, budget_entries=budget_entries, volunteers=volunteers, donations=donations)





@app.route('/add_food_stock', methods=['POST'])
@login_required
def add_food_stock():
    item_name = request.form.get('item_name')
    quantity = request.form.get('quantity')
    new_item = FoodStock(item_name=item_name, quantity=quantity, user_id=current_user.id)
    db.session.add(new_item)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/add_shelter_location', methods=['POST'])
@login_required
def add_shelter_location():
    address = request.form.get('address')
    date_str = request.form.get('date')
    
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Initialize geolocator
        geolocator = Nominatim(user_agent="FoodShelterApp/1.0 (bencamrush@gmail.com)")
        
        # Attempt to geocode the address
        location = geolocator.geocode(address)
        
        if location:
            new_location = ShelterLocation(
                address=address,
                date=date_obj,
                user_id=current_user.id,
                latitude=location.latitude,
                longitude=location.longitude
            )
            db.session.add(new_location)
            db.session.commit()
            logging.info(f"Added new shelter location: {new_location.id}")
            flash('New shelter location added successfully!')
        else:
            logging.warning(f"Could not geocode address: {address}")
            flash('Could not geocode the address. Please try a more specific address.', 'error')
    
    except ValueError:
        flash('Invalid date format. Please use YYYY-MM-DD.')
    except (GeocoderTimedOut, GeocoderUnavailable):
        logging.error(f"Error adding shelter location: {str(e)}")
        flash('Geocoding service is currently unavailable. Please try again later.', 'error')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}')
    
    return redirect(url_for('dashboard'))


@app.route('/add_note', methods=['POST'])
@login_required
def add_note():
    content = request.form.get('content')
    new_note = Note(content=content, user_id=current_user.id)
    db.session.add(new_note)
    db.session.commit()
    flash('New note added successfully!')
    return redirect(url_for('dashboard'))

@app.route('/add_budget', methods=['POST'])
@login_required
def add_budget():
    amount = request.form.get('amount')
    description = request.form.get('description')
    date_str = request.form.get('date')
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        new_budget = Budget(amount=float(amount), description=description, date=date_obj, user_id=current_user.id)
        db.session.add(new_budget)
        db.session.commit()
        flash('New budget entry added successfully!')
    except ValueError:
        flash('Invalid input. Please check your entries.')
    return redirect(url_for('dashboard'))

@app.route('/add_volunteer', methods=['POST'])
@login_required
def add_volunteer():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    availability = request.form.get('availability')
    skills = request.form.get('skills')
    notes = request.form.get('notes')
    new_volunteer = Volunteer(name=name, email=email, phone=phone, availability=availability, skills=skills, notes=notes, user_id=current_user.id)
    db.session.add(new_volunteer)
    db.session.commit()
    flash('New volunteer added successfully!')
    return redirect(url_for('dashboard'))

@app.route('/delete_food_stock/<int:item_id>', methods=['POST'])
@login_required
def delete_food_stock(item_id):
    item = FoodStock.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        abort(403)
    db.session.delete(item)
    db.session.commit()
    flash('Food stock item deleted successfully.')
    return redirect(url_for('dashboard'))

@app.route('/delete_shelter_location/<int:location_id>', methods=['POST'])
@login_required
def delete_shelter_location(location_id):
    location = ShelterLocation.query.get_or_404(location_id)
    if location.user_id != current_user.id:
        abort(403)
    db.session.delete(location)
    db.session.commit()
    flash('Shelter location deleted successfully.')
    return redirect(url_for('dashboard'))

@app.route('/delete_note/<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        abort(403)
    db.session.delete(note)
    db.session.commit()
    flash('Note deleted successfully.')
    return redirect(url_for('dashboard'))

@app.route('/delete_volunteer/<int:volunteer_id>', methods=['POST'])
@login_required
def delete_volunteer(volunteer_id):
    volunteer = Volunteer.query.get_or_404(volunteer_id)
    if volunteer.user_id != current_user.id:
        abort(403)
    db.session.delete(volunteer)
    db.session.commit()
    flash('Volunteer deleted successfully.')
    return redirect(url_for('dashboard'))

@app.route('/delete_budget/<int:budget_id>', methods=['POST'])
@login_required
def delete_budget(budget_id):
    budget = Budget.query.get_or_404(budget_id)
    if budget.user_id != current_user.id:
        abort(403)
    db.session.delete(budget)
    db.session.commit()
    flash('Budget entry deleted successfully.')
    return redirect(url_for('dashboard'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists')
            return redirect(url_for('register'))
        
        new_user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registered successfully! Please log in.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/add_donation', methods=['POST'])
@login_required
def add_donation():
    amount = request.form.get('amount')
    donor_name = request.form.get('donor_name')
    new_donation = Donation(amount=float(amount), donor_name=donor_name, user_id=current_user.id)
    db.session.add(new_donation)
    db.session.commit()
    flash('New donation added successfully!')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

