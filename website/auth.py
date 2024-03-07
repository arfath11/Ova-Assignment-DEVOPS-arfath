from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user
import pyrebase
import os

auth = Blueprint('auth', __name__)



firebaseConfig = {
    "apiKey": os.getenv("API_KEY"),
    "authDomain": os.getenv("AUTH_DOMAIN"),
    "projectId": os.getenv("PROJECT_ID"),
    "storageBucket": os.getenv("STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("MESSAGING_SENDER_ID"),
    "appId": os.getenv("APP_ID"),
    "measurementId": os.getenv("MEASUREMENT_ID"),
    "databaseURL": ""
}





firebase = pyrebase.initialize_app(firebaseConfig)
authf = firebase.auth()



@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')


        try:
            # Attempt user sign-in using Pyrebase
            userf = authf.sign_in_with_email_and_password(email, password)
            user = User.query.filter_by(email=email).first()

            # If no exception is thrown, sign-in was successful
            # (You can access the user details from `userf`)
            flash('Logged in successfully!', category='success')
            #login_user(userf['localId'], remember=True)  # Use 'localId' for Flask-Login
            login_user(user, remember=True)


            return redirect(url_for('views.home')) 
        
        except:
           flash('Incorrect password or email , try again.', category='error')

            
            
      

        



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
            user = authf.sign_in_with_email_and_password(email, password1)
            print(user)

            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)
