import re
import json
import os
import uuid

from flask import Flask, redirect, render_template, request, session, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from tempfile import mkdtemp
# about uploads
from flask_uploads import UploadSet, configure_uploads, IMAGES

from lib import login_required, admin_required, hashPassword, verifyPassword
from datetime import date

from flask_restful import Api, Resource
from webargs import fields, validate
from webargs.flaskparser import use_kwargs, parser

# Configure application
app = Flask(__name__)
api = Api(app)

# connect database
app.config['SQLALCHEMY_DATABASE_URI'] = 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.debug = True
db = SQLAlchemy(app)

# set upload images
photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = 'static/uploads'
configure_uploads(app, photos)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30))
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(30))
    password = db.Column(db.String(1000))

    def __init__(self, username, email, phone, password):
        self.username = username
        self.email = email
        self.phone = phone
        self.password = password
    
    def __repr__(self):
        return '<User %r>' % self.username

class Stores(db.Model):
    storeid = db.Column(db.Integer, primary_key=True)
    notice = db.Column(db.Text)

    def __init__(self, notice):
        self.notice = notice
    
    def __repr__(self):
        return '<Stores %r>' % self.notice

class Categories(db.Model):
    catid = db.Column(db.Integer, primary_key=True)
    catname = db.Column(db.String(100), unique=True)
    catimg = db.Column(db.String(300))

    def __init__(self, catname, catimg):
        self.catname = catname
        self.catimg = catimg
    
    def __repr__(self):
        return '<Categories %r>' % self.catname

class Store(db.Model):
    productid = db.Column(db.Integer, primary_key=True)
    catid = db.Column(db.Integer)
    productname = db.Column(db.String(100))
    productprice = db.Column(db.String(30))
    productimg = db.Column(db.String(300))
    product_des = db.Column(db.Text)

    def __init__(self, catid, productname, productprice, productimg, product_des):
        self.catid = catid
        self.productname = productname
        self.productprice = productprice
        self.productimg = productimg
        self.product_des = product_des
    
    def __repr__(self):
        return '<Store %r>' % self.productname

class Cart(db.Model):
    cartid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer)
    ordernum = db.Column(db.String(100))
    productname = db.Column(db.String(100))
    productprice = db.Column(db.String(30))
    amount = db.Column(db.Integer)
    isdone = db.Column(db.Boolean)
    time = db.Column(db.DateTime)

    def __init__(self, userid, ordernum, productname, productprice, amount, isdone, time):
        self.userid = userid
        self.ordernum = ordernum
        self.productname = productname
        self.productprice = productprice
        self.amount = amount
        self.isdone = isdone
        self.time = time
    
    def __repr__(self):
        return '<Store %r>' % self.productname

# This error handler is necessary for usage with Flask-RESTful.
@parser.error_handler
def handle_request_parsing_error(err, req, schema, *, error_status_code, error_headers):
    abort(error_status_code, errors=err.messages)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/')
def hello_world():
    # session[""]
    return render_template("home.html")

@app.route('/adminlogin', methods=["GET", "POST"])
def adminlogin():
    """Login admin"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        password = request.form.get('password')
        with open('adminpassword.json') as f:
            data = json.load(f)

        if not verifyPassword(data["password"], password):
                return render_template("adminlogin.html", msg = "Password is not correct!")

        # Remember which admin has logged in
        session["admin"] = data["id"]

        return redirect(url_for('adminsettings'))
    else:
        return render_template("adminlogin.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
     # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        cpwd = request.form.get('confirmation')

        if not username:
            msg = "Username is empty!"
            return render_template("register.html", msg = msg)
        
        if not email:
            msg = "Email is empty!"
            return render_template("register.html", msg = msg)
        
        if not phone:
            msg = "Phone is empty!"
            return render_template("register.html", msg = msg)

        if not password:
            msg = "Password is empty!"
            return render_template("register.html", msg = msg)
        
        if not cpwd:
            msg = "Please confirm your password is empty!"
            return render_template("register.html", msg = msg)
        
        if not password == cpwd:
            msg = "Please enter same passwords!"
            return render_template("register.html", msg = msg)

        if len(password) < 8:
            return render_template("register.html", msg = "password must have at least 8 characters")
        elif re.search('[0-9]',password) is None:
            return render_template("register.html", msg = "password must have numbers")
        elif re.search('[A-Z]',password) is None:
            return render_template("register.html", msg = "password must have capital letters")
        
        # hash password
        """Hash a password for storing."""
        hash = hashPassword(password)

        if db.session.query(User).filter(User.email == email).count() == 0:   
            user = User(username, email, phone, hash)
            db.session.add(user)
            db.session.commit()
            # Redirect user to login page
            return redirect(url_for('login'))
        return render_template("register.html", msg="This email has been used!")
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Login user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        if not email:
            msg = "Email is empty!"
            return render_template("login.html", msg = msg)
        
        if not password:
            msg = "Password is empty!"
            return render_template("login.html", msg = msg)

        if db.session.query(User).filter(User.email == email).count() == 0:
            return render_template("login.html", msg = "Email is not registered!")
        else:
            user = User.query.filter_by(email = email).first()
            print("user ",user.id)
            user_id = user.id
            dbpwd = user.password

            if not verifyPassword(dbpwd, password):
                return render_template("login.html", msg = "Password is not correct!")

            # Remember which user has logged in
            session["user_id"] = user_id

        # Redirect user to login page
        return redirect("/stores")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    """show settings"""
    user_id = session["user_id"]
    user = User.query.filter_by(id = user_id).first()
    username = user.username
    email = user.email
    dbpwd = user.password
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        oldpwd = request.form.get('password')
        npwd = request.form.get('npassword')
        cpwd = request.form.get('confirmation')

        # check old password is right
        if not verifyPassword(dbpwd, oldpwd):
            return render_template("settings.html", name = username, msg="current password is wrong!")
        
        if len(npwd) < 8:
            return render_template("settings.html", name = username, msg = "new password must have at least 8 characters")
        elif re.search('[0-9]',npwd) is None:
            return render_template("settings.html", name = username, msg = "new password must have numbers")
        elif re.search('[A-Z]',npwd) is None:
            return render_template("settings.html", name = username, msg = "new password must have capital letters")

        if not npwd == cpwd:
            return render_template("settings.html", name = username, msg="new passwords do not match!")
        
        """Hash new password for storing."""
        hash = hashPassword(npwd)

        rows_update = User.query.filter_by(id = user_id).update(dict(password = hash))
        db.session.commit()

        return redirect("/login")
    else:
        return render_template("settings.html", name = username, email = email)

@app.route("/userupdate", methods=["POST"])
@login_required
def userupdate():
    user_id = session["user_id"]
    name = request.form.get("username")
    rows_update = User.query.filter_by(id = user_id).update(dict(username = name))
    db.session.commit()

    return redirect("/settings")

@app.route("/stores", methods=["GET"])
def groups():
    """show groups"""
    stores = Stores.query.all()
    cats = Categories.query.all()

    if not stores:
        notice = ""
    else:
        notice = stores[0].notice

    return render_template("group.html", notice = notice, cats = cats)


@app.route("/adminsettings", methods=["GET", "POST"])
@admin_required
def adminsettings():
    """show settings"""
    user_id = session["admin"]
    with open('adminpassword.json') as f:
        data = json.load(f)
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        oldpwd = request.form.get('password')
        npwd = request.form.get('npassword')
        cpwd = request.form.get('confirmation')

        # check old password is right
        if not verifyPassword(data["password"], oldpwd):
            return render_template("adminsettings.html", name = username, msg="current password is wrong!")

        if len(npwd) < 8:
            return render_template("adminsettings.html", name = username, msg = "new password must have at least 8 characters")
        elif re.search('[0-9]',npwd) is None:
            return render_template("adminsettings.html", name = username, msg = "new password must have numbers")
        elif re.search('[A-Z]',npwd) is None:
            return render_template("adminsettings.html", name = username, msg = "new password must have capital letters")

        if not npwd == cpwd:
            return render_template("adminsettings.html", name = username, msg="new passwords do not match!")
        
        """Hash new password for storing."""
        hash = hashPassword(npwd)

        adminpassword = {}
        adminpassword["id"] = 1 
        adminpassword["password"] = hash

        with open("adminpassword.json", "w") as outfile:
            json.dump(adminpassword, outfile)

        return redirect("/adminlogin")
    else:
        return render_template("adminsettings.html")

@app.route('/manage', methods=["GET", "POST"])
@admin_required
def manage():
    """show manage"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        admin_id = session["admin"]
        notice = request.form.get("notice")

        if notice:
            store = Stores(notice)
            db.session.add(store)
            db.session.commit()
        
        return render_template("manage.html")
    else:
        return render_template("manage.html")

@app.route("/manage/addcat", methods=["GET", "POST"])
@admin_required
def addcat():
    """add categories"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        name = request.form.get("name")
        img = request.files['photo']
        imgname = photos.save(request.files['photo'])
        
        cat = Categories(name, imgname)
        db.session.add(cat)
        db.session.commit()
        
        cats = Categories.query.all()
        return render_template("addcats.html", cats = cats)
    else:
        cats = Categories.query.all()
        return render_template("addcats.html", cats = cats)

@app.route("/catedelete/<int:id>", methods=["GET", "POST", "DELETE"])
@admin_required
def catedelete(id):
    """delete category"""
    cat = Categories.query.filter_by(catid=id).first()
    os.remove("static/uploads/"+cat.catimg)
    print(cat)
    db.session.delete(cat)
    db.session.commit()

    return redirect(url_for('addcat'), code=307)

@app.route("/cateupdate/<int:id>", methods=["GET", "POST"])
@admin_required
def cateupdate(id):
    """update category"""
    cat = Categories.query.filter_by(catid=id).first()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        name = request.get.form("name")
        img = request.files['photo']

        if not name:
            catname = cat.catname
        else:
            catname = name          
        
        if not img:
            imgname = cat.catimg
        else:
            imgname = photos.save(request.files['photo'])
            rows_update = Categories.query.filter_by(catid=id).update(dict(catname = catname, catimg = imgname)) 
            db.session.commit()
            os.remove("static/uploads/"+cat.catimg)
            return redirect(url_for('/manage/addcat'))
            

        rows_update = Categories.query.filter_by(catid=id).update(dict(catname = catname, catimg = imgname)) 
        db.session.commit()

        return redirect(url_for('/manage/addcat'))
    else:
        return render_template("cateupdate.html", cat = cat)


@app.route("/manage/additems", methods=["GET", "POST"])
@admin_required
def additems():
    """show additmes"""
    cats = Categories.query.all()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        cat = request.form.get("cat")
        proname = request.form.get("productname")
        photo = request.files['photo']
        des = request.form.get("des")
        price = request.form.get("price")

        if not cat:
            return render_template("additems.html", cats = cats, msg = "Please select product category!")
        
        if not photo:
            imgname = "default_food.jpg"
        else:
            imgname = photos.save(request.files['photo'])

        product = Store(catid = cat, productname = proname, productprice = price, productimg = imgname, product_des = des)
        db.session.add(product)
        db.session.commit()

        return render_template("additems.html", cats = cats, msg ="add successfully!")
    else:
        
        return render_template("additems.html", cats = cats)

@app.route("/cat/<int:id>", methods=["GET", "POST"])
def showproducts(id):
    """show products"""
    products = Store.query.filter_by(catid = id).all()
    print(products)
    if len(products):
        hasPro = True
    else:
        hasPro = False

    return render_template("showproducts.html", products = products, hasPro = hasPro)

@app.route("/showproduct/<int:id>", methods=["GET", "POST"])
def showproduct(id):
    """show products"""
    product = Store.query.filter_by(productid = id).first()
    print(product)

    return render_template("showproduct.html", product = product, userid = session["user_id"])

@app.route("/prodelete/<int:id>", methods=["GET", "POST", "DELETE"])
@admin_required
def prodelete(id):
    """delete product"""
    pro = Store.query.filter_by(productid=id).first()
    if pro.productimg and not pro.productimg == "default_food.jpg":
        os.remove("static/uploads/"+pro.productimg)
    print(pro)
    db.session.delete(pro)
    db.session.commit()

    return redirect(url_for('showproducts', id = pro.catid))

@app.route("/proupdate/<int:id>", methods=["GET", "POST"])
@admin_required
def proupdate(id):
    """update product"""
    pro = Store.query.filter_by(productid=id).first()
    cats = Categories.query.all()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        cat = request.form.get("cat")
        name = request.form.get("name")
        price = request.form.get("price")
        des = request.form.get("des")
        img = request.files['photo']

        if not cat:
            catid = pro.catid
        else:
            catid = cat

        if not name:
            proname = pro.productname
        else:
            proname = name

        if not price:
            price = pro.productprice
        else:
            price = price

        if not des:
            des = pro.product_des
        else:
            des = des  
        
        if not img:
            imgname = pro.productimg
        else:
            imgname = photos.save(request.files['photo'])
            rows_update = Store.query.filter_by(productid=id).update(dict(
                catid = catid, productname = proname, productprice = price, productimg = imgname, product_des = des
            )) 
            db.session.commit()
            os.remove("static/uploads/"+pro.productimg)
            return redirect(url_for('showproducts', id = pro.catid))
            

        rows_update = Store.query.filter_by(productid=id).update(dict(
            catid = catid, productname = proname, productprice = price, productimg = imgname, product_des = des
        ))  
        db.session.commit()

        return redirect(url_for('showproducts', id = pro.catid))
    else:
        return render_template("updatepro.html", pro = pro, cats = cats)

@app.route("/cart", methods=["GET", "POST"])
@login_required
def cart():
    """show cart"""
    return render_template("cart.html")


@app.route("/submitPro", methods=["GET", "POST"])
@login_required
def submitPro():
    userid = session["user_id"]
    info = request.form["info"]
    ordernum = uuid.uuid4().hex
    time = date.today()

    for pro in json.loads(info):
        name = pro[1]
        price = pro[2]
        amount = pro[3]
        cart = Cart(userid = userid, ordernum = ordernum, productname = name, productprice = price, amount = amount, 
        isdone = False, time = time)
        db.session.add(cart)
        db.session.commit()

    return jsonify({"status":"sucess", "order": ordernum})

@app.route("/orderhistory", methods=["GET", "POST"])
@login_required
def orderhistory():
    """show order history"""
    userid = session["user_id"]
    orders = Cart.query.filter_by(userid=userid).all()
    print(orders)
    carts = []
    total = []
    i = " "
    sum = 0
    count = -1
    for order in orders:
        num = order.ordernum
        if not i == num:
            i = num
            count+=1
            print("count", count)
            if not count == 0:
                total.append(sum)
                print("total:", total)
            sum = 0
            carts.append([])
            carts[len(carts)-1].append(order)
            sum = sum + float(order.productprice) * float(order.amount)
            print(sum)
        else:
            carts[len(carts)-1].append(order)
            sum = sum + float(order.productprice) * float(order.amount)
            print(sum)
    total.append(sum)
    print("total:", total)
    return render_template("orderhistory.html", carts = carts, total = total)


@app.route("/orders", methods=["GET", "POST"])
@admin_required
def orders():
    orders = db.session.query(Cart, User).outerjoin(User, Cart.userid == User.id).filter(Cart.isdone == False).order_by(Cart.time.desc()).all()
    print(orders)
    carts = []
    total = []
    i = " "
    sum = 0
    count = -1
    for order in orders:
        num = order[0].ordernum
        if not i == num:
            i = num
            count+=1
            if not count == 0:
                total.append(sum)

            sum = 0
            carts.append([])
            carts[len(carts)-1].append(order)
            sum = sum + float(order[0].productprice) * float(order[0].amount)

        else:
            carts[len(carts)-1].append(order)
            sum = sum + float(order[0].productprice) * float(order[0].amount)
            
    total.append(sum)
    print(carts[0][0][1].username)
    return render_template("orders.html", carts = carts, total = total)

@app.route("/orderdone/<string:id>", methods=["GET", "POST"])
@admin_required
def orderdone(id):
    """mark finished order"""
    print(id)
    rows = Cart.query.filter_by(ordernum = id).update(dict(isdone = True))
    db.session.commit()

    return redirect("/orders")