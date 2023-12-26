# IMPORTS
import random

from sqlalchemy.orm import make_transient

from users.forms import RegisterForm
from flask import Blueprint, render_template, flash, redirect, url_for, session
from flask_login import current_user, login_required
from app import db, requires_roles
from models import User, Draw, decrypt

# CONFIG
admin_blueprint = Blueprint('admin', __name__, template_folder='templates')


# VIEWS
# View admin homepage
@admin_blueprint.route('/admin')
@login_required
@requires_roles('admin')
def admin():
    return render_template('admin/admin.html', name=current_user.firstname)


# Create a new winning draw
@admin_blueprint.route('/generate_winning_draw')
@login_required
@requires_roles('admin')
def generate_winning_draw():
    # Get current winning draw
    current_winning_draw = Draw.query.filter_by(master_draw=True).first()
    # Determines the lottery round
    lottery_round = 1

    # If a current winning draw exists
    if current_winning_draw:
        # Update lottery round by 1
        lottery_round = current_winning_draw.lottery_round + 1

        # Delete current winning draw from the database
        db.session.delete(current_winning_draw)
        db.session.commit()

    # Generates six random numbers within the range given
    winning_numbers = random.sample(range(1, 60), 6)
    # Sorts the winning numbers
    winning_numbers.sort()
    # Creates a string representation of the winning numbers
    winning_numbers_string = ''
    # Appends each winning number to the string
    for i in range(6):
        winning_numbers_string += str(winning_numbers[i]) + ' '
    winning_numbers_string = winning_numbers_string[:-1]

    # Creates a new draw object for the current user
    new_winning_draw = Draw(user_id=current_user.id, numbers=winning_numbers_string, master_draw=True,
                            lottery_round=lottery_round, draws_key=current_user.draws_key)

    # Adds the new winning draw to the database
    db.session.add(new_winning_draw)
    db.session.commit()

    # Displays message and then redirects to the admin page
    flash("New winning draw %s added." % winning_numbers_string)
    return redirect(url_for('admin.admin'))


# View current winning draw
@admin_blueprint.route('/view_winning_draw')
@login_required
@requires_roles('admin')
def view_winning_draw():
    # Get winning draw from the database
    current_winning_draw = Draw.query.filter_by(master_draw=True, been_played=False).first()

    # Check if a winning draw exists
    if current_winning_draw:
        creator = User.query.filter_by(id=current_winning_draw.user_id).first()
        make_transient(creator)
        current_winning_draw.view_draws(creator.draws_key)
        # re-render admin page with current winning draw and lottery round
        return render_template('admin/admin.html', winning_draw=current_winning_draw, name=current_user.firstname)

    # If no winning draw exists, display message and redirect to admin page
    flash("No valid winning draw exists. Please add new winning draw.")
    return redirect(url_for('admin.admin'))


# View lottery results and winners
@admin_blueprint.route('/run_lottery')
@login_required
@requires_roles('admin')
def run_lottery():
    # Get the current unplayed winning draw
    current_winning_draw = Draw.query.filter_by(master_draw=True, been_played=False).first()

    # Check if current unplayed winning draw exists
    if current_winning_draw:

        # Get all the unplayed user draws
        user_draws = Draw.query.filter_by(master_draw=False, been_played=False).all()
        results = []  # List to store the winners information

        # Check if at least one unplayed user draw exists
        if user_draws:

            # Update the current winning draw as played
            current_winning_draw.been_played = True
            db.session.add(current_winning_draw)
            db.session.commit()

            # Iterate through each unplayed user draw
            for draw in user_draws:

                # Get the corresponding user (instance/object)
                user = User.query.filter_by(id=draw.user_id).first()

                # if user draw matches current unplayed winning draw
                if draw.numbers == current_winning_draw.numbers:
                    # Update draw information using the creator's draw key
                    creator = User.query.filter_by(id=current_winning_draw.user_id).first()
                    make_transient(creator)
                    draw.view_draws(creator.draws_key)
                    # Add details of winner to list of results
                    results.append((current_winning_draw.lottery_round, draw.numbers, draw.user_id, user.email))

                    # Update the user draw as a winning draw
                    draw.matches_master = True

                # Update the user draw as played
                draw.been_played = True

                # update draw with current lottery round
                draw.lottery_round = current_winning_draw.lottery_round

                # Commit draw changes to the database
                db.session.add(draw)
                db.session.commit()

            # If there are no winners, display message
            if len(results) == 0:
                flash("No winners.")
            # Redirect to admin page with the winner's information
            return render_template('admin/admin.html', results=results, name=current_user.firstname)

        # If there are no user draws entered, display message
        flash("No user draws entered.")
        return admin()

    # If current unplayed winning draw does not exist, display message and redirect to admin page
    flash("Current winning draw expired. Add new winning draw for next round.")
    return redirect(url_for('admin.admin'))


# View all registered users
@admin_blueprint.route('/view_all_users')
@login_required
@requires_roles('admin')
def view_all_users():
    # Retrieve all registered users with the role pf 'user'
    current_users = User.query.filter_by(role='user').all()
    # Render the admin template with the current user's name and the list of the users
    return render_template('admin/admin.html', name=current_user.firstname, current_users=current_users)


# View last 10 log entries
@admin_blueprint.route('/logs')
@login_required
@requires_roles('admin')
def logs():
    # Read the lottery.log file and retrieve the last 10 lines
    with open("lottery.log", "r") as f:
        content = f.read().splitlines()[-10:]

        # Reverse the list to display the latest logs first
        content.reverse()
    # Render the admin template with the current user's name and the reversed log entries
    return render_template('admin/admin.html', logs=content, name=current_user.firstname)


@admin_blueprint.route('/registerAdmin', methods=['GET', 'POST'])
def register_admin():
    # Create a new instance of the 'RegisterForm' class for user registration
    form = RegisterForm()

    # Check if the form data is valid
    if form.validate_on_submit():
        # Check if a user already exists with the submitted email address
        admin = User.query.filter_by(email=form.email.data).first()

        # Check if the email address already exists, the display the error message
        if admin:
            flash('Email address already exists')
            return render_template('users/register.html', form=form)

        # Create a new 'User' object with the form data
        new_admin = User(email=form.email.data,
                         firstname=form.firstname.data,
                         lastname=form.lastname.data,
                         phone=form.phone.data,
                         date_of_birth=form.date_of_birth.data,
                         postcode=form.postcode.data,
                         password=form.password.data,
                         role='admin')

        # Add the admin user to the database
        db.session.add(new_admin)
        db.session.commit()

        # Redirects to admin page after new admin has been successfully registered and message has been displayed
        flash('New admin has been successfully registered!', 'success')
        return redirect(url_for('admin.admin'))

    # If the form data is valid, render the register template with the form
    return render_template('users/register.html', form=form)


@admin_blueprint.route('/userActivity', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def view_user_activity():
    # Retrieve all registered users with the role of 'user'
    current_users = User.query.filter_by(role='user').all()
    # Render the admin template with the current user's name and list of all the users
    return render_template('admin/admin.html', name=current_user.firstname, view_current_users=current_users)
