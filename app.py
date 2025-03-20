import os 
from email_validator import validate_email, EmailNotValidError
from flask import Flask, render_template, redirect, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,TextAreaField
from wtforms.validators import DataRequired, Email, ValidationError
from flask_sqlalchemy import SQLAlchemy 
from flask_migrate import Migrate
from sqlalchemy import Column, String, Integer
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Hide key in hash table before psoting
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


# Configure database using environment variable
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URL', 'sqlite:///email.db')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)
migrate = Migrate(app, db)

# db model 
class EmailEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)


# Custom Validators 

# Custom email validator 
def validate_message_length(field): 
        max_length = 500 # define maximum allowed message length 
        if len(field.data) > max_length: 
            raise ValidationError(f'Message cannot be longer than {max_length} characters')

# Custom message length validator 
def validate_email_address(field): 
    try: 
        # validate email using the email_validator package 
        validate_email(field.data)
    except EmailNotValidError as e: 
        raise ValidationError("Invalid email addresss.")

# Flask-WTF form 
class EmailForm(FlaskForm):
    email = StringField('Email: ', validators=[DataRequired(), validate_email_address])
    message = TextAreaField('Message: ', validators=[DataRequired(), validate_message_length])
    submit = SubmitField('Submit')


def handle_email_submission(form): 
    email = form.email.data
    message =form.message.data

    
    new_entry = EmailEntry(email=email, message=message)
    db.session.add(new_entry)
    db.session.commit()
    flash(f'Email "{email}" submitted successfully!', 'success')

    return redirect(request.path)


@app.route('/', methods=['GET','POST'])
def home(): 
    form = EmailForm()
    if form.validate_on_submit():
        return handle_email_submission(form)
    return render_template('home.html', form=form)

@app.route('/guide', methods=['GET','POST'])
def guide():
    form = EmailForm()
    if form.validate_on_submit(): 
        return handle_email_submission(form)
    return render_template('guide.html', form=form)

if __name__ =='__main__':
    with app.app_context():
        db.create_all()
    
    