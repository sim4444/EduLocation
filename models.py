from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

# Create Flask App
app = Flask(__name__)
# SQL Alchemy Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///locations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create a database
db = SQLAlchemy(app)

#Initialize table
#Table consist of: name, location, hours of operation, contact information, link to website, type of location
class Locations(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100))
    address = db.Column(db.String(100))
    hours = db.Column(db.String(100))
    link = db.Column(db.String(100))
    phone = db.Column(db.String(100))
    location_type = db.Column(db.String(100))

    def __init__(self, name, city, address, hours, link, phone, location_type):
        self.name = name
        self.city = city
        self.address = address
        self.hours = hours
        self.link = link
        self.phone = phone
        self.location_type = location_type

# Allowing user to request a location
class RequestLocation(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100))
    address = db.Column(db.String(100), unique=True)
    hours = db.Column(db.String(100))
    link = db.Column(db.String(100))
    phone = db.Column(db.String(100))
    location_type = db.Column(db.String(100))

    def __init__(self, name, city, address, hours, link, phone, location_type):
        self.name = name
        self.city = city
        self.address = address
        self.hours = hours
        self.link = link
        self.phone = phone
        self.location_type = location_type

# Create a Form Class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    city = StringField("City", validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired()])
    hours = StringField("Hours of Operation", validators=[DataRequired()])
    link = StringField("Link to Website", validators=[DataRequired()])
    phone = StringField("Phone Number", validators=[DataRequired()])
    location_type = StringField("Type of Location", validators=[DataRequired()])
    submit = SubmitField("Submit")