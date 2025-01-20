from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os

app = Flask(__name__)

# Set up the database URI (using SQLite in this case)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///users.db')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking to avoid warnings
app.secret_key = 'supersecretkey'

# Initialize database, bcrypt, and login manager
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


class Investment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    time_period = db.Column(db.Float, nullable=False)
    interest_type = db.Column(db.String(10), nullable=False)
    interest = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)

# Database table creation
with app.app_context():
    db.create_all()  # This ensures that tables are created when the app starts


# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Interest Calculation Functions
def calculate_simple_interest(principal, rate, time):
    return (principal * rate * time) / 100

def calculate_compound_interest(principal, rate, time):
    return principal * ((1 + rate / 100) ** time - 1)


# Routes

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Please check your credentials and try again.', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out!', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    investments = Investment.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', name=current_user.email, investments=investments)


@app.route('/invest', methods=['GET', 'POST'])
@login_required
def invest():
    interest = None
    total_amount = None
    if request.method == 'POST':
        # Get form data
        amount = float(request.form['amount'])
        interest_rate = float(request.form['interest_rate'])
        time_period = float(request.form['time_period'])
        interest_type = request.form['interest_type']

        # Calculate interest
        if interest_type == 'simple':
            interest = calculate_simple_interest(amount, interest_rate, time_period)
        elif interest_type == 'compound':
            interest = calculate_compound_interest(amount, interest_rate, time_period)

        # Calculate total amount
        total_amount = amount + interest

        # Store investment in the database
        new_investment = Investment(
            user_id=current_user.id,
            amount=amount,
            interest_rate=interest_rate,
            time_period=time_period,
            interest_type=interest_type,
            interest=interest,
            total_amount=total_amount
        )
        db.session.add(new_investment)
        db.session.commit()

        flash('Investment added successfully!', 'success')

        # Don't redirect; just render the invest page with the calculated values
        return render_template('invest.html', interest=interest, total_amount=total_amount)

    return render_template('invest.html', interest=interest, total_amount=total_amount)


if __name__ == "__main__":
    # Binding to all network interfaces, so it's accessible outside the container
    app.run(host="0.0.0.0", port=5000, debug=True)

