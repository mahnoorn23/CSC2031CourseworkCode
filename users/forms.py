import pyotp
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length, EqualTo, ValidationError
import re


def character_check(form, field):
    # Defining a set of excluded characters that are not allowed
    excluded_chars = "*?!'^+%&/()=}][{$#@<>"
    # Iterate through each character in the field's data
    for char in field.data:
        # Check if the current character is in the set of excluded characters
        if char in excluded_chars:
            # Raise a validation error indicating the disallowed character
            raise ValidationError(f"Character {char} is not allowed.")


def validate_phone(form, phone):
    # Creating a regex pattern for matching the given phone number format
    p = re.compile(r'(^\d{4}-\d{3}-\d{4}$)')

    # Check if the phone number data matches the regular expression pattern
    if not p.match(phone.data):
        # Raise a validation error if the phone number format is incorrect
        raise ValidationError("Must have the format XXXX-XXX-XXXX")


def validate_password(form, password):
    # Creating a regex pattern for matching the password with the given requirements
    p = re.compile(r'(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*\W|_)')

    # Check if the password data matches the regular expression data
    if not p.match(password.data):
        # Raise a validation error if the password doesn't match the requirements
        raise ValidationError("Must contain 1 digit, 1 uppercase letter, 1 lower case letter and 1 special character")


def validate_dob(form, dob):
    # Creating a regex pattern for matching the date of birth with the given format
    p = re.compile(r'^(0[1-9]|[1-2][0-9]|3[0-1])/(0[1-9]|1[0-2])/(19|20)\d{2}$')

    # Check if the date of birth matches the regex expression
    if not p.match(dob.data):
        # Raise a validation error if the date of birth is in the incorrect format
        raise ValidationError("Must be of the format DD/MM/YYYY - D (Day), M (Month), Y (Year)")


def validate_postcode(form, postcode):
    # Creating a regex pattern for matching the postcode with the given format
    p = re.compile(r'^[A-Z]{1,2}\d{1,2}\s\d[A-Z]{2}$')

    # Check if the postcode matches the regex expression
    if not p.match(postcode.data):
        # Raise a validation error if the postcode is in the incorrect format
        raise ValidationError("Must be of the format XY YXX, XYY YXX or XXY YXX "
                              "where X is an uppercase letter and Y is a digit")


class RegisterForm(FlaskForm):
    # Define form fields with validators for registration form
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
    # Define form fields with validators for login form
    email = StringField(validators=[InputRequired(), Email()])
    password = PasswordField(validators=[InputRequired(), validate_password])
    time_based_pin = StringField(validators=[InputRequired(), Length(6)])
    postcode = StringField(validators=[InputRequired(), validate_postcode])
    recaptcha = RecaptchaField()
    submit = SubmitField('Login')


class PasswordForm(FlaskForm):
    # Define form fields with validators for password form
    current_password = PasswordField(id='password', validators=[InputRequired()])
    show_password = BooleanField('Show password', id='check')
    new_password = PasswordField(validators=[InputRequired(), Length(min=6, max=12,
                                                                     message="Must be between 6 and 12 characters "
                                                                             "in length"), validate_password])
    confirm_new_password = PasswordField(validators=[InputRequired(),
                                                     EqualTo('new_password',
                                                             message='Both new password fields must be equal')])
    submit = SubmitField('Change Password')
