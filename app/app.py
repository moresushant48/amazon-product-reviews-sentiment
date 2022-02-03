from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL

from algorithm import getDataFrameFromProductLink, getProductBarGraphAndPieChart, getProductImage, html_code, getProductAbout, getProductName

app = Flask(__name__)
app.secret_key = "super secret key"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'sentiment'

mysql = MySQL(app)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/search')
def search():
    return render_template("search.html")


@app.route('/insert-link', methods=['POST'])
def insertLink():
    details = request.form
    name = details['name']
    url = details['url']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO products(name,url) VALUES('{0}','{1}')".format(name,
                url))
    mysql.connection.commit()
    cur.close()
    return redirect("product?url=" + url)


@app.route('/products')
def products():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products")
    data = cur.fetchall()
    cur.close()
    return render_template("products.html", data=data)


@app.route('/product', methods=['POST'])
def product():
    details = request.form
    id = details['id']
    return redirect("product?id=" + id)


@app.route('/product')
def productByIdOrUrl():

    if(request.args.get('id')):
        id = request.args.get('id')
        cur = mysql.connection.cursor()
        cur.execute("SELECT url FROM products where id={0}".format(id))
        data = cur.fetchone()
        cur.close()

        soup = html_code(data[0])
        df = getDataFrameFromProductLink(soup)
        image = getProductImage(soup)
        name = getProductName(soup)
        ul = getProductAbout(soup)
        figures = getProductBarGraphAndPieChart(df)
        return render_template("product.html", row_data=list(df.values.tolist()), image=image, name=name, ul=ul, figures=figures)

    elif(request.args.get('url')):
        url = request.args.get('url')

        soup = html_code(url)
        df = getDataFrameFromProductLink(soup)
        image = getProductImage(soup)
        name = getProductName(soup)
        ul = getProductAbout(soup)
        figures = getProductBarGraphAndPieChart(df)
        return render_template("product.html", row_data=list(df.values.tolist()), image=image, name=name, ul=ul, figures=figures)

    else:
        return render_template("product.html")


# ================================================
# LOGIN & REGISTER


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.values.get('username')
        email = request.values.get('email')
        password = request.values.get('password')
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(email,password,username) VALUES('{0}','{1}','{2}')".format(
            email, password, username))
        mysql.connection.commit()
        cur.close()
        return render_template("register.html", msg="Registration Successful. Please Login")
    else:
        return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.values.get('email')
        password = request.values.get('password')
        if email.strip() == "admin@gmail.com" and password.strip() == "123456":
            session['isAdmin'] = True
            session['isLoggedIn'] = True
            session['email'] = email
            return redirect("/admin/users")
        else:
            cur = mysql.connection.cursor()
            cur.execute(
                "SELECT * FROM users WHERE email = '{0}' AND password = '{1}'".format(email, password))
            users = cur.fetchall()
            cur.close()

            if len(users) > 0:
                session['isAdmin'] = False
                session['isLoggedIn'] = True
                session['email'] = users[0][1]
                session['username'] = users[0][3]
                return redirect("/")
            else:
                return render_template("login.html", invalidCreds=True)

    else:
        return render_template("login.html")


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ================================================
# ADMIN


@app.route('/admin/users')
def adminUsers():
    if session.get('isAdmin') == True:
        # Get users
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        cur.close()

        return render_template("admin-users.html", users=users)
    else:
        return render_template("admin-users.html")


@app.route('/del/users')
def usersDelete():
    if request.args.get('id'):
        id = request.args.get('id')
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM users WHERE id = {0}'.format(id))
        mysql.connection.commit()
        cur.close()

    return redirect("/admin/users")


@app.route('/admin/products')
def adminProducts():
    if session.get('isAdmin') == True:

        # Get Products
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM products")
        products = cur.fetchall()
        cur.close()

        return render_template("admin-products.html", products=products)
    else:
        return render_template("admin-products.html")


@app.route('/del/products')
def productsDelete():
    if request.args.get('id'):
        id = request.args.get('id')
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM products WHERE id = {0}'.format(id))
        mysql.connection.commit()
        cur.close()

    return redirect("/admin/products")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contact-us')
def contactUs():
    return render_template("contact-us.html")


app.run(debug=True)
