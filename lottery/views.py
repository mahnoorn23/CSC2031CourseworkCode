# IMPORTS

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from sqlalchemy.orm import make_transient

from app import db, requires_roles
from lottery.forms import DrawForm
from models import Draw, User

# CONFIG
lottery_blueprint = Blueprint('lottery', __name__, template_folder='templates')


# VIEWS
# View lottery page
@lottery_blueprint.route('/lottery')
@login_required
@requires_roles('user')
def lottery():
    # Render lottery template
    return render_template('lottery/lottery.html', name=current_user.firstname)


# View all draws that have not been played
@lottery_blueprint.route('/create_draw', methods=['POST'])
@login_required
@requires_roles('user')
def create_draw():
    # Create an instance of the DrawForm
    form = DrawForm()

    # If form is valid i.e. all the fields are filled in correctly
    if form.validate_on_submit():
        # Extract the submitted numbers from the form fields
        submitted_numbers = (str(form.number1.data) + ' '
                          + str(form.number2.data) + ' '
                          + str(form.number3.data) + ' '
                          + str(form.number4.data) + ' '
                          + str(form.number5.data) + ' '
                          + str(form.number6.data))

        # Create a new draw with the form data
        new_draw = Draw(user_id=current_user.id, numbers=submitted_numbers, master_draw=False, lottery_round=0,
                        draws_key=current_user.draws_key)
        # Add the new draw to the database
        db.session.add(new_draw)
        db.session.commit()

        # Notify the user that the draw was submitted
        flash('Draw %s submitted.' % submitted_numbers)
        # Redirect to the lottery page to display the submitted draw
        return redirect(url_for('lottery.lottery'))

    # If the form is invalid, render the lottery page with the form
    return render_template('lottery/lottery.html', name=current_user.firstname, form=form)


# View all draws that have not been played
@lottery_blueprint.route('/view_draws', methods=['POST'])
@login_required
@requires_roles('user')
def view_draws():
    # Retrieve all draws that have not been played [played=False]
    playable_draws = Draw.query.filter_by(been_played=False, user_id=current_user.id).all()

    # Check if any playable draws exist
    if len(playable_draws) != 0:
        # If playable draws exist, decrypt them for viewing by the user
        for draw in playable_draws:
            # Make each draw transient to allow decryption
            make_transient(draw)
            # Update the draw's numbers using the user's draws key
            creator = User.query.filter_by(id=draw.user_id).first()
            draw.view_draws(creator.draws_key)

        # Render lottery page with playable draws
        return render_template('lottery/lottery.html', playable_draws=playable_draws)
    # If no playable draw exists, notify the user and redirect to lottery page
    else:
        flash('No playable draws.')
        return lottery()


# View lottery results
@lottery_blueprint.route('/check_draws', methods=['POST'])
@login_required
@requires_roles('user')
def check_draws():
    # Get all played draws for the current user
    played_draws = Draw.query.filter_by(been_played=True, user_id=current_user.id).all()

    # Check if played draws exist
    if len(played_draws) != 0:
        # If they exist, render the lottery page with the played draws
        return render_template('lottery/lottery.html', results=played_draws, played=True)

    # If no played draws exist, notify the user about the next round of lottery
    else:
        flash("Next round of lottery yet to play. Check you have playable draws.")
        return lottery()


# Delete all played draws
@lottery_blueprint.route('/play_again', methods=['POST'])
@login_required
@requires_roles('user')
def play_again():
    # Delete all played draws created by the current user
    Draw.query.filter_by(been_played=True, master_draw=False, user_id=current_user.id).delete(synchronize_session=False)
    db.session.commit()

    # Notify the current user that all played draws have been deleted and the redirect to lottery page
    flash("All played draws deleted.")
    return lottery()


