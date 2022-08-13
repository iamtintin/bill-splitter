from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

from datetime import datetime
from werkzeug import security

db = SQLAlchemy()

# Model for User Table with links to user-bill components, friends, friend requests, party memberships and notifications
class User(UserMixin, db.Model):
    __tablename__='user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(200), unique=True)
    password = db.Column(db.String(100))
    bills = db.relationship('UserBill', backref='user', lazy='dynamic')
    parties = db.relationship('PartyMember', backref='user', lazy='dynamic')
    friends = db.relationship('Friend', primaryjoin="or_(User.id==Friend.user_id1, User.id==Friend.user_id2)", lazy='dynamic')
    friendrequests = db.relationship('FriendRequest', primaryjoin="or_(User.id==FriendRequest.user_id1, User.id==FriendRequest.user_id2)", lazy='dynamic')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')

    def __init__(self, username, fullname, email, password):
        self.username = username
        self.name = fullname
        self.email = email
        self.password = password

# Model for Table of Friend relationships between Users, with back references to users
class Friend(db.Model):
    __tablename__='friends'
    id = db.Column(db.Integer, primary_key=True)
    user_id1 = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_id2 = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, id1, id2):
        self.user_id1 = id1
        self.user_id2 = id2

# Model for Table of Friend Requests from 1 user to another, with back references to users
class FriendRequest(db.Model):
    __tablename__='friendrequests'
    id = db.Column(db.Integer, primary_key=True)
    user_id1 = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_id2 = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, id1, id2):
        self.user_id1 = id1
        self.user_id2 = id2

# Model for Table of Partys with links to party-bills and party memberships
class Party(db.Model):
    __tablename__='party'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    admin = db.Column(db.Boolean) # Admin True -> Admin-type Party && False -> Equal-type Party
    bills = db.relationship('Bill', backref='party')
    members = db.relationship('PartyMember', backref='party', lazy='dynamic')

    def __init__(self, name, admin):
        self.name = name
        self.admin = admin

# Model for Table of Party Memberships with back references to party and user
class PartyMember(db.Model):
    __tablename__='partymembers'
    id = db.Column(db.Integer, primary_key=True)
    party_id = db.Column(db.Integer, db.ForeignKey('party.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    role = db.Column(db.Boolean) # Role True -> Admin && False -> Non-Admin

    def __init__(self, pid, uid, role):
        self.party_id = pid
        self.user_id = uid
        self.role = role

# Model for Table of Party-bills with back-reference to party and links to all its bill components    
class Bill(db.Model):
    __tablename__='bill'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50)) 
    description = db.Column(db.String(200))
    party_id = db.Column(db.Integer, db.ForeignKey('party.id'))
    status = db.Column(db.Boolean)
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    amount = db.Column(db.Float)
    paid = db.Column(db.Float)
    user_bills = db.relationship('UserBill', backref='bill', lazy='dynamic')

    def __init__(self, name, dscrp, pid, startDT, endDT, amount):
        self.name = name
        self.description = dscrp
        self.party_id = pid
        self.status = False
        self.start = startDT
        self.end = endDT
        self.amount = amount
        self.paid = 0

# Model for Table of User-Bill components with back references to user and bill
class UserBill(db.Model):
    __tablename__='userbill'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'))
    amount = db.Column(db.Float)
    status = db.Column(db.Boolean)
    confirmed = db.Column(db.Boolean)
    paid_dt = db.Column(db.DateTime)
    seen = db.Column(db.Boolean)

    def __init__(self, uid, bid, amount, paidDT):
        self.user_id = uid
        self.bill_id = bid
        self.amount = amount
        self.status = False
        self.confirmed = False
        self.paid_dt = paidDT
        self.seen = False

# Model for Table of Notifications with back reference to user
class Notification(db.Model):
    __tablename__='notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.String(300))
    dt = db.Column(db.DateTime)

    def __init__(self, uid, content, dt):
        self.user_id = uid
        self.content = content
        self.dt = dt

# Resets Database when called
def dbinit():
    db.drop_all()
    db.create_all()
    print("Database Reset.")
