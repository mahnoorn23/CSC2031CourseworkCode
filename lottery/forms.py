from flask import flash
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, validators
from wtforms.validators import DataRequired, NumberRange, ValidationError


# Custom validator that ensures each number is unique by accessing all the form's fields
def validate_numbers(form, field):
    # Extract numbers from the form fields into a list
    numbers = [form.number1.data, form.number2.data, form.number3.data,
               form.number4.data, form.number5.data, form.number6.data]
    unique_number = set(numbers)
    # Check if length of the numbers in the list is equal to six
    if len(unique_number) != 6:
        # Raise a validation error if the length is not six
        raise validators.ValidationError('All numbers entered must be unique')


class DrawForm(FlaskForm):
    # Defining each individual number field with validation
    number1 = IntegerField(id='no1',
                           validators=[DataRequired(), NumberRange(1, 60, message="Must be between 1 and 60"),
                                       validate_numbers])
    number2 = IntegerField(id='no2',
                           validators=[DataRequired(), NumberRange(1, 60, message="Must be between 1 and 60"),
                                       validate_numbers])
    number3 = IntegerField(id='no3',
                           validators=[DataRequired(), NumberRange(1, 60, message="Must be between 1 and 60"),
                                       validate_numbers])
    number4 = IntegerField(id='no4',
                           validators=[DataRequired(), NumberRange(1, 60, message="Must be between 1 and 60"),
                                       validate_numbers])
    number5 = IntegerField(id='no5',
                           validators=[DataRequired(), NumberRange(1, 60, message="Must be between 1 and 60"),
                                       validate_numbers])
    number6 = IntegerField(id='no6',
                           validators=[DataRequired(), NumberRange(1, 60, message="Must be between 1 and 60"),
                                       validate_numbers])
    # Submit button to submit the form
    submit = SubmitField("Submit Draw")
