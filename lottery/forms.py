from flask import flash
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange, ValidationError


# added validators to ensure that the draw contains 6 entries and that each
# number is within the range with error messages
class DrawForm(FlaskForm):
    number1 = IntegerField(id='no1',
                           validators=[DataRequired(), NumberRange(1, 60, message="Must be between 1 and 60")])
    number2 = IntegerField(id='no2',
                           validators=[DataRequired(), NumberRange(1, 60, message="Must be between 1 and 60")])
    number3 = IntegerField(id='no3',
                           validators=[DataRequired(), NumberRange(1, 60, message="Must be between 1 and 60")])
    number4 = IntegerField(id='no4',
                           validators=[DataRequired(), NumberRange(1, 60, message="Must be between 1 and 60")])
    number5 = IntegerField(id='no5',
                           validators=[DataRequired(), NumberRange(1, 60, message="Must be between 1 and 60")])
    number6 = IntegerField(id='no6',
                           validators=[DataRequired(), NumberRange(1, 60, message="Must be between 1 and 60")])
    submit = SubmitField("Submit Draw")

    # custom validator that ensures each number is unique by accessing all the form's fields
    def validate(self, **kwargs):
        standard_validators = FlaskForm.validate(self)
        if standard_validators:
            # put numbers in a list
            numbers = [self.number1, self.number2, self.number3, self.number4, self.number5, self.number6]
        # if length is not 6 raise a validation error
        if len != 6:
            flash('All numbers entered must be unique')

        return False
