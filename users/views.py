# IMPORTS
from datetime import datetime

import bcrypt
from flask import Blueprint, render_template, flash, redirect, url_for, session, request
from flask_login import login_user, logout_user, current_user, login_required
from markupsafe import Markup

from app import db
from models import User
from users.forms import RegisterForm, LoginForm, PasswordForm
import logging

# CONFIG
users_blueprint = Blueprint('users', __name__, template_folder='templates')


# VIEWS
# View registration
@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    # Create a registration form object
    form = RegisterForm()

    # Check if request method is POST or form is valid
    if form.validate_on_submit():
        # Retrieve the user from the database with the provided email address
        user = User.query.filter_by(email=form.email.data).first()

        # If the user exists, it means that the email address is already registered
        if user:
            # Notify the user and render the register page with an error message
            flash('Email address already exists')
            return render_template('users/register.html', form=form)

        # Otherwise, create a new user object from the data in the form
        new_user = User(email=form.email.data,
                        firstname=form.firstname.data,
                        lastname=form.lastname.data,
                        phone=form.phone.data,
                        date_of_birth=form.date_of_birth.data,
                        postcode=form.postcode.data,
                        password=form.password.data,
                        role='user')

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # Log the user registration in lottery.log file
        logging.warning('SECURITY - User registration [%s, %s]',
                        form.email.data,
                        request.remote_addr
                        )

        # Store the user's email address in the session for future use
        session['email'] = new_user.email

        if 'email' not in session:
            # Redirect the user to main page
            return redirect(url_for('main.index'))

        # Redirect the user to set up 2-factor authentication
        return redirect(url_for('users.setup_2fa'))

    # If request method is GET or form not valid re-render signup page
    return render_template('users/register.html', form=form)


# Set up of 2-factor authentication
@users_blueprint.route('/setup_2fa')
def setup_2fa():
    # Check if the user's email address is stored in the session
    if 'email' not in session:
        # If the email address is not present, redirect the user to the main page
        return redirect(url_for('main.index'))

    # Retrieve the user object from the database using the email address
    user = User.query.filter_by(email=session['email']).first()
    # Check if the user object exists
    if not user:
        # If the user does not exist, redirect the user to the main page
        return redirect(url_for('main.index'))

    # Remove the email address from the session to prevent unauthorized access
    del session['email']

    # Render the 2FA setup page
    return render_template('users/setup_2fa.html', email=user.email, uri=user.get_2fa_uri()), \
           200, {
               'Cache-Control': 'no-cache, no-store, must-revalidate',
               'Pragma': 'no-cache',
               'Expires': '0'
           }


# View user login
@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    # Check if the current user is anonymous (not logged in)
    if current_user.is_anonymous:
        # Check if 'authentication_attempts' session variable exists, if not initialize it to 0
        if not session.get('authentication_attempts'):
            session['authentication_attempts'] = 0

        # Instantiate a login form object
        form = LoginForm()

        # If the request method is POST and the form is valid
        if form.validate_on_submit():
            # Retrieve the user from the database using the provided email address
            user = User.query.filter_by(email=form.email.data).first()

            # Check if the user exists, the password is valid, and the time-based PIN is valid
            if not user or not user.verify_password(form.password.data) or not user.verify_pin(
                    form.time_based_pin.data):

                # Authentication attempts are incremented by 1 every time the program enters the IF statement
                session['authentication_attempts'] += 1

                # Authentication attempts are limited to 3
                if session.get('authentication_attempts') >= 3:
                    flash(Markup('Number of incorrect login attempts exceeded.'
                                 'Please click <a href="/reset">here</a> to reset.'))

                    # Log the invalid login attempts in the 'lottery.log' file
                    logging.warning('SECURITY - Invalid log in attempts [%s, %s]',
                                    current_user.email,
                                    request.remote_addr
                                    )
                    # Redirect the user to the login page
                    return render_template('users/login.html')

                # Inform the user that their login details are incorrect and provide the remaining attempts
                flash('Please check your login details and try again, {} login attempts '
                      'remaining'.format(3 - session.get('authentication_attempts')))

            # If all validations pass, log the user in and store their session
            login_user(user)

            # Increment the user's total login count
            current_user.total_no_logins += 1
            # Log the successful user login in lottery.log file
            logging.warning('SECURITY - Log in [%s, %s, %s]',
                            current_user.id,
                            current_user.email,
                            request.remote_addr
                            )

            # Update the current user's details
            current_user.current_login = datetime.now()
            current_user.last_login = current_user.current_login
            current_user.current_ip = request.remote_addr
            current_user.last_ip = current_user.current_ip

            # Commit changes to the database
            db.session.commit()

            # Redirect the user to the appropriate page based on their role (user or admin)
            if current_user.role == 'user':
                return redirect(url_for('lottery.lottery'))
            else:
                return redirect(url_for('admin.admin'))

    else:
        # Redirect the logged-in user to the main page
        flash('You are already logged in.')
        return render_template('main/index.html')

    return render_template('users/login.html', form=form)


@users_blueprint.route('/reset')
def reset():
    # Reset the authentication attempts counts to 0
    session['authentication_attempts'] = 0
    # Redirect the user to the login page
    return redirect(url_for('users.login'))


@users_blueprint.route('/logout')
@login_required
def logout():
    # Logging the user log out in logging.log file
    logging.warning('SECURITY - Log out [%s, %s, %s]',
                    current_user.id,
                    current_user.email,
                    request.remote_addr
                    )
    # Clear the user's login session
    logout_user()
    # Redirect the user to the main page
    return redirect(url_for('index'))


# View user account
@users_blueprint.route('/account')
@login_required
def account():
    return render_template('users/account.html',
                           acc_no=current_user.id,
                           email=current_user.email,
                           firstname=current_user.firstname,
                           lastname=current_user.lastname,
                           phone=current_user.phone,
                           date_of_birth=current_user.date_of_birth,
                           postcode=current_user.postcode,
                           role=current_user.role)


@users_blueprint.route('/update_password', methods=['GET', 'POST'])
@login_required
def update_password():
    # Create a password update form object
    form = PasswordForm()

    # If the request method is POST and the form is valid
    if form.validate_on_submit():
        # To check if the current password entered does not match the password stored in the database
        if not current_user.verify_password(form.current_password.data):
            # Notify the user that the current password is incorrect
            flash('Current password is incorrect')

            # Render the update password page with the form for the user to try again
            return render_template('users/update_password.html', form=form)

        # To check if new password entered matches current password stored for user in database
        if form.new_password.data == form.current_password.data:
            # Notify the user that the new password must be different from the current password
            flash('New password must be different from current password')

            # Render the update password page with the form for the user to change the password again
            return render_template('users/update_password.html', form=form)

        # Hash the new password using bcrypt
        current_user.password = bcrypt.hashpw(form.new_password.data.encode('utf-8'), bcrypt.gensalt())
        # Commit the changes to the database
        db.session.commit()

        # Notify the user that the password change was successful
        flash('Password changed successfully')

        # Redirect the user to their account page
        return redirect(url_for('users.account'))

    # If the request method is GET or the form is invalid, render the update password page with the form
    return render_template('users/update_password.html', form=form)
