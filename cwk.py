from flask import Flask, render_template, redirect, request, send_from_directory, url_for
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_, and_

from db_schema import db, User, Friend, FriendRequest, Party, PartyMember, Bill, UserBill, Notification, dbinit

from werkzeug import security
from markupsafe import escape

from datetime import datetime, timedelta
import os

''' ----------------------------------------------------------------------------
                            SETUP
-----------------------------------------------------------------------------'''

# Initialise and Configure Flask App and Datebase
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///bills.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME']=timedelta(days=1)
app.secret_key = 'secretkeyrequiredforsessions'

db.init_app(app)

resetdb = False
if resetdb:
    with app.app_context():
        dbinit()

# Initialise and Configure Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.session_protection = "strong"

# Login Manager method to return current user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Error Handling Page for 404 Error - Route does not exist
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

# Favicon Route for older browsers
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'img'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Security Response Header Config
@app.after_request
def add_header(response):
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response


''' ----------------------------------------------------------------------------
                            LOGIN
-----------------------------------------------------------------------------'''

# Redirect common routes to login
@app.route('/index')
@app.route('/')
def index():
    return redirect(url_for('login'))


# Route for Login page
@app.route('/login', methods=['GET','POST'])
def login():
    # Redirect to Overview page if Logged in
    if current_user.is_authenticated:
        return redirect(url_for('overview'))
    
    # Handle POST Form
    if request.method == "POST":
        data = {
            'error': ""
        }

        # Retrieve Form Data
        email = escape(request.form['email'])
        password = escape(request.form['user_pass'])

        # Check whether User exists 
        user = User.query.filter_by(email = email).first()

        if user is None:
            data["error"] = "Incorrect Email or Password"
            return data

        # Check if password is correct
        if not security.check_password_hash(user.password, password):
            data["error"] = "Incorrect Email or Password"
            return data
        
        # Log in User
        login_user(user)
        return data

    # Render Login page
    if request.method == "GET":
        return render_template('login.html')


# Route for Register page
@app.route('/register', methods=['GET','POST'])
def register():
    # Redirect to Overview page is Logged in
    if current_user.is_authenticated:
        return redirect(url_for("overview"))
    
    # Handle POST Form
    if request.method == "POST":
        data = {
            'error': ""
        }

        # Retrieve Form Data
        name = escape(request.form['name'])
        username = escape(request.form['username'])
        email = escape(request.form['email'])
        password = escape(request.form['user_pass'])

        # Generate Hashed Password
        password_hash = security.generate_password_hash(password)

        # Attempt to Add User to database with error handling if invalid 
        try:
            new_user = User(username, name, email, password_hash, )
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            data["error"] = "Unable to register User. Note: Username and Email must be unique."
            return data
        
        # Log in User
        login_user(new_user)
        return data
    
    # Render Register page
    if request.method == "GET":
        return render_template('register.html')


# Route to Log out User Session with redirect to Login page
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

''' ----------------------------------------------------------------------------
                            MAIN PAGES
-----------------------------------------------------------------------------'''

# Route for Main Overview Page 
@app.route('/overview')
@login_required
def overview():
    # Retrieve user's unpaid bills and sort from newest to oldest
    bill_data = current_user.bills.filter_by(status=False).join(UserBill.bill).order_by(Bill.start.desc())
    confirmations = []

    # Retrieve any payments that need confirmation in any of the parties where the user is an admin
    for membership in current_user.parties:
        if membership.role and membership.party.admin:
            for bill in membership.party.bills:
                # Retrieve user bill components that need confirmation in currently considered party
                user_bills = bill.user_bills.filter(and_(UserBill.status==True, UserBill.confirmed==False)).all()
                if len(user_bills) > 0:
                    confirmations += user_bills

    # Get current date & time to compare datetimes
    current = datetime.now()
    
    # Render page with the unpaid bills, confirmations that need to be made and the current date & time
    return render_template('overview.html', bills=bill_data, bill_confirm=confirmations, time=current)


# Route for Overview of Bills Page
@app.route('/billoverview')
@login_required
def billoverview():
    # Retrieve user's bills
    bill_data = current_user.bills

    # Initialise empty variables required for rendering
    unpaid = []
    paid = []
    t_pay = 0
    t_paid = 0
    confirmations = []
    
    # Sort user's bills in paid bills and unpaid bills (+ calculate amounts)
    for bill in bill_data:
        if bill.status:
            paid.append(bill)
            t_paid += bill.amount
        else:
            unpaid.append(bill)
            t_pay += bill.amount
    
    # Retrieve any payments that need confirmation in any of the parties where the user is an admin
    for membership in current_user.parties:
        if membership.role and membership.party.admin:
            for bill in membership.party.bills:
                # Retrieve user bill components that need confirmation in currently considered party
                user_bills = bill.user_bills.filter(and_(UserBill.status==True, UserBill.confirmed==False)).all()
                if len(user_bills) > 0:
                    confirmations += user_bills

    # Get current date & time to compare datetimes
    current_time = datetime.now()

    # Render page with the paid bills, unpaid bills, confirmations that need to be made, current date & time and the total amounts paid/unpaid
    return render_template('billoverview.html', paid_bills=paid, unpaid_bills=unpaid, confirmreq=confirmations, time=current_time, total_pending=t_pay, total_paid=t_paid)

# Route for Overview of Parties and Friends Page
@app.route('/partyoverview')
@login_required
def partyoverview():
    # Retrieve user's parties, friends and friend requests
    parties = current_user.parties
    friends = current_user.friends
    friend_requests = current_user.friendrequests

    # Initialise empty variables required for rendering
    user_friends = []
    requests = []
    pending = []

    # For each friend, store the friend's user object and all common parties between the friend and current user
    for friend in friends: 
        # Retrieve friend's user object
        uid = friend.user_id1 if friend.user_id2 == current_user.id else friend.user_id2
        user = User.query.filter_by(id=uid).first()
        # Retrieve common parties between current user and friend
        common_parties = []
        for party in user.parties:
            if current_user.parties.filter_by(party_id=party.party_id).first() is not None:
                common_parties.append(party.party.name)
        user_friends.append([user, common_parties])

    # For each friend request, retrieve corresponding user object and into outgoing and ingoing requests
    for request in friend_requests:
        if request.user_id1 == current_user.id:
            pending.append([User.query.filter_by(id=request.user_id2).first(), request.id])
        else:
            requests.append([User.query.filter_by(id=request.user_id1).first(), request.id])

    # Render page with the parties, friends, incoming friend requests and outgoing friend requests
    return render_template('partyoverview.html', parties=parties, friends=user_friends, requests=requests, pending=pending)  

''' ----------------------------------------------------------------------------
                            BILL MANAGEMENT
-----------------------------------------------------------------------------'''

#                           VIEW BILL

# Route for page for viewing a user's bill component
@app.route('/focusedbill/<bill_id>')
@login_required
def focusedbill(bill_id):
    bill_id = escape(bill_id)
    # Retrieve corresponding bill component from database
    userbill = UserBill.query.filter_by(id=bill_id).first()
    msg=""
    
    # Check if bill component exists and if it belongs to the current user
    if userbill == None: 
        msg = "User has no such bill"
    elif userbill.user.id != current_user.id:
        msg = "User has no such bill"

    # Render page with the bill component objectand a possible error message
    return render_template('focusedbill.html', item=userbill, err=msg)

#                           PAY BILL


# Route for AJAX Bill Payment
@app.route('/paybill', methods=['GET','POST'])
@login_required
def paybillajax():
    # Handle Correct POST method
    if request.method == "POST":
        # Initialise dictionary (JSON) to return
        data = {
            'error': "",
            'paid_dt': "",
            'confirmed': False,
        }

        # Retrieve the corresponding bill component using ID from POST form
        id = escape(request.form['id'])
        userbill = UserBill.query.filter_by(id=id).first()

        # Check if Bill component exists and belong to current user
        if userbill == None:
            data['error'] = "User Bill does not exist"
            return data
        elif userbill.user_id != current_user.id:
            data['error'] = "User Bill does not exist"
            return data
        
        # Retrieve user's party membership for party corresponding to the bill
        membership = userbill.user.parties.filter_by(party_id=userbill.bill.party_id).first()

        # Attempt to update database with error handling        
        try:
            # Update bill component status and paid time
            userbill.status = True
            userbill.paid_dt = datetime.now()
            data["paid_dt"] = userbill.paid_dt.strftime('%H:%M %d/%m/%y')

            # If user is admin, payment is auto-confirmed
            if userbill.bill.party.admin == False or membership.role == True:
                userbill.confirmed = True
                data["confirmed"] = True

                # Update portion of Total Party Bill paid and if fully paid, update status
                userbill.bill.paid = userbill.bill.paid + userbill.amount
                if userbill.bill.paid == userbill.bill.amount:
                    userbill.bill.status = True
            # If user is not admin, payment is not confirmed
            else: 
                userbill.confirmed = False

                # Retrieve admin in party and add notification for the payment confirmation request
                admin = userbill.bill.party.members.filter_by(role=1).first()
                if admin is not None:
                    notif_str = ("Request for Payment Confirmation for (Bill) " + userbill.bill.name 
                        + " in (Party) " + userbill.bill.party.name + " by (User) " + userbill.user.name.title())
                    notif = Notification(admin.user.id, notif_str, datetime.now())
                    db.session.add(notif)
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            data["error"] = "Error during sending request. Try again."

        # Return Dictionary (JSON) with any error message, the paid date & time and whether the payment was confirmed
        return data
    # Redirect to Overview if Request Method is incorrect
    else:
        return redirect(url_for('overview'))

#                           ADD BILL

# Route for New Bill Form page
@app.route('/addbill', defaults={'party_id': None})
@app.route('/addbill/<party_id>')
@login_required
def addbill(party_id):
    # If Party ID specified
    if party_id is not None:
        party_id = escape(party_id)
        # Retrieve corresponding party and check if user is member
        is_member = current_user.parties.filter_by(party_id=party_id)
        if is_member is not None:
            selected = Party.query.filter_by(id=party_id).first()
        else:
            selected = None
    else: 
        selected = None
    
    # Retrieve List of user's parties where user has admin permissions
    parties = list(PartyMember.query.filter_by(user_id=current_user.id, role=True))

    # Render page with the user's parties and the selected_option (None if not selected)
    return render_template('addbill.html', party=parties, selected_option=selected)


# Redirect route for Adding Bill (POST request from addbill page)
@app.route('/addbillredirect', methods=['GET','POST'])
@login_required
def addbillredirect():
    # Handle Correct POST request method
    if request.method == "POST":
        # Retrieve input from POST request's Form
        name = escape(request.form["name"])
        description = escape(request.form["description"])
        amount = float(escape(request.form["amount"]))
        party = request.form.get("party")
        if party is None:
            party = escape(request.form["party_id"])
        portions = request.form.getlist("uneven")
        due = request.form.getlist("tlimit")

        # Get all members in specified party
        party_users = list(Party.query.filter_by(id=party).first().members)
        user_amounts = []
        # Find average amount per member
        value = round(amount / len(party_users), 2)
        amount = value * len(party_users)

        # If portions specified, assign corresponding amout to each party member (otherwise use average amount)
        for member in party_users:
            if len(portions) == 1:
                value = float(request.form[str(member.user_id)])
            user_amounts.append([value, member.user_id])

        # Retrieve due datetime if one is specified

        due_date = escape(request.form["duedate"]) if len(due) == 1 else None
        due_time = escape(request.form["duetime"]) if len(due) == 1 else None
        duedate = datetime.strptime((due_date + "T" + due_time), "%Y-%m-%dT%H:%M") if due_date is not None and due_time is not None else None


        # Attempt to add bill and bill components to database
        try:
            # Add bill to database
            party_bill = Bill(name, description, party, datetime.now(), duedate, amount)
            db.session.add(party_bill)
            db.session.commit()
            db.session.refresh(party_bill)
            # Add bill components for each member (if they have a portion)
            for user in user_amounts:
                if user[0] != 0:
                    user_bill = UserBill(user[1], party_bill.id, user[0], None)
                    db.session.add(user_bill)
                    # Add notification to member for the creation of the new bill
                    notif_str = ("New Bill: " + name + " in (Party) " + party_bill.party.name + " of  £" + "{:.2f}".format(user[0])) 
                    notif = Notification(user[1], notif_str, datetime.now())
                    db.session.add(notif)
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            return redirect(url_for('billoverview'))
        
        return redirect(url_for('focusedpartybill', bill_id=party_bill.id))

    # Redirect to Bill Overview if request method is incorrect 
    else:
        return redirect(url_for('billoverview'))

#                           DELETE BILL

# Redirect route for Bill Deletion (POST request from focusedparty page)
@app.route('/deletebill', methods=['GET','POST'])
@login_required
def deletebillredirect():
    # Handle Correst POST request method
    if request.method == "POST":
        # Retrieve ID from POST form
        bill_id = escape(request.form["id"])

        # Retrieve Bill corresponding to ID from table
        matching_bill = Bill.query.filter_by(id=bill_id)
        bill = matching_bill.first()

        # Check if Bill exists and if User is admin in the Party in which the Bill exists
        if bill is None:
            return redirect(url_for("partyoverview"))
        else:
            if current_user.parties.filter(and_(PartyMember.role==True, PartyMember.party_id==bill.party_id)).first() is None:
                return redirect(url_for("partyoverview"))

        # Retrieve all User-Bill components belonging to Bill
        user_bills = UserBill.query.filter_by(bill_id=bill.id)
        party_id = bill.party_id
        
        # Attempt to delete Bill and components with error handling
        try:
            user_bills.delete()
            matching_bill.delete()
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            return redirect(url_for("partyoverview"))
        
        # Redirect back to Party if successful
        return redirect(url_for("focusedparty", party_id=str(party_id)))
    # Redirect to Party Overview if request methid is incorrect
    else: 
        return redirect(url_for("partyoverview"))

''' ----------------------------------------------------------------------------
                            PARTY MANAGEMENT
-----------------------------------------------------------------------------'''

#                           FRIEND REQUESTS

# Route for AJAX Friend Request Response 
@app.route('/friendreqresponse', methods=['GET', 'POST'])
@login_required
def ajaxfriendresponse():
    # Handle Correct POST method
    if request.method == "POST":
        # Initialise dictionary (JSON) to return
        data = {
            'error': "",
            'id': -1,
            'uid': -1,
            'name': "",
            'username': "",
            'added': False,
            'common': []
        }

        # Retrieve ID and action from POST form
        id = escape(request.form["id"])
        response = escape(request.form["action"])

        if response not in ["Accept", "Reject"]:
            data["error"] = "Invalid Data Posted. "
            return data

        # Retrieve corresponding Friend Request from database
        friend_requests = FriendRequest.query.filter_by(id=id)
        friend_request = friend_requests.first()

        # Check if Friend Request Exists and belongs to the User
        if friend_request is None:
            data["error"] = "Friend Request does not exist."
            return data
        elif current_user.id not in [friend_request.user_id2, friend_request.user_id1]:
            data["error"] = "Friend Request does not exist."
            return data
        
        # Attempt to update the database depending on the action with error handling
        try:
            # Retrieve User object for friend
            friend_id = friend_request.user_id1 if friend_request.user_id2 == current_user.id else friend_request.user_id2
            request_id = friend_request.id
            friend = User.query.filter_by(id=friend_id).first()

            # If request is accepted, add friend and delete friend request
            if response == "Accept":
                friend_rs = Friend(friend_request.user_id1, friend_request.user_id2)
                db.session.add(friend_rs)
                # Add notification for friend that friend request was accepted
                notif_str = ("Friend Request Accepted by " + current_user.name.title())
                notif = Notification(friend_id, notif_str, datetime.now())
                db.session.add(notif)
                friend_requests.delete()
            # If request is rejected, delete friend request
            else:
                friend_requests.delete()

            db.session.commit()
            # Assign required data to be returned in Dictionary
            data["id"] = request_id
            if response == "Accept":
                data["uid"] = friend_id
                data["name"] = friend.name
                data["username"] = friend.username
                data["added"] = True 
                # Retrieve common parties between user and friend
                common_parties = []
                for party in friend.parties:
                    if current_user.parties.filter_by(party_id=party.party_id).first() is not None:
                        common_parties.append(party.party.name)
                data["common"] = common_parties
        except IntegrityError as exc:
            db.session.rollback()
            data["error"] = "Error during sending request. Try again."
        
        # Return Dictionary (JSON) with any error message, the friend request id, friend's id, name, username, 
        # whether the friend was added and the common parties between the user and the friend
        return data
    # Redirect to Party Overview if Request Method is incorrect
    else:
        return redirect(url_for("partyoverview"))


# Route for AJAX Sending new Friend Request
@app.route("/friendrequest", methods=['GET', 'POST'])
@login_required
def friendrequestajax():
    # Handle Correct POST method
    if request.method == "POST":
        # Initialise dictionary (JSON) to return
        data = {
            'error': "",
            'id': -1,
            'uid': -1,
            'name': "",
            'username': "",
            'added': False,
            'common': []
        } # If added = false and no errors -> requested

        # Retrieve username from POST form
        username = escape(request.form['username'])

        # Check if username corresponds to current-user
        if username == current_user.username:
            data["error"] = "User can not add themselves as friends."
            return data

        # Retrieve user corresponding to username and check if user exists
        friend = User.query.filter_by(username=username).first()

        if friend is None:
            data["error"] = "User with username does not exist."
            return data

        # Check if user is already current user's friend
        already_friend = current_user.friends.filter(or_(Friend.user_id1==friend.id, Friend.user_id2==friend.id)).first()
        if already_friend is not None:
            data["error"] = "User is already added as friend."
            return data 
        
        # Check if current user has already sent request to user
        already_requested = current_user.friendrequests.filter_by(user_id2=friend.id).first()
        if already_requested is not None:
            data["error"] = "Request has already been sent to user."
            return data
        
        # Attempt to update database with error handling
        try: 
            incoming_requested = current_user.friendrequests.filter_by(user_id1=friend.id)
            # If user has already sent request to current user
            if incoming_requested.first() is not None:
                # Add new Friend and delete incoming friend request
                friend_rs = Friend(current_user.id, friend.id)
                db.session.add(friend_rs)
                data["id"] = incoming_requested.first().id
                # Add notification for user that friend request has beeb accepted
                notif_str = ("Friend Request Accepted by " + current_user.name.title())
                notif = Notification(friend.id, notif_str, datetime.now())
                db.session.add(notif)
                incoming_requested.delete()
                data["added"] = True
            # If user has not sent request to current user
            else:
                # Add new Friend request and add notification for user that there is a new friend request
                friend_request = FriendRequest(current_user.id, friend.id)
                db.session.add(friend_request)
                notif_str = ("New Friend Request from " + current_user.name.title())
                notif = Notification(friend.id, notif_str, datetime.now())
                db.session.add(notif)
                data["added"] = False
            db.session.commit()

            # Assign required data to be returned in Dictionary
            data["name"] = friend.name
            data["username"] = friend.username

            if not data["added"]:
                db.session.refresh(friend_request)
                data["id"] = friend_request.id
            else:
                data["uid"] = friend.id
                common_parties = []
                # Retrieve common parties between user and friend
                for party in friend.parties:
                    if current_user.parties.filter_by(party_id=party.party_id).first() is not None:
                        common_parties.append(party.party.name)
                data["common"] = common_parties

        except IntegrityError as exc:
            db.session.rollback()
            data["error"] = "Error during sending request. Try again."
        
        # Return Dictionary (JSON) with any error message, the friend request id, friend's id, name, username, 
        # whether the friend was added and the common parties between the user and the friend
        return data
    # Redirect to Party Overview if Request Method is incorrect
    else:
        return redirect(url_for("partyoverview"))

#                           REMOVE FRIEND

# Route for AJAX Deleting Friend
@app.route("/deletefriend", methods=['GET', 'POST'])
@login_required
def deletefriend():
    # Handle Correct POST method
    if request.method == "POST":
        # Initialise dictionary (JSON) to return
        data = {
            'error': ""
        }
        
        # Obtain ID from POST form and retrieve corresponding Friend
        id = escape(request.form['id'])
        friend = current_user.friends.filter(or_(Friend.user_id1==id, Friend.user_id2==id))
        
        # Check if friend exists
        if friend.first() is None:
            data['error'] = "User has no such friend."
            return data
        
        # Attempt to delete friend with error handling
        try:
            friend.delete()
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            data["error"] = "Error during sending request. Try again."

        # Return Dictionary (JSON) with any error message
        return data
    # Redirect to Party Overview if Request Method is incorrect
    else: 
        return redirect(url_for("partyoverview"))

#                           CREATE PARTY

# Route for New Party Form Page
@app.route('/addparty')
@login_required
def addparty():
    # Retrieve user's friends
    friends = current_user.friends
    users = []
    for friend in friends: 
        uid = friend.user_id1 if friend.user_id2 == current_user.id else friend.user_id2
        users.append(User.query.filter_by(id=uid).first())
    
    # Render page with the user's friends
    return render_template('addparty.html', friends=users)


# Redirect route for Adding Party (POST request from addparty page)
@app.route('/addpartyredirect', methods=['GET', 'POST'])
@login_required
def addpartyredirect():
    # Handle Correct POST request method
    if request.method == "POST":
        # Retrieve input from POST request's Form
        members = request.form.getlist("memberlist")
        name = escape(request.form["partyname"])
        party_type = escape(request.form["partytype"])

        # Check if specified party type is valid and if there is at least 1 member
        if party_type not in ["admin", "equal"] or len(members) == 0:
            return redirect(url_for("partyoverview"))

        party_type = True if party_type == "admin" else False

        # Check if selected members are user's friends and obtain their IDs
        all_members = []
        for member in members:
            safe_str = escape(member)
            is_friend = current_user.friends.filter(or_(Friend.user_id1==safe_str, Friend.user_id2==safe_str)).first()
            if is_friend is not None:
                if is_friend.user_id1 == current_user.id:
                    all_members.append(is_friend.user_id2)
                else:
                    all_members.append(is_friend.user_id1)
            else:
                return redirect(url_for("partyoverview"))

        # Attempt to create party and memberships with error handling
        try:
            # Add new Party to database
            party = Party(name, party_type)
            db.session.add(party)
            db.session.commit()
            db.session.refresh(party)
            # Add new admin Membership for current user
            party_member = PartyMember(party.id, current_user.id, True)
            db.session.add(party_member)
            # Add new memberships for all specified members
            for member in all_members:
                party_member = PartyMember(party.id, member, not party_type)
                db.session.add(party_member)
                # Add notification to corresponding member that they were added to a party
                notif_str = ("Added to New Party: " + party.name)
                notif = Notification(member, notif_str, datetime.now())
                db.session.add(notif)
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            return redirect(url_for("partyoverview"))

        return redirect(url_for('focusedparty', party_id=party.id))
    # Redirect to Party Overview if Request Method is incorrect
    else:
        return redirect(url_for("partyoverview"))

#                           ADD USER TO PARTY

# Route for AJAX Adding Friend to Party
@app.route('/adduserparty', methods=['GET', 'POST'])
@login_required
def adduserparty():
    # Handle Correst POST method
    if request.method == "POST":
        # Initialise dictionary (JSON) to return
        data = {
            'error': "",
            'name': "",
            'username': ""
        }

        # Retrieve party id and friend's user id from POST form and corresponding user and party objects from database
        uid = escape(request.form["user_id"])
        pid = escape(request.form["party_id"])
        user = User.query.filter_by(id=uid).first()
        party = current_user.parties.filter(and_(PartyMember.role==True, PartyMember.party_id==pid)).first()

        # Check if user exists
        if user is None:
            data['error'] = "No such User exists"
            return data

        # Check if party exists
        if party is None:
            data['error'] = "User has no such Party"
            return data
        
        role = False if party.party.admin else True

        # Attempt to add friend to party with error handling        
        try:
            # Add new party membership for friend
            membership = PartyMember(pid, uid, role)
            db.session.add(membership)
            # Add notification for friend that they were added to a party
            notif_str = ("Added to New Party: " + party.party.name)
            notif = Notification(uid, notif_str, datetime.now())
            db.session.add(notif)
            db.session.commit()
            data['name'] = user.name
            data['username'] = user.username
        except IntegrityError as exc:
            db.session.rollback()
            data['error'] = "Error during sending request. Try again."

        # Return Dictionary (JSON) with any error message, the friend's name and username
        return data
    # Redirect to Party Overview if Request Method is incorrect
    else: 
        return redirect(url_for("partyoverview"))

#                           VIEW PARTY

# Route for page for viewing a Party
@app.route('/focusedparty/<party_id>')
@login_required
def focusedparty(party_id):
    # Retrieve the specified Party and the user's parties
    party_id = escape(party_id)
    party_data = Party.query.filter_by(id=party_id).first()
    membership = current_user.parties.filter_by(party_id=party_id).first()
    msg = ""
    admin_users = []
    userfriends = []
    is_admin = None

    # Check if party does not exist or user has no parties
    if membership is None or party_data is None:
        msg = "User has no such party"
    else:
        # Retrieve Admin Members in Party 
        is_admin = membership.role
        for member in party_data.members:
            if member.role == True:
                admin_users.append(member)

        # Retrieve user's friends that are not already in the party
        friends = current_user.friends
        for friend in friends:
            uid = friend.user_id1 if friend.user_id2 == current_user.id else friend.user_id2
            user = User.query.filter_by(id=uid).first()
            # Check if friend is in the party
            already_member = user.parties.filter_by(party_id=party_id).first()
            if already_member is None:
                userfriends.append(user)

    # Render the page with the party data, admin users, whether the party is admin-based, the user's friend not already in the party and a possible error message
    return render_template('focusedparty.html', party=party_data, admin=admin_users, is_admin=is_admin, friends=userfriends, err=msg)

#                           VIEW PARTY BILL

# Route for the page viewing an overall Bill for a Party
@app.route('/focusedpartybill/<bill_id>')
@login_required
def focusedpartybill(bill_id):
    # Retrieve the corresponding Bill from database
    bill_id = escape(bill_id)
    bill = Bill.query.filter_by(id=bill_id).first()

    # Check If bill exists
    if bill is not None:
        # Check if user is in the party in which the bill is and has admin perms
        is_member = current_user.parties.filter_by(party_id=bill.party_id).first()
        if is_member is None:
            bill = None
        elif is_member.role == False:
            bill = None
    
    # Render the page with the bill data
    return render_template('focusedpartybill.html', partybill=bill)

#                           BILL CONFIRMATION

# Route for AJAX Bill Payment Confirmation Respose
@app.route("/billconfirm", methods=['GET', 'POST'])
@login_required
def billconfirmajax():
    # Handle Correst POST method
    if request.method == "POST":
        # Initialise dictionary (JSON) to return
        data = {
            'error': "",
            'billpaid': False,
            'billamount': -1
        }

        # Retrieve action and id from POST form and retrieve corresponding bill component
        response = escape(request.form['action'])
        userbill_id = escape(request.form['id'])
        userbill = UserBill.query.filter_by(id=userbill_id).first()

        # Check if action is valid
        if response not in ["Accept", "Deny"]:
            data["error"] = "Invalid Form Data Posted"
            return data

        # Check if bill exists
        if userbill is None:
            data["error"] = "User Bill does not exist"
            return data
        # Check if current user is a member of the party in which the bill exists
        else:
            is_member = current_user.parties.filter_by(party_id=userbill.bill.party_id).first()
            if is_member is None:
                data["error"] = "User Bill does not exist"
                return data

        # Attempt to update database with error handling
        try:
            # If payment accepted update the bill component and bill
            if response == "Accept":
                userbill.confirmed = True
                # Update portion of overall bill paid and check if it is fully paid
                userbill.bill.paid = userbill.bill.paid + userbill.amount
                data['billamount'] = userbill.bill.paid
                if userbill.bill.paid == userbill.bill.amount: 
                    userbill.bill.status = True
                    data['billpaid'] = True
                # Add notification to the user of the bill-component that the payment was accepted
                notif_str = ("Payment Accepted for (Bill) " + userbill.bill.name + " in (Party) " + userbill.bill.party.name)
                notif = Notification(userbill.user.id, notif_str, datetime.now())
                db.session.add(notif)
            # If payment rejected update the bill component
            else:
                userbill.status = False
                # Add notification to the user of the bill-component that the payment was rejected
                notif_str = ("Payment Rejected for (Bill) " + userbill.bill.name + " in (Party) " + userbill.bill.party.name)
                notif = Notification(userbill.user.id, notif_str, datetime.now())
                db.session.add(notif)
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            data["error"] = "Error during sending request. Try again."
        
        # Return Dictionary (JSON) with any error message, whether the overall bill was paid 
        # and what the resulting paid portion of the overall bill is
        return data
    # Redirect to Party Overview if Request Method is incorrect
    else:
        return redirect(url_for("partyoverview"))


''' ----------------------------------------------------------------------------
                            MISC FUNCTION
-----------------------------------------------------------------------------'''

# Route for AJAX retrieval of Members of Party
@app.route('/getjsonmembers/<id>', methods=['GET', 'POST'])
@login_required
def getjsonmembers(id):
    # Handle Correst POST method
    if request.method == "POST":
        # Initialise dictionary (JSON) to return
        data = {
            'error': "",
            'ids': [],
            'names': []
        }

        # Check if user is member of specified party
        if current_user.parties.filter_by(party_id=id).first() is None:
            data['error'] = "User has no such party"
            return data

        # Retrieve members of party and obtain their IDs and names
        members = Party.query.filter_by(id=id).first().members
        member_ids = []
        member_names = []

        for member in members:
            member_ids.append(member.user.id)
            member_names.append(member.user.name.title())

        data['ids'] = member_ids
        data['names'] = member_names

        # Return Dictionary (JSON) with any error message, array of IDs of party members
        # and array of names of party members 
        return data
    # Redirect to Bill Overview if Request Method is incorrect   
    else:
        return redirect(url_for("billoverview"))


# Route for AJAX retrieval of Notifications
@app.route('/getnotifs')
@login_required
def getnotifs():
    # Initialise dictionary (JSON) to return
    data = {
        'notifs': []
    }

    # Retrieve user's ntoification content
    notifications = current_user.notifications
    notif_content = []
    for notif in notifications:
        notif_content.append(notif.content)
    data['notifs'] = notif_content

    # Attempt to delete the notifications with error handling
    try: 
        notifications.delete()
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()

    # Return Dictionary (JSON) with array of notification strings
    return data


# Route for AJAX Updating New Bills once seen by User
@app.route('/updateseenbills')
@login_required
def updateseenbills():
    # Retrieve user's new bills
    bill_data = current_user.bills.filter_by(seen=False)

    # Attempt to update bills to seen with error handling
    try: 
        for bill in bill_data:
            if not bill.seen:
                bill.seen = True
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()

    return ""

# Route for AJAX retrieval of Search Results
@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    # Initialise Dictionary (JSON) to return
    data = {
        'bills': [],
        'parties': []
    }

    # Retrieve user's bills that contain the search key
    search_term = escape(request.form['search_key']).lower()
    bills = current_user.bills.join(UserBill.bill).filter(or_(Bill.name.contains(search_term), Bill.description.contains(search_term)))
    bill_data = []

    # Add Bill data to Dictionary for each Bill
    for bill in bills: 
        dueString = "None" if bill.bill.end == None else bill.bill.end.strftime('%H:%M %d/%m/%y')
        paidString = "None" if bill.paid_dt == None else bill.paid_dt.strftime('%H:%M %d/%m/%y')
        # Construct Dictionary (JSON) for current bill
        temp = {
            'id': bill.id,
            'name': bill.bill.name,
            'party': bill.bill.party.name,
            'description': bill.bill.description,
            'amount': "{:.2f}".format(bill.amount),
            'status': bill.status,
            'confirmed': bill.confirmed,
            'set': bill.bill.start.strftime('%H:%M %d/%m/%y'),
            'due': dueString,
            'paid_dt': paidString
        }
        bill_data.append(temp)
    data['bills'] = bill_data

    # Retrieve user's parties that contain the search key
    parties = current_user.parties.join(PartyMember.party).filter(Party.name.contains(search_term))
    party_data = []

    # Add Party data to Dictionary for each Party
    for party in parties:
        # Construct Dictionary (JSON) for current party
        temp = {
            'name': party.party.name,
            'id': party.party.id
        }
        party_data.append(temp)
    data['parties'] = party_data
    
    # Return Dictionary (JSON) with array of bill dictionaries and party dictionaries that contain the search string
    return data

