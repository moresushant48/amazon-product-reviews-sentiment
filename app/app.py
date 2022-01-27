from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL

from algorithm import getDataFrameFromProductLink, getProductBarGraphAndPieChart, getProductImage, html_code, getProductAbout, getProductName

app = Flask(__name__)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'sentiment'

mysql = MySQL(app)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/add-link')
def addLink():
    if(request.args.get('success') == 'true'):
        result = request.args
        return render_template("addLink.html", result=result)
    else:
        return render_template("addLink.html")


@app.route('/insert-link', methods=['POST'])
def insertLink():
    details = request.form
    name = details['name']
    url = details['url']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO products(name,url) VALUES(%s,%s)", (name,
                url))
    mysql.connection.commit()
    cur.close()
    return redirect("product?url=" + url)


@app.route('/search')
def search():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products")
    data = cur.fetchall()
    cur.close()
    return render_template("search.html", data=data)


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
        cur.execute("SELECT url FROM products where id=%s", (id,))
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


@app.route('/about')
def about():
    return render_template("about.html")


app.run(debug=True)
