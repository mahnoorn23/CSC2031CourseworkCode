# IMPORTS
from datetime import datetime

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
# view registration
@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    # create signup form object
    form = RegisterForm()

    # if request method is POST or form is valid
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # if this returns a user, then the email already exists in database

        # if email already exists redirect user back to signup page with error message so user can try again
        if user:
            flash('Email address already exists')
            return render_template('users/register.html', form=form)

        new_user = User(email=form.email.data,
                        firstname=form.firstname.data,
                        lastname=form.lastname.data,
                        phone=form.phone.data,
                        date_of_birth=form.date_of_birth.data,
                        postcode=form.postcode.data,
                        password=form.password.data,
                        role='user')

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # logging user registration in lottery.log
        logging.warning('SECURITY - User registration [%s, %s]',
                        form.email.data,
                        request.remote_addr
                        )

        session['email'] = new_user.email
        if 'email' not in session:
            return redirect(url_for('main.index'))
        # sends user to login page

        # sends user to 2-factor authentication
        return redirect(url_for('users.setup_2fa'))

    # if request method is GET or form not valid re-render signup page
    return render_template('users/register.html', form=form)


@users_blueprint.route('/setup_2fa')
def setup_2fa():
    if 'email' not in session:
        return redirect(url_for('main.index'))
    user = User.query.filter_by(email=session['email']).first()
    if not user:
        return redirect(url_for('main.index'))
    del session['email']
    return render_template('users/setup_2fa.html', email=user.email, uri=user.get_2fa_uri()), \
           200, {
               'Cache-Control': 'no-cache, no-store, must-revalidate',
               'Pragma': 'no-cache',
               'Expires': '0'
           }


# view user login
@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_anonymous:
        if not session.get('authentication_attempts'):
            session['authentication_attempts'] = 0

        form = LoginForm()

        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()

            if not user or not user.verify_password(form.password.data) or not user.verify_pin(
                    form.time_based_pin.data):
                # authentication attempts are incremented by 1 every time the program enters the IF statement
                session['authentication_attempts'] += 1
                # authentication attempts are limited to 3
                if session.get('authentication_attempts') >= 3:
                    flash(Markup('Number of incorrect login attempts exceeded.'
                                 'Please click <a href="/reset">here</a> to reset.'))
                    # invalid log in attempts being logged in logging.log
                    logging.warning('SECURITY - Invalid log in attempts [%s, %s]',
                                    current_user.email,
                                    request.remote_addr
                                    )
                    return render_template('users/login.html')

                flash('Please check your login details and try again, {} login attempts '
                      'remaining'.format(3 - session.get('authentication_attempts')))

            login_user(user)
            current_user.total_no_logins += 1
            # logging user login in lottery.log
            logging.warning('SECURITY - Log in [%s, %s, %s]',
                            current_user.id,
                            current_user.email,
                            request.remote_addr
                            )
            current_user.current_login = datetime.now()
            current_user.last_login = current_user.current_login
            current_user.current_ip = request.remote_addr
            current_user.last_ip = current_user.current_ip
            db.session.commit()

            if current_user.role == 'user':
                return redirect(url_for('lottery.lottery'))
            else:
                return redirect(url_for('admin.admin'))

    else:
        flash('You are already logged in.')
        return render_template('main/index.html')

    return render_template('users/login.html', form=form)


@users_blueprint.route('/reset')
def reset():
    session['authentication_attempts'] = 0
    return redirect(url_for('users.login'))


@users_blueprint.route('/logout')
@login_required
def logout():
    # logging the user log out in logging.log
    logging.warning('SECURITY - Log out [%s, %s, %s]',
                    current_user.id,
                    current_user.email,
                    request.remote_addr
                    )
    logout_user()
    return redirect(url_for('index'))


# view user account
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
    form = PasswordForm()

    if form.validate_on_submit():
        # To check if the current password entered does not match the password stored in the database
        if current_user.password != form.current_password.data:
            flash('Current password is incorrect')
            return render_template('users/update_password.html', form=form)

        # To check if new password entered matches current password stored for user in database
        if form.new_password.data == form.current_password.data:
            flash('New password must be different from current password')
            return render_template('users/update_password.html', form=form)

        current_user.password = form.new_password.data
        db.session.commit()
        flash('Password changed successfully')
        return redirect(url_for('users.account'))

    return render_template('users/update_password.html', form=form)
