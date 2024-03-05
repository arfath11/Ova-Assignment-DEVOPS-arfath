from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user
import pyrebase

auth = Blueprint('auth', __name__)


firebaseConfig = {
  "apiKey": "AIzaSyBRrQeFV8TUDyzSSsJYw3E-ZCiorKUyXB0",
  "authDomain": "devops-authenticaiton.firebaseapp.com",
  "projectId": "devops-authenticaiton",
  "storageBucket": "devops-authenticaiton.appspot.com",
  "messagingSenderId": "640521249367",
  "appId": "1:640521249367:web:cafba7d959be0242ed3912",
  "measurementId": "G-Q1ZEETV5QJ",
  "databaseURL": ""
}

firebase = pyrebase.initialize_app(firebaseConfig)
authf = firebase.auth()



@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if (user.password == password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=password1)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            
            user = authf.create_user_with_email_and_password(email, password1)
            # Log the user in
            #user = authf.sign_in_with_email_and_password(email, password)
            print(user)

            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)
