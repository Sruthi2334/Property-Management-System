from flask import Flask,render_template,request,redirect,url_for,session,send_file
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import os
from MySQLdb.cursors import DictCursor
import requests 
from flask import send_from_directory

app=Flask('__name__')
app.secret_key='your_super_secret_key_2004'
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='projectmanagement'

mysql=MySQL(app)
app.config['UPLOAD_FOLDER']='/Users/sruthi/Desktop/Everything/Project/static/loan_documents'
app.config['UPLOAD_FOLDER_1']='/Users/sruthi/Desktop/Everything/Project/static/maintenance_request'
app.config['UPLOAD_FOLDER_2']='/Users/sruthi/Desktop/Everything/Project/static/apartments'
app.config['UPLOAD_FOLDER_3']='/Users/sruthi/Desktop/Everything/Project/static/individualhouse'
app.config['UPLOAD_FOLDER_4']='/Users/sruthi/Desktop/Everything/Project/static/lands'
app.config['UPLOAD_FOLDER_5']='/Users/sruthi/Desktop/Everything/Project/static/villas'
app.config['UPLOAD_FOLDER_6']='/Users/sruthi/Desktop/Everything/Project/static/admin_apart'
app.config['UPLOAD_FOLDER_7']='/Users/sruthi/Desktop/Everything/Project/static/admin_ind'
app.config['UPLOAD_FOLDER_8']='/Users/sruthi/Desktop/Everything/Project/static/admin_land'
app.config['UPLOAD_FOLDER_9']='/Users/sruthi/Desktop/Everything/Project/static/admin_villa'
UPLOAD_FOLDER='/Users/sruthi/Desktop/Everything/Project/static/downloadimages'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def main():
    if 'email' in session:
        return render_template('main.html',email=session['email'])
    else:
        return render_template('main.html')


@app.route('/login.html',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email=request.form['email'].strip() 
        pwd=request.form['password']
        role=request.form['role'].strip().lower()
        cur=mysql.connection.cursor()
        cur.execute("select email,password,role from register where email=%s", (email,))  
        user=cur.fetchone()
        cur.close()
        if user:
            if pwd== user[1] and role==user[2].strip().lower():
                session['email']=user[0]
                session['role']=user[2]
                return redirect(url_for('main'))
            else: 
                return render_template('login.html',error='invalid email or password or role')
        else:
            return render_template('login.html',error='Invalid email or password')    
    return render_template('login.html')

@app.route('/register.html',methods=['GET','POST'])
def register():
    if request.method =='POST':
        name=request.form['name']
        email=request.form['email']
        phone=request.form['phone']
        role=request.form['role']
        pwd=request.form['password']
        cur=mysql.connection.cursor()
        cur.execute("insert into register (name,email,phone,role,password) values (%s,%s,%s,%s,%s)",(name,email,phone,role,pwd))
        mysql.connection.commit()
        cur.close()
        
        return  redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('email',None)
    return redirect(url_for('main'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/properties')
def properties():
    return render_template('properties.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/agent')
def agent():
    return render_template('agent.html')

@app.route('/submit_option')
def submit_option():
    return render_template('submit_option.html')

@app.route('/admin_view_option')
def admin_view_option():
    return render_template('admin_view_option.html')

@app.route('/admin_add_option')
def admin_add_option():
    return render_template('admin_add_option.html')


@app.route('/apartment', methods=['GET', 'POST'])
def apartment():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        
        # Personal Information
        name = request.form['name']
        phone = request.form['phone']
        email=request.form['email']
        loans = request.form['outstandingloan']
        price = request.form['price']
        landmark = request.form['landmark']
        nearby_facility = request.form['nearbyfacility']
        address = request.form['address']
        pincode = request.form['pincode']

        # Loan Details (if applicable)
        loan_document = request.files['loanDocument']
        loan_document_filename = None
        amnt, balance, lender_name, next_repayment = None, None, None, None
        
        if loan_document:
            filename = secure_filename(loan_document.filename)
            loan_document_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            loan_document.save(loan_document_path) 
            loan_document_filename = filename
            if loans == 'yes':
                amnt = request.form['loanAmount']
                balance = request.form['loanBalance']
                lender_name = request.form['lenderName']
                next_repayment = request.form['nextRepayment']

        # Apartment Details
        sq_feet = request.form['sqFeet']
        floor_no = request.form['floorNo']
        tot_floors = request.form['totalfloors']
        bhk_number = request.form['bhknumber']
        kit_detail = request.form['kitchendetail']
        direction = request.form['direction']
        amenities = request.form['amenties']
        status = request.form['status']
        img = request.files['propertyimage']
        img_filename = None

        # Handle property image upload
        if img:
            img_filename = secure_filename(img.filename)
            img_path = os.path.join(app.config['UPLOAD_FOLDER_2'], img_filename)
            img.save(img_path)
        
        # Insert into Apartments table
        cur.execute(
            """
            INSERT INTO Apartments 
            (Name, Phone,Email, OutstandingLoan, LoanAmount, LoanBalance, LenderName, NextRepayment, LoanDocument, 
            SqFeet, FloorNo, TotalFloors, BHKNumber, KitchenDetail, Direction, Amenities, Status, Image, Price, 
            Landmark, NearbyFacility, Address, Pincode)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
            """,
            (name, phone,email, loans, amnt, balance, lender_name, next_repayment, loan_document_filename,
             sq_feet, floor_no, tot_floors, bhk_number, kit_detail, direction, amenities, status, img_filename,
             price, landmark, nearby_facility, address, pincode)
        )

        mysql.connection.commit()
        cur.close()

        return redirect(url_for('main'))
    
    return render_template('apartment.html')


@app.route('/apartment_add', methods=['GET', 'POST'])
def apartment_add():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        
        # Collecting form data
        phone = request.form['phone']
        email = request.form['email']
        sq_feet = request.form['sqFeet']
        floor_no = request.form['floorNo']
        tot_floors = request.form['totalfloors']
        bhk_number = request.form['bhknumber']
        kit_detail = request.form['kitchendetail']
        direction = request.form['direction'] 
        amenities = request.form['amenties']
        price = request.form['price']
        landmark = request.form['landmark']
        nearby_facility = request.form['nearbyfacility']
        address = request.form['address']
        pincode = request.form['pincode']
        img = request.files['propertyimage']
        img_filename = None

        # Handle property image upload
        if img:
            img_filename = secure_filename(img.filename)
            img_path = os.path.join(app.config['UPLOAD_FOLDER_6'], img_filename)
            img.save(img_path)
        
        # Insert into Apartments table
        cur.execute(
            """
            INSERT INTO ApartmentsAdd
            (Phone, Email, SqFeet, FloorNo, TotalFloors, BHKNumber, KitchenDetail, Direction, Amenities, Image, 
            Price, Landmark, NearbyFacility, Address, Pincode)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (phone, email, sq_feet, floor_no, tot_floors, bhk_number, kit_detail, direction, amenities, img_filename,
             price, landmark, nearby_facility, address, pincode)
        )

        mysql.connection.commit()
        cur.execute("SELECT LAST_INSERT_ID()")
        last_id = cur.fetchone()[0]
        cur.close()

        # Redirect to view the added apartment
        return redirect(url_for('apartment_view', id=last_id))
    
    return render_template('apartment_add.html')


@app.route('/individualhouse', methods=['GET', 'POST'])
def individualhouse():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        
        # Personal Information
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        price = request.form['price']
        landmark = request.form['landmark']
        nearby_facility = request.form['nearbyfacility']
        address = request.form['address']
        pincode = request.form['pincode']

        # Loan Details (if applicable)
        outstanding_loan = request.form['outstandingloan']
        loan_document = request.files['loanDocument']
        loan_document_filename = None
        loan_amount, loan_balance, lender_name, next_repayment = None, None, None, None
        
        if loan_document:
            filename = secure_filename(loan_document.filename)
            loan_document_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            loan_document.save(loan_document_path)
            loan_document_filename = filename
            if outstanding_loan == 'yes':
                loan_amount = request.form['loanAmount']
                loan_balance = request.form['loanBalance']
                lender_name = request.form['lenderName']
                next_repayment = request.form['nextRepayment']

        # House Details
        rooms = request.form['houseRooms']
        area = request.form['houseArea']
        kitchen_type = request.form['kitchenType']
        storage_spaces = request.form['storageSpaces']
        status = request.form['status']
        property_image = request.files['propertyImage']
        property_image_filename = None

        # Handle property image upload
        if property_image:
            property_image_filename = secure_filename(property_image.filename)
            property_image_path = os.path.join(app.config['UPLOAD_FOLDER_7'], property_image_filename)
            property_image.save(property_image_path)
        
        # Insert into IndividualHouse table
        cur.execute(
            """
            INSERT INTO IndividualHouse 
            (Name, Email, Phone, Price, Landmark, NearbyFacility, Address, Pincode, 
             OutstandingLoan, LoanAmount, LoanBalance, LenderName, NextRepayment, 
             Rooms, Area, KitchenType, StorageSpaces, Status, Image, LoanDocument)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (name, email, phone, price, landmark, nearby_facility, address, pincode, 
             outstanding_loan, loan_amount, loan_balance, lender_name, next_repayment, 
             rooms, area, kitchen_type, storage_spaces, status, property_image_filename, 
             loan_document_filename)
        )

        mysql.connection.commit()
        cur.close()

        return redirect(url_for('main'))
    
    return render_template('individualhouse.html')

@app.route('/individualhouse_add', methods=['GET', 'POST'])
def individualhouse_add():
    if request.method == 'POST':
        cur = mysql.connection.cursor()

        # Collect data from form
        email = request.form['email']
        phone = request.form['phone']
        price = request.form['price']
        landmark = request.form['landmark']
        nearby_facility = request.form['nearbyfacility']
        address = request.form['address']
        pincode = request.form['pincode']
        rooms = request.form['houseRooms']
        area = request.form['houseArea']
        kitchen_type = request.form['kitchenType']
        storage_spaces = request.form['storageSpaces']
        status = request.form['status']
        property_image = request.files['propertyImage']
        property_image_filename = None

        # Handle property image upload
        if property_image:
            property_image_filename = secure_filename(property_image.filename)
            property_image_path = os.path.join(app.config['UPLOAD_FOLDER_3'], property_image_filename)
            property_image.save(property_image_path)

        # Insert into IndividualHouse table
        cur.execute(
            """
            INSERT INTO IndividualHouseAdd
            (Email, Phone, Price, Landmark, NearbyFacility, Address, Pincode, Rooms, Area, 
             KitchenType, StorageSpaces, Status, Image)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (email, phone, price, landmark, nearby_facility, address, pincode, rooms, area, 
             kitchen_type, storage_spaces, status, property_image_filename)
        )

        mysql.connection.commit() 
        cur.close()

        return redirect(url_for('main'))

    return render_template('individualhouse_add.html')



@app.route('/land', methods=['GET', 'POST'])
def land():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        
        # Personal Information
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        loans = request.form['outstandingloan']
        price = request.form['price']
        landmark = request.form['landmark']
        nearby_facility = request.form['nearbyfacility']  
        address = request.form['address']
        pincode = request.form['pincode']

        # Loan Details (if applicable)
        loan_document = request.files['loanDocument']
        loan_document_filename = None
        amnt, balance, lender_name, next_repayment = None, None, None, None
        
        if loan_document:
            filename = secure_filename(loan_document.filename)
            loan_document_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            loan_document.save(loan_document_path)
            loan_document_filename = filename
            if loans == 'yes':
                amnt = request.form['loanAmount']
                balance = request.form['loanBalance']
                lender_name = request.form['lenderName']
                next_repayment = request.form['nextRepayment']

        # Land Details
        area = request.form['area']
        land_type = request.form['landType']
        boundary_details = request.form['boundaryDetails']
        status = request.form['status']
        img = request.files['propertyimage']
        img_filename = None
        patta_image = request.files['pattaImage']
        patta_image_filename = None

        # Handle property image upload
        if img:
            img_filename = secure_filename(img.filename)
            img_path = os.path.join(app.config['UPLOAD_FOLDER_4'], img_filename)
            img.save(img_path)
        
        # Handle patta image upload
        if patta_image:
            patta_image_filename = secure_filename(patta_image.filename)
            patta_image_path = os.path.join(app.config['UPLOAD_FOLDER_3'], patta_image_filename)
            patta_image.save(patta_image_path)

        # Insert into Lands table
        cur.execute(
            """
            INSERT INTO Lands 
            (Name, Phone, Email, OutstandingLoan, LoanAmount, LoanBalance, LenderName, NextRepayment, LoanDocument, 
            Area, LandType, BoundaryDetails, Status, PropertyImage, PattaImage, Price, Landmark, NearbyFacility, Address, Pincode)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
            """,
            (name, phone, email, loans, amnt, balance, lender_name, next_repayment, loan_document_filename,
             area, land_type, boundary_details, status, img_filename, 
             patta_image_filename, price, landmark, nearby_facility, address, pincode)
        )

        mysql.connection.commit()
        cur.close()

        return redirect(url_for('main'))
    
    return render_template('land.html')

@app.route('/land_add', methods=['GET', 'POST'])
def land_add():
    if request.method == 'POST':
        cur = mysql.connection.cursor()

        # Get form data
        phone = request.form['phone']
        email = request.form['email']
        area = request.form['area']
        land_type = request.form['landType']
        boundary_details = request.form['boundaryDetails']
        status = request.form['status']
        property_image = request.files['propertyImage']
        patta_image = request.files['pattaImage']
        price = request.form['price']
        landmark = request.form['landmark']
        nearby_facility = request.form['nearbyFacility']
        address = request.form['address']
        pincode = request.form['pincode']

        # Save property image
        property_image_filename = secure_filename(property_image.filename)
        property_image_path = os.path.join(app.config['UPLOAD_FOLDER_8'], property_image_filename)
        property_image.save(property_image_path)

        # Save patta image
        patta_image_filename = secure_filename(patta_image.filename)
        patta_image_path = os.path.join(app.config['UPLOAD_FOLDER_8'], patta_image_filename)
        patta_image.save(patta_image_path)

        # Insert into Lands table
        cur.execute(
            """
            INSERT INTO LandsAdd
            (Phone, Email, Area, LandType, BoundaryDetails, Status, PropertyImage, PattaImage, Price, Landmark, NearbyFacility, Address, Pincode)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (phone, email, area, land_type, boundary_details, status, property_image_filename, 
             patta_image_filename, price, landmark, nearby_facility, address, pincode)
        )

        mysql.connection.commit()
        cur.close()

        return redirect(url_for('main'))

    return render_template('land_add.html')



@app.route('/villa', methods=['GET', 'POST'])
def villa():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        
        # Personal Information
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        loans = request.form['outstandingloan']
        price = request.form['price']
        landmark = request.form['landmark']
        nearby_facility = request.form['nearbyfacility']
        address = request.form['address']
        pincode = request.form['pincode']

        # Loan Details (if applicable)
        loan_document = request.files['loanDocument']
        loan_document_filename = None
        amnt, balance, lender_name, next_repayment = None, None, None, None
        
        if loan_document:
            filename = secure_filename(loan_document.filename)
            loan_document_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            loan_document.save(loan_document_path)
            loan_document_filename = filename
            if loans == 'yes':
                amnt = request.form['loanAmount']
                balance = request.form['loanBalance']
                lender_name = request.form['lenderName']
                next_repayment = request.form['nextRepayment']

        # Villa Details
        sq_feet = request.form['sqFeet']
        floor_no = request.form['floorNo']
        total_floors = request.form['totalfloors']
        bhk_number = request.form['bhknumber']
        pool = request.form.get('pool', 'no')  # Check if pool is included
        garden = request.form.get('garden', 'no')  # Check if garden is included 
        amenities = request.form['amenties']
        img = request.files['propertyimage']
        img_filename = None

        # Handle property image upload
        if img:
            img_filename = secure_filename(img.filename)
            img_path = os.path.join(app.config['UPLOAD_FOLDER_5'], img_filename)
            img.save(img_path)
        
        # Insert into Villas table
        cur.execute(
            """
            INSERT INTO Villas 
            (Name, Phone, Email, OutstandingLoan, LoanAmount, LoanBalance, LenderName, NextRepayment, LoanDocument, 
            SqFeet, FloorNo, TotalFloors, BHKNumber, Pool, Garden, Amenities, Status, Image, Price, 
            Landmark, NearbyFacility, Address, Pincode)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (name, phone, email, loans, amnt, balance, lender_name, next_repayment, loan_document_filename,
             sq_feet, floor_no, total_floors, bhk_number, pool, garden, amenities, 'available', img_filename,
             price, landmark, nearby_facility, address, pincode)
        )

        mysql.connection.commit()
        cur.close()

        return redirect(url_for('main'))
    
    return render_template('villa.html')


@app.route('/villa_add', methods=['GET', 'POST'])
def villa_add():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        email = request.form['email']
        phone = request.form['phone']
        price = request.form['price']
        landmark = request.form['landmark']
        nearby_facility = request.form['nearbyfacility']
        address = request.form['address']
        swimming_pool = request.form['swimmingpool']
        parking = request.form['parking']
        garden = request.form['garden']
        bhk_number = request.form['bhknumber']
        sq_feet = request.form['sqfeet']
        status = request.form['status']
        total_floors = request.form['totalfloors']
        floor_no = request.form['floorno']
        amenities = request.form['amenities']
        img = request.files['propertyimage']
        img_filename = None
        if img:
            img_filename = secure_filename(img.filename)
            img_path = os.path.join(app.config['UPLOAD_FOLDER'], img_filename)
            img.save(img_path)
        else:
            img_path = None
        cur.execute(
            """
            INSERT INTO VillasAdd 
            (Email, Phone, Price, Landmark, NearbyFacility, Address, SwimmingPool, Parking, Garden, 
            BHKNumber, SqFeet, Status, Image, TotalFloors, FloorNo, Amenities)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (email, phone, price, landmark, nearby_facility, address, swimming_pool, parking, garden, 
             bhk_number, sq_feet, status, img_filename, total_floors, floor_no, amenities)
        )
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('main'))  
    return render_template('villa_add.html')

@app.route('/maintenance_request.html', methods=['GET', 'POST'])
def maintenance_request():
    if 'email' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        type=request.form['propertyType']
        date=request.form['submissionDate']
        property_address = request.form['propertyAddress']
        time=request.form['preferredTime']
        issue_description = request.form['issueDescription']
        otherIssueText=request.form['otherIssueText']
        priority = request.form['priority']
        contact_info = request.form['contactInfo']
        img=request.files['issueImage']
        
        # Insert data into MaintenanceRequests table
        if img and img.filename != '':
            # Secure the filename
            filename = secure_filename(img.filename)
            # Save the file in the UPLOAD_FOLDER
            img.save(os.path.join(app.config['UPLOAD_FOLDER_1'], filename))
            # Store the image path to insert into the database
            img_path = os.path.join(app.config['UPLOAD_FOLDER_1'], filename)
        else:
            img_path = None
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO maintenancerequests (name, phone, email, property_type,request_date,property_address,preferred_time, issue_description,otherIssueText,priority, contactInfo,image) VALUES (%s, %s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s)", 
                    (name, phone, email,type,date, property_address,time, issue_description,otherIssueText,priority, contact_info,filename))
        mysql.connection.commit()
        cur.close()

        # Redirect to the main page after submission
        return redirect(url_for('main'))
    
    # If GET request, show the form
    return render_template('maintenance_request.html')


@app.route('/termsandcondition')
def termsandcondition():
    return render_template('termsandcondition.html')

@app.route('/admin_dash')
def admin_dash():
    return render_template('admin_dash.html')

@app.route('/property_list')
def property_list():
    return render_template('property_list.html')

@app.route('/users_list')
def users_list():
    return render_template('users_list.html')

@app.route('/buyers')
def buyers():
    cur = mysql.connection.cursor()
    # Select only users with the role 'Buyer'
    cur.execute("SELECT * FROM register WHERE role = 'Buyer'")
    buyers = cur.fetchall()
    cur.close()
    
    # Render the results in the buyers.html template
    return render_template('buyers.html', buyers=buyers)

@app.route('/sellers')
def sellers():
    cur = mysql.connection.cursor()
    # Select only users with the role 'Seller'
    cur.execute("SELECT * FROM register WHERE role = 'Seller'")
    sellers = cur.fetchall()
    cur.close()
    
    # Render the results in the sellers.html template
    return render_template('sellers.html', sellers=sellers)

@app.route('/agents')
def agents():
    cur = mysql.connection.cursor()
    # Select only users with the role 'Agent'
    cur.execute("SELECT * FROM register WHERE role = 'Agent'")
    agents = cur.fetchall()
    cur.close()
    
    # Render the results in the sellers.html template
    return render_template('agents.html', agents=agents)

@app.route('/maintreq_list')
def maintreq_list():
    cur = mysql.connection.cursor(DictCursor)
    # Fetch all maintenance requests
    cur.execute("SELECT * FROM maintenancerequests")
    maintreq_list = cur.fetchall()  
    cur.close()
    # Render the results in the maintreq_list.html template
    return render_template('maintreq_list.html', maintreq_list=maintreq_list)

# app.py

@app.route('/apartment_list', methods=['GET'])
def apartment_list():
    cur = mysql.connection.cursor(DictCursor)
    # Fetch all records from the Apartments table
    cur.execute("SELECT * FROM Apartments")
    apartments = cur.fetchall()
    cur.close()
    # Render template with apartments data
    return render_template('apartment_list.html', apartments=apartments)

@app.route('/individualhouse_list', methods=['GET'])
def individualhouse_list():
    cur = mysql.connection.cursor(DictCursor)
    # Fetch all records from the Houses table
    cur.execute("SELECT * FROM IndividualHouse")
    houses = cur.fetchall()
    cur.close()
    # Render template with houses data
    return render_template('individualhouse_list.html', houses=houses)
    

@app.route('/individualhouse_view', methods=['GET'])
def individualhouse_view():
    cur = mysql.connection.cursor(DictCursor)
    # Fetch all records from the IndividualHouseView table
    cur.execute("SELECT * FROM IndividualHouse")
    houses = cur.fetchall()
    cur.close()
    return render_template('individualhouse_view.html', houses=houses)


@app.route('/villa_list', methods=['GET'])
def villa_list():
    cur = mysql.connection.cursor(DictCursor)
    # Fetch all records from the Villas table
    cur.execute("SELECT * FROM Villas")
    villas = cur.fetchall()
    cur.close()
    # Render template with villas data 
    return render_template('villa_list.html', villas=villas) 

'''@app.route('/villa_list')
def villa_list():
    cur = mysql.connection.cursor(cursorclass=DictCursor)
    cur.execute("SELECT VillaId, Name, Phone, Email, SqFeet, BHKNumber, FloorNo, TotalFloors, Price, Landmark, Address, Pincode, NearbyFacility, OutstandingLoan, LoanAmount, LoanBalance, LenderName, NextRepayment, Amenities, Pool, Garden, Status, Image FROM villas")
    villas = cur.fetchall()
    cur.close()
    return render_template('villa_list.html', villas=villas)''' 

@app.route('/land_list', methods=['GET'])
def land_list():
    cur = mysql.connection.cursor(DictCursor)
    cur.execute("SELECT * FROM Lands")
    lands = cur.fetchall()
    cur.close()
    return render_template('land_list.html', lands=lands)

@app.route('/apartment_view')
def apartment_view():
    cur = mysql.connection.cursor(cursorclass=DictCursor)
    cur.execute("SELECT * FROM Apartments")
    apartments = cur.fetchall()
    cur.close()
    return render_template('apartment_view.html', apartments=apartments)

@app.route('/land_view')
def land_view():
    cur = mysql.connection.cursor(cursorclass=DictCursor)
    cur.execute("SELECT * FROM Lands")  # Adjust the table name if needed
    lands = cur.fetchall()
    cur.close()
    return render_template('land_view.html', lands=lands)


@app.route('/villa_view')
def villa_view():
    cur = mysql.connection.cursor(cursorclass=DictCursor)
    cur.execute("SELECT * FROM Villas")
    villas = cur.fetchall()
    cur.close()
    return render_template('villa_view.html', villas=villas)
    
# <----DOWNLOAD IMAGES FOR APARTMENT ---->
@app.route('/download_apart/<int:apartment_id>', methods=['GET'])
def download_apart(apartment_id):
    # Fetch the image filename from the database for the given apartment_id
    cur = mysql.connection.cursor(DictCursor)
    cur.execute("SELECT Image FROM Apartments WHERE ApartmentID = %s", (apartment_id,))
    result = cur.fetchone()
    cur.close()
    if not result or not result['Image']:
        return "Image not found", 404
    
    # URL of the image in the static folder
    image_filename = result['Image']
    image_url = url_for('static', filename=f'uploads_apartment/{image_filename}', _external=True)
    save_path = os.path.join(UPLOAD_FOLDER, image_filename)

    # Download and save the image
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                file.write(response.content)
            return send_file(save_path, as_attachment=True)
        else:
            return "Failed to download image", 400
    except Exception as e:
        return f"An error occurred: {str(e)}", 500
    
@app.route('/download_loandoc_apart/<int:apartment_id>', methods=['GET'])
def download_loandoc_apart(apartment_id):
    # Fetch the loan document filename from the database for the given apartment_id
    cur = mysql.connection.cursor(DictCursor)
    cur.execute("SELECT LoanDocument FROM Apartments WHERE ApartmentID = %s", (apartment_id,))
    result = cur.fetchone()
    cur.close()

    if not result or not result['LoanDocument']:
        return "Loan document not found", 404

    # URL of the loan document in the static folder
    loan_filename = result['LoanDocument']
    loan_url = url_for('static', filename=f'uploads_loandoc/{loan_filename}', _external=True)
    save_path = os.path.join(UPLOAD_FOLDER, loan_filename)  # Adjust path as needed

    # Download and save the loan document
    try:
        response = requests.get(loan_url)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                file.write(response.content)
            return send_file(save_path, as_attachment=True)
        else:
            return "Failed to download loan document", 400
    except Exception as e:
        return f"An error occurred: {str(e)}", 500
    
@app.route('/delete_villa/<int:villa_id>', methods=['POST'])
def delete_villa(villa_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM Villas WHERE VillaId = %s", (villa_id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('villa_list'))

@app.route('/delete_apartment/<int:apartment_id>', methods=['POST'])
def delete_apartment(apartment_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM Apartments WHERE ApartmentID = %s", (apartment_id,))
    mysql.connection.commit() 
    cur.close()
    return redirect(url_for('apartment_list'))

@app.route('/delete_land/<int:land_id>', methods=['POST'])
def delete_land(land_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM Lands WHERE LandID = %s", (land_id,))
    mysql.connection.commit() 
    cur.close()
    return redirect(url_for('land_list'))

@app.route('/delete_individualhouse/<int:individualhouse_id>', methods=['POST'])
def delete_individualhouse(individualhouse_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM IndividualHouse WHERE HouseId = %s", (individualhouse_id,))
    mysql.connection.commit() 
    cur.close()
    return redirect(url_for('individualhouse_list')) 

if __name__=='__main__':
    app.run(debug=True) 