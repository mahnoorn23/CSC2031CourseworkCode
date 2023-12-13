import pyotp
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length, EqualTo, ValidationError
import re


def character_check(form, field):
    excluded_chars = "*?!'^+%&/()=}][{$#@<>"
    for char in field.data:
        if char in excluded_chars:
            raise ValidationError(f"Character {char} is not allowed.")


def validate_phone(form, phone):
    p = re.compile(r'(^\d{4}-\d{3}-\d{4}$)')
    if not p.match(phone.data):
        raise ValidationError("Must have the format XXXX-XXX-XXXX")


def validate_password(form, password):
    p = re.compile(r'(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*\W|_)')
    if not p.match(password.data):
        raise ValidationError("Must contain 1 digit, 1 uppercase letter, 1 lower case letter and 1 special character")


def validate_dob(form, dob):
    p = re.compile(r'^(0[1-9]|[1-2][0-9]|3[0-1])/(0[1-9]|1[0-2])/(19|20)\d{2}$')
    if not p.match(dob.data):
        raise ValidationError("Must be of the format DD/MM/YYYY - D (Day), M (Month), Y (Year)")


def validate_postcode(form, postcode):
    p = re.compile(r'^[A-Z]{1,2}\d{1,2}\s\d[A-Z]{2}$')
    if not p.match(postcode.data):
        raise ValidationError("Must be of the format XY YXX, XYY YXX or XXY YXX "
                              "where X is an uppercase letter and Y is a digit")


class RegisterForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email()])
    firstname = StringField(validators=[InputRequired(), character_check])
    lastname = StringField(validators=[InputRequired(), character_check])
    phone = StringField(validators=[InputRequired(), validate_phone])
    date_of_birth = StringField(validators=[InputRequired(), validate_dob, Length(8)])
    postcode = StringField(validators=[InputRequired(), validate_postcode])
    password = PasswordField(validators=[InputRequired(), Length(min=6, max=12), validate_password])
    confirm_password = PasswordField(validators=[InputRequired(), EqualTo('password',
                                                                          message="Must be the same as above")])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email()])
    password = PasswordField(validators=[InputRequired(), validate_password])
    time_based_pin = StringField(validators=[InputRequired(), Length(6)])
    postcode = StringField(validators=[InputRequired(), validate_postcode])
    recaptcha = RecaptchaField()
    submit = SubmitField('Login')


class PasswordForm(FlaskForm):
    current_password = PasswordField(id='password', validators=[InputRequired()])
    show_password = BooleanField('Show password', id='check')
    new_password = PasswordField(validators=[InputRequired(), Length(min=6, max=12,
                                                                     message="Must be between 6 and 12 characters "
                                                                             "in length"), validate_password])
    confirm_new_password = PasswordField(validators=[InputRequired(),
                                                     EqualTo('new_password',
                                                             message='Both new password fields must be equal')])
    submit = SubmitField('Change Password')
