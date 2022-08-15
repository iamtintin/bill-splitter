# Overall User Experience

## <ins> **Fundamental Idea** </ins>
The Bill Splitter works on the idea that there are users can form groups called parties, to which a bill can then be assigned. In order to form a party, the user creating the party, must be friends with all the proposed members of the party. A friend is created by a user sending a friend request to another user, who then accepts the request. 

There are 2 types of Parties: 
- Admin - where only the creator of the Party has Admin Permissions
- Equal - where all the members of the Party have Admin Permissions 
  
Admin permissions allow a user to add a new bill, pay bills with further confirmation, delete bills, view all party bills, add further member to the party and confirm non-admin users' bill payments when required. 

When creating a bill for a party, the required data is the name of the bill and the amount. Optional data includes:
 - A brief description of the bill
 - A due date and time 
 - Uneven Portions for each member (where the amount for each user is specified)

When a bill is created the party bill refers to the overall bill created for the entire party and each member receives a bill-component. 

## <ins> **Main Features** </ins>

### **Registering and Authentication**

In order to register, a user must provide a valid name, username, email and password. These will initially be checked for validity by JavaScript and then checked for validity by database itself to ensure any fields that must be unique across the users, is indeed unique (i.e.: username and email). The password is hashed with a salt string and the hash is stored in the database for security. 

In order to login, a user must provide their email and corresponding password. These will again follow the same checking as registering. The password is checked by comparing its hash to that stored in the database. 

Any errors during logging in or registering are displayed to the user through an error box that appears. 

### **Adding a Bill and Splitting the Bill**

When adding a bill, a user must specify the name of the bill and the total amount for its quantity. By default, the bill will be split equally between all members in the selected party. If the average amount is not to 2 decimal places, it is rounded, and the total amount is slightly decreased to account for this. Optional fields include the due date and time for the bill as well as irregular distribution of the bill.

### **Settling Payments**

Payments can be settled by opening a bill and confirming the payment. Depending on the permissions of the user in the corresponding party, this payment may need to be confirmed by an admin of the party. 

### **Displaying Status of Bills**

The bills are displayed both in the main overview page and in more detail in the bills overview page. The bills overview page comprises of 3 lists of bills. Each list element has a summary of the bill it corresponds to (i.e.: bill name, bill description, party name, created date, due date, amount, status - paid? and confirmed?). The first list is a list of unpaid bills, which also displays the total amount of unpaid bills at the top of the list. The second list is a list of bill payment confirmations requested by non-admin users in parties where the user is an admin. The last list is a list of paid bills, comprising of bills that are pending confirmation and have been confirmed. It also displays the total amount of paid bills at the top of the list. 

### **Notification of New Bill and Monies Owed**

When a user arrives at the main overview page, any new bills that have been created will be at the top of the bill list with a red **NEW** marker alongside to signify that it is a new bill unseen by the user. Just like all the other elements, a summary of the bill can be seen in the list element. This includes the bill name, description, party name, due date, amount and status. For new bills, a notification string is also added to the notification tab, which specifies the bill name, party name and amount.

### **Security**

In order to ensure security of the user accounts, only the hashed passwords are stored in the database, which are created using the entered string and a salt string. A password is authenticating by calculating the hash and comparing the calculated hash to that stored in the database. All routes within the site (apart from the Error Handler, Register and Login pages) require a user to be logged in. In all the relevant routes, where data is retrieved, checks are made to ensure that the currently logged in user should have access to that information (e.g.: attempting to access a different party's bills). 

The website (the server) itself kept secure by escaping all input that is provided to it before further processing, in order to prevent Cross-Scripting attacks. SQLAlchemy automatically parameterises the SQL statements executed. The constant checks for whether a user should have access to the method in the relevant routes, also help prevent possible malicious attacks. 

### **Usability and Accessibility**

After logging in, all the pages within the website having a header with a navigation bar at the top of the page. This is for ease of navigation throughout the site. The navigation bar includes links for: 
 - The Main Overview Page
 - The Bills Overview Page
 - The Friends and Parties Overview Page
 - Signing Out

Each page has appropriate buttons and links to move around to different pages with ease. For example, each bill in the flex panel list is clickable to open up the focused bill-component page view of the bill for that user. 

The usability and accessibility to disabled users is considered in the design of the website by ensuring that appropriate semantic tags are used in the HTML to ensure that the site it well supported by screen-readers. The site is also structured such that, the relevant buttons and forms can be accessed using just a keyboard rather than a mouse. High contrast buttons are frequently throughout the site to ensure that they are clearly visible, even to users whose vision may be partially impaired. All the input fields and buttons have appropriate labels and text fields so that their purpose is clear, and a screen-reader would be able to understand what the form does. 

## <ins> **Additional Features** </ins>

### **Groups of Users - Parties and Friends**

As mentioned previously, users can create groups called parties, and in order to do so the creator of the party must be friends with all the proposed members of the party. A friend is made is when a user sends out a friend request to another user, using their username and the 2nd user accepts the requests. This is to ensure, that any user can not just add any user if they know their username. 

There are 2 types of Parties: 
- Admin - where only the creator of the Party has Admin Permissions
- Equal - where all the members of the Party have Admin Permissions 

### **Permissions in Parties and Bill Confirmations**
  
Admin permissions allow a user to:
- Add new bills
- Pay bills without further confirmation
- Delete bills
- View party bills
- Add further members to the party
- Confirm bill payments of non-admin users when required. 

### **Uneven Splitting of Bills**

A bill can be irregularly distributed across the members of a party (even removing some users from the bill) by selecting the uneven portions option in the new bill form. This allows the user to specify the amount each member should have to pay. If a member is given an amount of £0, no bill is created for them, and they are not included in the bill. 

### **Searching through Bills and Parties**

The Main Overview page contains a search field which can be used to search through all the user's bills and parties using the bill name, description and party name attributes. When the search field is not empty, the main overview content is removed and replaced by the search results (and vice versa). 

### **Responsive Design - AJAX, jQuery, CSS**

Most the pages on the site use flex panels to allow for more responsive design. The wrap feature of the flex panel ensure that the content wont overflow of the screen but wrap around to the next row/column. Media queries combined with jQuery to check for overflow on elements is also used to ensure that elements are appropriately sized on most screens and works even with smaller screen sizes up to a limit. The CSS design furthers this by staying away from absolute values wherever possible. 

In order to make the website feel more responsive and smoother, AJAX is used to make requests to the server and update the page without having to refresh the page. This is used in all the forms except the new bill and new party forms where a redirect is necessary. After a response is received from the server, jQuery is used to update the page according to the data, whether that is displaying an error message or adding an element to a flex panel. 

### **General Notifications**

The Main Overview page contains a notification panel which includes a list of the notifications that have not been seen by the user. This includes a brief summary of operations that have occurred since the user last logged in, including events such as:
- Friend Requests Accepted
- Incoming Friend Requests
- New Party Creation
- New Bill Creation
- Bill Payment Confirmation Request
- Bill Payment Confirmation / Rejection

When a user has new notifications, upon arrival to the Main Overview page, the notification panel will pulse and there will be a number indicator of the number of notifications. 

### **Error Messages**

If the user attempts to go to a route that is not defined an appropriate 404 Error Page will be returned. This includes a button to return to either the Main Overview page if the user is logged in, or otherwise, the login page. 

Inputs forms are validated initially by the client using JavaScript to ensure input is of the correct form, and then by the server to ensure the input is correct in terms of what is required by the database. Any errors returned during this validation is appropriately mapped to an error string which is displayed to the user using a suitably-styled red error box that appears when an error is found and disappears when the input is valid. This error box is also used to display an error message when a user attempts to accept bill or party that does not belong to them or does not exist. Some of the forms where this feature can be seen include the:
- Registration Form
- Login Authentication Form
- Create New Bill Form
- Create New Party Form
- Add Friend Form