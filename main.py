from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
from werkzeug.utils import secure_filename
import os, random, time
from mylib import *




app = Flask(__name__)
app.secret_key="super secret key"
app.config['UPLOAD_FOLDER']='static/photos'
app.config['BLOG_UPLOAD']='static/blogImages'



def placeOrder():
    email = session["email"]
    total = session["total"]
    conn = pymysql.connect(host="localhost", port=3306, user="root", passwd="", db="arbor")
    cur = conn.cursor()
    sql = "SELECT u_id FROM user_details WHERE email='" + email + "'"
    cur.execute(sql)
    n = cur.rowcount
    if n == 1:
        data = cur.fetchone()
        userid = data[0]
        q = "SELECT product_id FROM cart WHERE user_id=%s"
        cur.execute(q, userid)
        m = cur.rowcount
        if m > 0:
            data1 = cur.fetchall()
            tup = tuple()
            for k in data1:
                tup = tup + k
            tup = str(tup)
            sq = "SELECT MAX(order_id) FROM orders"
            if cur.execute(sq):
                id = cur.fetchone()
                id = id[0] + 1
                status = 'PENDING'
                conn.autocommit = False
                sql1 = 'INSERT INTO orders(order_id,user_id,total,status,product_id) VALUES(%s,%s,%s,%s,%s)'
                sq = 'INSERT INTO shipping_address VALUES(%s,%s,%s,%s,%s,%s,%s,%s)'
                record = (id,userid,total,status,tup)
                record1 = (session['name'],session['address'], session['houseno'], session['city'],session['state'], session['pincode'],session['phno'], id)
                cur.execute(sql1, record)
                l = cur.rowcount
                cur.execute(sq, record1)
                z = cur.rowcount
                if l == 1 and z ==1:
                    session.pop('name', None)
                    session.pop('address', None)
                    session.pop('houseno', None)
                    session.pop('city', None)
                    session.pop('pincode', None)
                    session.pop('state', None)
                    session.pop('phno', None)
                    print("order maded")
                    q = "SELECT product_id, quantity FROM cart WHERE user_id=%s"
                    cur.execute(q, userid)
                    m = cur.rowcount
                    if m > 0:
                        data2 = cur.fetchall()
                        for k in data2:
                            q2 = "SELECT stock FROM products WHERE product_id = %s"
                            if cur.execute(q2, k[0]):
                                data = cur.fetchone()
                                new = data[0] - k[1]
                                q3 = "UPDATE products SET stock = %s WHERE product_id = %s"
                                record = (new, k[0])
                                if cur.execute(q3, record):
                                    print("updated stock")
                        sql = "DELETE FROM cart WHERE user_id = %s"
                        if cur.execute(sql, userid):
                            print("Deleted from cart")
                            conn.commit()
                            return 1
                        else:
                            conn.rollback()
                            return 0
                    else:
                        conn.rollback()
                        return 0
                else:
                    conn.rollback()
                    return 0
            return 0
        return 0
    return 0


@app.route('/autherror')
def autherror():
    return render_template('AuthError.html')


@app.route('/')
def index():
    if 'email' in session and "ADMIN" == session["secret"]:
        return redirect(url_for('adminhome'))
    elif 'email' in session and "WORKER" == session["secret"]:
        return redirect(url_for('worker'))
    else:
        return redirect(url_for('userhome'))






@app.route('/logout')
def logout():
    if 'email' in session:
        session.pop('email', None)
        session.pop('role',None)
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))




@app.route('/reg', methods=['GET','POST'])
def reg():
    if request.method == 'POST':
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        email = request.form['email']
        password = request.form['password']
        details = (first_name,last_name,email,password)
        otp = genrateotp()
        return render_template('reg.html', otp = otp, data=details)




@app.route('/register',methods=['GET','Post'])
def register():
    if request.method == 'POST':
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        email = request.form['email']
        print('email: ', email)
        password = request.form['password']
        secret ="USER"
        cur=connect_to_database()
        sql = "SELECT * FROM login WHERE email = %s"
        cur.execute(sql, email)
        n = cur.rowcount
        if n == 0:
            sql1 = "SELECT MAX(id) FROM login"
            if cur.execute(sql1):
                data = cur.fetchone()
                id = data[0]
            else:
                id = 0
            number = id + 1
            write_key(number)
            epassword = encrypt_password(password, number)
            print(epassword)
            epassword = epassword.decode()
            print(epassword)
            sql2 = "INSERT INTO login VALUES(%s,%s,%s,%s)"
            print(sql2)
            record = (email, epassword, secret, number)
            if cur.execute(sql2, record):
                q = "INSERT INTO user_details(firstname,lastname,email) VALUES(%s,%s,%s)"
                data3 = (first_name, last_name, email)
                if (cur.execute(q, data3)):
                    return render_template('Login.html')
            else:
                return render_template('Register.html', message="ACCOUNT NOT CREATED")
        else:
            return render_template('Register.html',message="EMAIL ALREADY EXSITS")
    else:
        return render_template('Register.html')




@app.route('/adminregister',methods=['GET','Post'])
def adminregister():
    if request.method == 'POST':
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        email = request.form['email']
        password = request.form['password']
        secret = request.form['secret']
        if secret == "ADMIN":
            cur=connect_to_database()
            sql = "SELECT * FROM login WHERE email = %s"
            cur.execute(sql, email)
            n = cur.rowcount
            if n == 0:
                q = "INSERT INTO user_details(firstname,lastname,email) VALUES(%s,%s,%s)"
                data3 = (first_name, last_name, email)
                if (cur.execute(q, data3)):
                    sql1 = "SELECT MAX(id) FROM login"
                    if cur.execute(sql1):
                        data = cur.fetchone()
                        id = data[0]
                        number = id + 1
                        write_key(number)
                        epassword = encrypt_password(password, number)
                        epassword=epassword.decode()
                        sql2 = "INSERT INTO login VALUES(%s,%s,%s,%s)"
                        record = (email,epassword,secret,number)
                        if cur.execute(sql2,record):
                            return render_template('Login.html')
                        else:
                            return render_template('adminRegister.html', message="ACCOUNT NOT CREATED")
                else:
                    return render_template('adminRegister.html', message="ERROR OCCURED PLEASE TRY AGAIN!!")
            else:
                return render_template('adminRegister.html',message="EMAIL ALREADY EXSITS")
        else:
            return render_template('adminRegister.html', message="WRONG SECURITY KEY")
    else:
        return render_template('adminRegister.html')







@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cur = connect_to_database()
        sql = "SELECT * FROM login WHERE email = %s"
        cur.execute(sql,email)
        n = cur.rowcount
        if n == 1:
            data = cur.fetchone()
            password1=data[1]
            print(password1)
            decrypted_password=decrypt_password(password1,data[3])
            print(decrypted_password)
            if password.encode() == decrypted_password:
                session["email"] = email
                session["secret"] = data[2]
                if data[2] == "ADMIN":
                    return redirect(url_for('adminhome'))
                elif data[2] == 'WORKER':
                    return redirect(url_for('worker'))
                else:
                    return redirect(url_for('index'))
            else:
                return render_template('Login.html',message="WRONG PASSWORD")
        else:
            return render_template('Login.html', message="WRONG EMAIL")
    else:
        return render_template('Login.html')




@app.route('/admin')
def adminhome():
    if 'email' in session:
        secret = session['secret']
        if secret =="ADMIN":
            return render_template('Adminhome.html',message="WELCOME ADMIN")
        else:
            return redirect(url_for('autherror'))
    else:
        return redirect(url_for('autherror'))




@app.route('/manageproducts')
def manageproducts():
    if 'email' in session:
        secret = session['secret']
        if secret == "ADMIN":
            cur = connect_to_database()
            q = "SELECT * FROM products"
            if (cur.execute(q)):
                data = cur.fetchall()
                return render_template('ManageProducts.html', productDetails=data)
            else:
                return render_template('ManageProducts.html', message="No Data in Database")
        else:
            return redirect(url_for('autherror'))
    else:
        return redirect(url_for('autherror'))




@app.route("/deleteproduct", methods=['POST'])
def deleteproduct():
    if 'email' in session:
        secret = session["secret"]
        if secret == "ADMIN":
            filename = request.form["filename"]
            product_id = request.form['productId']
            cur = connect_to_database()
            try:
                # q1 = "DELETE products, cart FROM products INNER JOIN cart ON products.product_id=cart.product_id WHERE products.product_id=%s"
                # cur.execute(q1, product_id)
                # m = cur.rowcount
                # if m > 0:
                #     print("deleted")
                #     os.unlink(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                #     flash("Deleted successfully from both cart and products")
                #     return redirect(url_for('adminhome'))
                # else:
                sql = "DELETE FROM products WHERE product_id = %s"
                cur.execute(sql, product_id)
                n = cur.rowcount
                if n == 1:
                    os.unlink(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    flash("deleted from products")
                    return redirect(url_for('manageproducts'))
            except:
                flash("exception")
                return redirect(url_for('manageproducts'))
        else:
            return redirect(url_for('autherror'))
    else:
        return redirect(url_for('autherror'))



@app.route('/editproduct', methods=['POST'])
def editproduct():
    if 'email' in session:
        secret = session["secret"]
        if secret == "ADMIN":
            product_id = request.form.get('productId')
            cur = connect_to_database()
            try:
                q1 = "SELECT * FROM products WHERE product_id = %s"
                cur.execute(q1, product_id)
                m = cur.rowcount
                if m == 1:
                    data = cur.fetchone()
                    category_id=data[1]
                    tag_id = data[8]
                    q2 = "SELECT * FROM categories where category_id=%s"
                    cur.execute(q2,category_id)
                    n = cur.rowcount
                    print("n: ",n)
                    if n==1:
                        data2 = cur.fetchone()
                        print(data2)
                        q3 = "SELECT * FROM categories WHERE category_id"
                        cur.execute(q3)
                        z = cur.rowcount
                        print("z: ",z)
                        if z>0:
                            print("here")
                            cat_info = cur.fetchall()
                            q3 = "SELECT * FROM tags where tag_id=%s"
                            cur.execute(q3, tag_id)
                            m = cur.rowcount
                            if m==1:
                                tag=cur.fetchone()
                                q3 = "SELECT * FROM tags WHERE tag_id"
                                cur.execute(q3)
                                l = cur.rowcount
                                if l>0:
                                    tag_info=cur.fetchall()
                                    return render_template('editproduct.html', data=data, category=data2,
                                                           cat_info=cat_info, tag=tag,tag_info=tag_info)
                            print("last",cat_info)
                            return render_template('editproduct.html', data=data, category=data2,cat_info=cat_info)
                        else:
                            return render_template('msg.html', data=data, category=data2)
                    else:
                        return render_template('editproduct.html',message="no data found")
            except:
                flash("exception")
                return redirect(url_for('adminhome'))
        else:
            return redirect(url_for('autherror'))
    else:
        return redirect(url_for('autherror'))



@app.route('/editproduct1', methods=['POST'])
def editproduct1():
    if 'email' in session:
        secret = session["secret"]
        if secret == "ADMIN":
            product_id = request.form["productId"]
            name = request.form["name"]
            discription = request.form["discription"]
            stock = request.form["stock"]
            price = request.form["price"]
            category_id = request.form["categoryId"]
            discount = request.form["discount"]
            tag_id = request.form["tagId"]
            cur = connect_to_database()
            q = "UPDATE products SET name=%s,discription=%s,price=%s,stock=%s,category_id=%s,discount=%s,tag_id=%s WHERE product_id=%s"
            data = (name, discription, price, stock, category_id, discount, tag_id, product_id)
            try:
                cur.execute(q, data)
                n = cur.rowcount
                if n == 1:
                    flash("update successfull:)")
                    return redirect(url_for('manageproducts'))
            except:
                return render_template('ManageProducts.html', message="i dont know i hate this")
    return redirect(url_for('autherror'))



@app.route('/updatephoto')
def updatephoto():
    if 'email' in session:
        secret = session["secret"]
        if secret == "ADMIN":
            product_id = int(request.args.get('productId'))
            image = request.args.get('image')
            return render_template('updatephoto.html', data=product_id, image=image)
        else:
            return redirect(url_for('autherror'))
    else:
        return redirect(url_for('autherror'))




@app.route('/updatephoto2', methods=['POST'])
def updatehoto2():
    if 'email' in session:
        secret =session["secret"]
        if secret == "ADMIN":
            product_id = request.form['productId']
            image = request.form['previmage']
            file = request.files['image']
            if file:
                path = os.path.basename(file.filename)
                file_ext = os.path.splitext(path)[1][1:]
                filename = str(int(time.time())) + '.' + file_ext
                filename = secure_filename(filename)
                print(filename)
                cur = connect_to_database()
                sql = "UPDATE products SET product_img=%s WHERE product_id=%s"
                data = (filename, product_id)
                try:
                    print(data)
                    cur.execute(sql, data)
                    n = cur.rowcount
                    print("n:", n)
                    if n == 1:
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        os.unlink(os.path.join(app.config['UPLOAD_FOLDER'], image))
                        flash("update successfull")
                        return redirect(url_for('manageproducts'))
                except:
                    flash("execption")
                    return redirect(url_for('adminhome'))
            else:
                return render_template("msg.html", message="no file:(")
    else:
        return redirect(url_for('autherror'))




@app.route('/add', methods=['Get', 'Post'])
def add():
    if 'email' in session:
        secret = session["secret"]
        if secret == "ADMIN":
            cur = connect_to_database()
            sql = "SELECT * FROM categories"
            cur.execute(sql)
            n = cur.rowcount
            if n>0:
                data = cur.fetchall()
                sql2 = "SELECT * FROM tags"
                cur.execute(sql2)
                m = cur.execute(sql2)
                if m>0:
                    tag=cur.fetchall()
                    return render_template('AddItems.html', data=data, tag=tag)
                else:
                    return render_template('AddItems.html',data=data)
            else:
                return render_template('AddItems.html',message="no categories in the database")
    return redirect(url_for('autherror'))



@app.route('/additem', methods=['Post'])
def additem():
    if 'email' in session:
        file = request.files["image"]
        name = request.form["name"]
        discription = request.form["discription"]
        price = request.form["price"]
        category_id = int(request.form['categoryId'])
        tag_id = int(request.form['tagId'])
        stock = int(request.form['stock'])
        discount = request.form['discount']
        if file:
            path = os.path.basename(file.filename)
            file_ext = os.path.splitext(path)[1][1:]
            filename = str(int(time.time())) + '.' + file_ext
            filename = secure_filename(filename)
            cur = connect_to_database()
            sql = """insert into products(category_id,name,discription,price,product_img,stock,discount,tag_id) values(%s,%s,%s,%s,%s,%s,%s,%s)"""
            record = (category_id, name, discription, price, filename, stock, discount, tag_id)
            try:
                cur.execute(sql, record)
                n = cur.rowcount
                if (n == 1):
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    flash("product has been added successfully")
                    return redirect(url_for('add'))
                else:
                    return render_template('msg.html', message="Failed")
            except:
                return render_template('msg.html', message="execptional case")
        else:
            return render_template('msg.html', message="no file")
    else:
        return redirect(url_for('autherror'))



@app.route('/search', methods=['GET','POST'])
def search():
    if "email" in session:
        if request.method=="POST":
            search = request.form["search"]
            cur=connect_to_database()
            sql="SELECT * FROM products WHERE name='" + search + "'"
            cur.execute(sql)
            n=cur.rowcount
            if n>0:
                data = cur.fetchall()
                secret=session["secret"]
                if secret == "ADMIN":
                    return render_template('ManageProducts.html',productDetails=data)
                else:
                    return redirect(url_for('autherror'))
            else:
                return render_template('ManageProducts.html',message="no products available of this name")
        else:
            return render_template('msg.html', message="error in searching")
    else:
        return redirect(url_for('autherror'))



@app.route('/addCategory')
def addCategory():
    if 'email' in session:
        secret = session["secret"]
        if secret == "ADMIN":
            return render_template('addCategory.html')
        else:
            return redirect(url_for('autherror'))
    else:
        return redirect(url_for('autherror'))


@app.route('/addCategory2',methods=['POST'])
def addCategory2():
    if 'email' in session:
        secret = session["secret"]
        if secret == "ADMIN":
            category = request.form['category']
            cur = connect_to_database()
            sql = "INSERT INTO categories(category) values('" + category + "')"
            try:
                cur.execute(sql)
                n = cur.rowcount
                if n == 1:
                    flash("Category Added")
                    return redirect(url_for('addCategory'))
            except:
                flash("exception")
                return redirect(url_for('addCategory'))
        else:
            return redirect(url_for('autherror'))
    else:
        return redirect(url_for('autherror'))


@app.route('/editCategory')
def editCategory():
    if 'email' in session:
        secret = session["secret"]
        if secret == "ADMIN":
            cur=connect_to_database()
            sql="SELECT * FROM categories"
            try:
                cur.execute(sql)
                n=cur.rowcount
                if n>0:
                    data=cur.fetchall()
                    return render_template('editCategory.html',data=data)
                else:
                    return render_template('editCategory.html',message="No Category Available")
            except:
                return render_template('msg.html', msg="execption")
        else:
            return redirect(url_for('autherror'))
    else:
        return redirect(url_for('autherror'))


@app.route('/deleteCategory',methods=['POST'])
def deleteCategory():
    if 'email' in session:
        secret = session["secret"]
        if secret == "ADMIN":
            category_id = request.form['categoryId']
            cur = connect_to_database()
            sql = "DELETE FROM categories WHERE category_id='" + category_id + "'"
            cur.execute(sql)
            m = cur.rowcount
            if m == 1:
                flash("deleted")
                return redirect(url_for('editCategory'))
            # qu = "SELECT category_id FROM products"
            # cur.execute(qu)
            # a = cur.rowcount
            # if a > 0:
            #     cate = cur.fetchall()
            #     temp = tuple()
            #     for k in cate:
            #         temp = temp + k
            #     if category_id in temp:
            #         q = "SELECT products.product_img FROM products INNER JOIN categories ON products.category_id=categories.category_id WHERE categories.category_id=%s"
            #         cur.execute(q, category_id)
            #         m = cur.rowcount
            #         if m > 0:
            #             data = cur.fetchall()
            #             data1 = tuple()
            #             for k in data:
            #                 data1 = data1 + k
            #             sql = "DELETE products, categories FROM categories INNER JOIN products ON products.category_id=categories.category_id WHERE categories.category_id=%s"
            #             try:
            #                 cur.execute(sql)
            #                 n = cur.rowcount
            #                 if n > 0:
            #                     for j in data1:
            #                         os.unlink(os.path.join(app.config['UPLOAD_FOLDER'], j))
            #                     flash("Category deleted")
            #                     sql1 = "DELETE FROM tags WHERE category_id='" + category_id + "'"
            #                     cur.execute(sql1)
            #                     z = cur.rowcount
            #                     if z > 0:
            #                         print("tags deleted")
            #                     return redirect(url_for('editCategory'))
            #             except:
            #                 flash("exception")
            #                 return redirect(url_for('editCategory'))
            #     else:
            #         sql3 = "SELECT category_id FROM tags"
            #         cur.execute(sql3)
            #         s = cur.rowcount
            #         if s > 0:
            #             data7 = cur.fetchall()
            #             temp = tuple()
            #             for k in data7:
            #                 temp = temp + k
            #             if category_id in temp:
            #                 sql = "DELETE categories,tags FROM categories INNER JOIN tags ON categories.category_id=tags.category_id WHERE categories.category_id =%s"
            #                 cur.execute(sql, category_id)
            #                 m = cur.rowcount
            #                 if m > 0:
            #                     flash("deleted")
            #                     return redirect(url_for('editCategory'))
            #             else:

        else:
            return redirect(url_for('autherror'))
    else:
        return redirect(url_for('autherror'))



@app.route('/tags')
def tags():
    if 'email' in session:
        secret = session["secret"]
        if secret == "ADMIN":
            cur = connect_to_database()
            sql1= "SELECT * FROM tags"
            cur.execute(sql1)
            n = cur.rowcount
            if n>0:
                data=cur.fetchall()
                return render_template('tags.html', data=data)
            else:
                return render_template('tags.html',message="no data found")
        else:
            return redirect(url_for('autherror'))
    else:
        return redirect(url_for('autherror'))



@app.route('/addtags')
def addtags():
    if 'email' in session:
        secret = session["secret"]
        if secret == "ADMIN":
            cur = connect_to_database()
            sql1= "SELECT * FROM categories"
            cur.execute(sql1)
            n = cur.rowcount
            if n>0:
                data=cur.fetchall()
                return render_template('Addtags.html', data=data)
            else:
                return render_template('Addtags.html',message="no data found")
        else:
            return redirect(url_for('autherror'))
    else:
        return redirect(url_for('autherror'))


@app.route('/addtag2',methods=['GET','POST'])
def addtag2():
    if 'email' in session:
        secret = session["secret"]
        if secret == "ADMIN":
            if request.method=='POST':
                tag = request.form['tag']
                category_id = request.form['categoryId']
                cur=connect_to_database()
                sql="INSERT INTO tags(tag,category_id) values('"+tag+"', '"+category_id+"')"
                try:
                    cur.execute(sql)
                    n=cur.rowcount
                    if n==1:
                        flash("tag Added")
                        return redirect(url_for('addtags'))
                except:
                    flash("exception")
                    return redirect(url_for('addtags'))
            else:
                return render_template('msg.html', msg="no post")
        else:
            return redirect(url_for('autherror'))
    else:
        return redirect(url_for('autherror'))






@app.route('/deletetag',methods=['GET','POST'])
def deletetag():
    global data1
    if 'email' in session:
        secret = session["secret"]
        if secret == "ADMIN":
            if request.method=='POST':
                tag_id = request.form['tagId']
                cur=connect_to_database()
                sql = "DELETE FROM tags WHERE tag_id='" + tag_id + "'"
                cur.execute(sql)
                m = cur.rowcount
                if m == 1:
                    flash("tag deleted")
                    return redirect(url_for('tags'))
                else:
                    flash("no deletion")
                    return redirect(url_for('tags'))
                # q = "SELECT products.product_img FROM products INNER JOIN tags ON products.tag_id=tags.tag_id WHERE tags.tag_id=%s"
                # cur.execute(q,tag_id)
                # m=cur.rowcount
                # if m>0:
                #     data=cur.fetchall()
                #     data1=tuple()
                #     for k in data:
                #         data1=data1+k
                #     sql="DELETE products, tags FROM tags INNER JOIN products ON products.tag_id=tags.tag_id WHERE tags.tag_id=%s"
                #     try:
                #         cur.execute(sql,tag_id)
                #         n=cur.rowcount
                #         if n>0:
                #             for j in data1:
                #                 os.unlink(os.path.join(app.config['UPLOAD_FOLDER'], j))
                #             flash("tag deleted")
                #             return redirect(url_for('tags'))
                #         else:
                #             return render_template('msg.html', msg="no fteching of image")
                #     except:
                #         flash("exception")
                #         return redirect(url_for('tags'))
                # else:

            else:
                return render_template('msg.html', msg="no post")
        else:
            return redirect(url_for('autherror'))
    else:
        return redirect(url_for('autherror'))






@app.route('/viewusers')
def viewuser():
    if 'email' in session and "ADMIN" == session["secret"]:
        cur = connect_to_database()
        sql = "SELECT * FROM user_details WHERE email <> %s"
        data = session['email']
        if(cur.execute(sql,data)):
            details = cur.fetchall()
            return render_template('Viweusers.html', data = details)
        else:
            return render_template('Viweusers.html',message="check ur database")
    else:
        return redirect(url_for('autherror'))



@app.route('/addblog',methods=['GET','POST'])
def addblog():
    if 'email' in session and "ADMIN" == session["secret"]:
        return render_template('AddBlog.html')
    else:
        return redirect(url_for('autherror'))



@app.route('/addblog2', methods=['POST'])
def addblog2():
    if 'email' in session and "ADMIN" == session["secret"]:
        file = request.files['image']
        content = request.form['content']
        topic = request.form['topic']
        id = request.form['id']
        if file:
            path = os.path.basename(file.filename)
            file_ext = os.path.splitext(path)[1][1:]
            filename = str(int(time.time())) + '.' + file_ext
            filename = secure_filename(filename)
            cur = connect_to_database()
            sql = "INSERT INTO blog(image,content,topic,b_id) VALUES('" + filename + "','" + content + "','" + topic + "', '"+id+"')"
            if cur.execute(sql):
                file.save(os.path.join(app.config['BLOG_UPLOAD'], filename))
                return render_template('msg.html', msg="blog posted")
            else:
                return render_template('msg.html', msg="Failed")
        else:
            return render_template('msg.html', msg="no file")
    else:
        return redirect(url_for('autherror'))


@app.route('/checkorders')
def checkorders():
    if 'email' in session and "ADMIN" == session["secret"]:
        cur = connect_to_database()
        sql = "SELECT * FROM orders"
        if cur.execute(sql):
            data = cur.fetchall()
            return render_template('ViewOrders.html', data=data)
        else:
            return render_template('ViewOrders.html', message="Zero Order")
    else:
        return redirect(url_for('autherror'))



@app.route('/searchorders', methods=['POST'])
def searchorders():
    if 'email' in session and "ADMIN" == session["secret"]:
        search = request.form["search"]
        cur = connect_to_database()
        sql = "SELECT * FROM orders WHERE order_id=%s or status=%s"
        record = (search,search)
        cur.execute(sql,record)
        n = cur.rowcount
        if n > 0:
            data = cur.fetchall()
            print(data)
            return render_template('ViewOrders.html', data=data)
        else:
            return render_template('ViewOrders.html', message="invalid id or status")
    else:
        return redirect(url_for('autherror'))




@app.route('/worker')
def worker():
    if 'email' in session and session['secret'] == "WORKER":
        return render_template('updatestatus.html',message="WELCOME ADMIN")
    else:
        return redirect(url_for('autherror'))


@app.route('/updatestatus', methods = ['GET', 'POST'])
def updatestatus():
    if 'email' in session and session['secret'] == "WORKER":
        id = request.form["id"]
        status = request.form["status"]
        try:
            cur = connect_to_database()
            sql = "UPDATE orders SET status = '"+status+"' where order_id = '"+id+"'"
            if cur.execute(sql):
                return render_template('updatestatus.html', msg="Updated Successfully")
        except:
            return render_template('updatestatus.html', msg="Error Occured Please Try Again")
    else:
        return redirect(url_for('autherror'))



# ---------------------------------------- USER CODE -------------------------------------
# ---------------------------------------- USER CODE -------------------------------------




@app.route('/userhome',methods=['GET','POST'])
def userhome():
    loggIn = False
    if 'email' in session:
        loggIn = True
    cur = connect_to_database()
    sql ="SELECT * FROM blog LIMIT 4;"
    sql1 = "SELECT * FROM products LIMIT 4"
    cur.execute(sql)
    n = cur.rowcount
    if n>0:
        data = cur.fetchall()
        cur.execute(sql1)
        m = cur.rowcount
        if(m > 0):
            data1 = cur.fetchall()
        return render_template('home.html', loggIn = loggIn,data=data, data1=data1)
    return render_template('home.html',loggIn = loggIn)


@app.route('/usersearch', methods=['GET','POST'])
def usersearch():
    loggIn = False
    if "email" in session:
        loggIn = True
    if request.method=="POST":
        search = request.form["search"]
        cur=connect_to_database()
        sql="SELECT * FROM products WHERE name='" + search + "'"
        cur.execute(sql)
        n=cur.rowcount
        if n>0:
            data = cur.fetchall()
            return render_template('search.html', data=data,loggIn=loggIn)
        else:
            return render_template('msg.html',msg="no products available of this name")
    else:
        return render_template('msg.html',msg="error in searching")


@app.route('/searchby', methods=['GET','POST'])
def searchby():
    loggIn = False
    if "email" in session:
        loggIn = True
    search = request.args.get("search")
    print(search)
    cur = connect_to_database()
    sql = "SELECT * FROM products INNER JOIN categories ON products.category_id=categories.category_id WHERE categories.category_id=%s"
    cur.execute(sql,search)
    n = cur.rowcount
    if n > 0:
        data = cur.fetchall()
        return render_template('search.html', data=data)
    else:
        sql ="SELECT * FROM products INNER JOIN tags ON products.tag_id=tags.tag_id WHERE tags.tag_id=%s"
        cur.execute(sql, search)
        n = cur.rowcount
        if n > 0:
            data = cur.fetchall()
            return render_template('search.html',data=data,loggIn=loggIn)
        else:
            return render_template('msg.html', msg="no products available of this name",loggIn=loggIn)



@app.route('/products')
def products():
    loggIn = False
    if "email" in session:
        loggIn = True
    cur=connect_to_database()
    sql = "SELECT * FROM products"
    cur.execute(sql)
    n=cur.rowcount
    if n>0:
        data = cur.fetchall()
        sql1 = "SELECT * FROM categories"
        cur.execute(sql1)
        m=cur.rowcount
        if m>0:
            category = cur.fetchall()
            sql2 = "SELECT * FROM tags"
            cur.execute(sql2)
            l=cur.rowcount
            if l>0:
                tag=cur.fetchall()
                print('hmmm')
                return render_template('products.html',data=data,loggIn=loggIn,category=category,tag=tag)
            else:
                return render_template('products.html',data=data,loggIn=loggIn,category=category)
        else:
            return render_template('products.html', data=data, loggIn=loggIn)
    else:
        flash("no product available")
        return render_template('products.html')




@app.route('/product_detail',methods=['GET','POST'])
def product_deatil():
    loggIn = False
    if "email" in session:
        loggIn = True
    product_id = request.args.get('product_id')
    print(product_id)
    cur = connect_to_database()
    q = "SELECT * FROM products WHERE product_id = '"+product_id+"'"
    try:
        cur.execute(q)
        n = cur.rowcount
        print(n)
        if n == 1:
            data = cur.fetchone()
            print(data)
            return render_template('productDetail.html',data=data,loggIn=loggIn)
        else:
            return render_template('msg.html',msg="error",loggIn=loggIn)
    except:
        return render_template('msg.html',msg="execption")





@app.route('/addtocart',methods=['GET','POST'])
def addtocart():
    if 'email' in session:
        if request.method=='POST':
            email = session["email"]
            product_id = request.form['product_id']
            price = request.form['price']
            quantity = request.form['quantity']
            cur = connect_to_database()
            try:
                q = "SELECT u_id FROM user_details WHERE email ='" + email + "'"
                cur.execute(q)
                n = cur.rowcount
                if n == 1:
                    data = cur.fetchone()
                    user_id = data[0]
                    q2 = "INSERT INTO cart(user_id,product_id,price,quantity) VALUES(%s,%s,%s,%s)"""
                    record = (user_id, product_id, price,quantity)
                    print(record)
                    cur.execute(q2, record)
                    m = cur.rowcount
                    if m == 1:
                        return render_template('msg.html', msg="Added To Cart")
                    else:
                        return render_template('msg.html', msg="Something Went Wrong")
                else:
                    return render_template('msg.html', msg="error in fetching userid")
            except:
                return render_template('msg.html', msg="Exception")
        else:
            return render_template('msg',msg="no post request")
    else:
        return redirect(url_for('login'))




@app.route('/cart', methods=['GET','POST'])
def cart():
    if 'email' in session:
        loggIn = True
        email = session["email"]
        cur = connect_to_database()
        q = "SELECT u_id FROM user_details WHERE email ='" + email + "'"
        cur.execute(q)
        n = cur.rowcount
        if n == 1:
            data = cur.fetchone()
            user_id = data[0]
            print("userid:", type(user_id))
            q2 = "SELECT products.product_id,products.name,products.product_img,cart.user_id,cart.price, " \
                 "cart.cart_item_id, cart.quantity, products.price, products.discount FROM products INNER JOIN cart ON " \
                 "products.product_id=cart.product_id INNER JOIN user_details ON user_details.u_id=cart.user_id WHERE cart.user_id = %s"
            print("hey")
            cur.execute(q2, user_id)
            m = cur.rowcount
            print("m: ", m)
            if m > 0:
                data1 = cur.fetchall()
                z = len(data1)
                print("length: ", z)
                withoutdiscount = 0
                for j in data1:
                    withoutdiscount = withoutdiscount + ((j[7])*(j[6]))
                grandtotal = 0
                for k in data1:
                    grandtotal = grandtotal + ((k[4]) * (k[6]))
                print('data1: ', data1)
                return render_template('cart.html', data=data1, grandtotal=grandtotal, withoutdiscount=withoutdiscount,
                                       items=z, loggIn=loggIn)
            else:
                return render_template('cart.html', Empty="Empty", loggIn=loggIn)
        else:
            return render_template('msg.html', msg="error occurred")
    else:
        return redirect(url_for('login'))



@app.route('/removefromcart',methods=['GET','POST'])
def removefromcart():
    if 'email' in session:
        loggIn = True
        if request.method=="POST":
            cart_id = request.form['cartId']
            cur = connect_to_database()
            sql ="DELETE FROM cart WHERE cart_item_id='"+cart_id+"'"
            try:
                cur.execute(sql)
                n=cur.rowcount
                if n==1:
                    return redirect(url_for('cart'))
                else:
                    return render_template('msg.html',msg="error",loggIn=loggIn)
            except:
                return render_template('msg.html',msg="exceptional")
        else:
            return render_template('msg.html',msg="no post",loggIn=loggIn)
    else:
        return redirect('autherror')




@app.route('/purchase',methods=['GET','POST'])
def purchase():
    print('okkk')
    if 'email' in session:
        loggIn = True
        total= request.args.get("grandtotal")
        session['total'] = total
        return render_template('address.html',loggIn=loggIn)
    else:
        return redirect(url_for('login'))


@app.route('/pay', methods=['POST'])
def pay():
    if 'email' in session:
        if request.method == 'POST':
            session['name'] = request.form['name']
            session['address'] = request.form['address']
            session['city'] = request.form['city']
            session['state'] = request.form['state']
            session['houseno'] = request.form['houseno']
            session['pincode'] = request.form['pincode']
            session['phno'] = request.form['phno']
            return render_template('checkout.html')
    else:
        return redirect(url_for('autherror'))




@app.route('/pay1', methods=['GET', 'POST'])
def pay1():
    if 'email' in session:
        loggIn = True
        if request.method == 'POST':
            cardname = request.form["cardname"]
            cardnumber = request.form['cardnumber']
            expmonth = request.form['expmonth']
            expyear = request.form['expyear']
            cvv = request.form['cvv']
            session["cardnumber"] = cardnumber
            cur = connect_to_bank()
            sql = "SELECT * FROM cards WHERE cardnumber='" + cardnumber + "'"
            cur.execute(sql)
            n = cur.rowcount
            if n == 1:
                data = cur.fetchone()
                if cardname == data[0] and expmonth == data[2] and expyear == data[3] and cvv == data[4]:
                    return redirect(url_for('otp'))
                else:
                    return render_template('checkout.html', msg="Recheck ur details eg: name on card, card expiry, cvv",loggIn=loggIn)
            else:
                return render_template('checkout.html',msg="no card found",loggIn=loggIn)
    else:
        return redirect(url_for('autherror'))



@app.route('/otp', methods=['GET', 'POST'])
def otp():
    if 'email' in session and 'cardnumber' in session:
        email = session["email"]
        otp = str(genrateotp())
        return render_template('otp.html',otp = otp)
    else:
        return redirect(url_for('autherror'))



@app.route('/deductmoney', methods=['GET', 'POST'])
def deductmoney():
    print(session["email"])
    if 'email' in session and 'cardnumber' in session:
        conn = pymysql.connect(host="localhost", port=3306, user="root", passwd="", db="banksystem")
        cur = conn.cursor()
        cardnumber = "111122223333"
        sql = "SELECT balance from account WHERE cardnumber = '"+session["cardnumber"]+"'"
        cur.execute(sql)
        n = cur.rowcount
        if n == 1:
            data = cur.fetchone()
            if int(data[0])> int(session['total']):
                balance = int(data[0]) - int(session['total'])
                sql = "SELECT balance from account WHERE cardnumber = %s"
                if cur.execute(sql, cardnumber):
                    data = cur.fetchone()
                    data = int(data[0]) + int(session['total'])
                    conn.autocommit = False
                    q1 = "UPDATE account SET balance = %s WHERE cardnumber = %s"
                    q2 = "UPDATE account SET balance = %s WHERE cardnumber = %s"
                    record1 = (balance,session["cardnumber"])
                    record2 = (data, cardnumber)
                    cur.execute(q1, record1)
                    n = cur.rowcount
                    cur.execute(q2, record2)
                    m = cur.rowcount
                    if n == 1 and m == 1:
                        conn.commit()
                        print("amount deducted")
                        session.pop("cardnumber",None)
                        return redirect(url_for('makeorder'))
                    else:
                        conn.rollback()
                        return render_template("msg.html", msg="Error occurred!!!")
            else:
                return render_template('msg.html', msg="AMount not sufficent in account")
    else:
        return redirect(url_for('autherror'))



@app.route('/makeorder', methods=['GET', 'POST'])
def makeorder():
    if 'email' in session:
        response = placeOrder()
        if response==1:
            return render_template('msg.html', msg="work done")
        else:
            return render_template('msg.html', msg="Error!!!")
    else:
        return redirect(url_for('autherror'))




@app.route('/blog', methods=['GET','POST'])
def blog():
    loggIn = False
    if 'email' in session:
        loggIn=True
    cur=connect_to_database()
    sql="SELECT * FROM blog"
    sql1 = "SELECT DISTINCT b_id FROM blog"
    try:
        cur.execute(sql)
        n=cur.rowcount
        if n>0:
            data=cur.fetchall()
            cur.execute(sql1)
            category = cur.fetchall()
            return render_template('Blog.html', data=data, loggIn=loggIn, category=category)
        else:
            return render_template('Blog.html',msg="no posts",loggIn=loggIn)
    except:
        return render_template('msg.html', msg="something went wrong",loggIn=loggIn)




@app.route('/blgbycategory', methods=['GET','POST'])
def blog1():
    name = request.args.get("name")
    cur=connect_to_database()
    sql = "SELECT * FROM blog WHERE b_id='"+name+"'"
    if cur.execute(sql):
        data = cur.fetchall()
        return render_template('blog1.html',data=data)


@app.route('/readblog', methods=['GET', 'POST'])
def readblog():
    id = request.args.get("id")
    cur = connect_to_database()
    sql = "SELECT * FROM blog WHERE id=%s"
    if cur.execute(sql,id):
        data = cur.fetchone()
        return render_template('readblog.html', data=data)


@app.route('/showFAQ',methods=['GET','POST'])
def showFAQ():
    loggIn = False
    if 'email' in session:
        loggIn=True
    cur = connect_to_database()
    sql = "select * from questions order by dtime desc"
    if(cur.execute(sql)):
        data1 = cur.fetchall()
        sql1 ="select * from answers"
        if(cur.execute(sql1)):
            reply = cur.fetchall()
            return render_template('FAQ.html', data=data1,reply=reply,loggIn=loggIn)
        return render_template('FAQ.html',data=data1,loggIn=loggIn)
    else:
        return render_template('FAQ.html', msg="No Questions Found",loggIn=loggIn)


@app.route('/uploadquestion',methods=['GET','POST'])
def uploadquestion():
    if 'email' in session:
        if request.method=='POST':
            email = session["email"]
            topic = request.form['topic']
            question = request.form['question']
            cur = connect_to_database()
            sql="insert into questions(topic, question, email) values('"+topic+"','"+question+"','"+email+"')"
            if cur.execute(sql):
                flash("question added")
                return redirect(url_for('showFAQ'))
            else:
                flash("something went wrong!")
                return redirect(url_for('showFAQ'))
        else:
            return render_template('msg.html',msg='no post request')
    else:
        return redirect(url_for('login'))


@app.route('/reply',methods=['GET','POST'])
def reply():
    if("email" in session):
        email = session["email"]
        if request.method == 'POST':
            reply = request.form["reply"]
            qid = request.form["qId"]
            cur = connect_to_database()
            sql="insert into answers(qId,answer,email) values('"+qid+"','"+reply+"','"+email+"')"
            if(cur.execute(sql)):
                return redirect(url_for('showFAQ'))
            else:
                return redirect(url_for('showFAq', msg='something went wrong'))
        else:
            return redirect(url_for('autherror'))
    else:
        return redirect(url_for('login'))



@app.route('/changepassword')
def changepassword():
    if 'email' in session:
        email = session["email"]
        otp = str(genrateotp())
        return render_template('changepassword.html', otp=otp)
    else:
        return redirect(url_for('login'))


@app.route('/changepass', methods=['POST'])
def changepass():
    if 'email' in session:
        return render_template('change.html')
    return redirect(url_for('login'))


@app.route('/change', methods=['POST'])
def change():
    if 'email' in session:
        if request.method == 'POST':
            password = request.form['password']
            email = session["email"]
            cur = connect_to_database()
            sql = "SELECT id FROM login WHERE email='"+email+"'"
            if cur.execute(sql):
                data = cur.fetchone()
                write_key(data[0])
                epassword = encrypt_password(password, data[0])
                sql1 = "UPDATE login SET password = %s WHERE email =%s"
                if cur.execute(sql1,(epassword, email)):
                    return redirect(url_for('login'))
                else:
                    return render_template('msg.html', msg="Error Occurred")
    return redirect(url_for('autherror'))


@app.route('/forgotpass')
def forgotpass():
    return render_template('forgotpassword.html')

@app.route('/forgotpassword', methods=['GET', 'POST'])
def forgotpassword():
    if request.method=='POST':
        email = request.form['email']
        session['email'] = email
        otp = genrateotp()
        return render_template('changepassword.html', otp = otp)



@app.route('/deleteaccount')
def deleteaccount():
    if 'email' in session:
        email = session['email']
        cur = connect_to_database()
        q = "SELECT id FROM login WHERE email = '"+email+"'"
        cur.execute(q)
        n= cur.rowcount
        if n ==1:
            data = cur.fetchone()
            id = str(data[0])
            path = 'key/key' + id + '.key'
            q2 = "DELETE FROM login WHERE email = '"+email+"'"
            cur.execute(q2)
            m = cur.rowcount
            if m == 1:
                os.unlink(path)
                return render_template('msg.html', msg="Account Deleted")
            else:
                return redirect(url_for('logout'))
    else:
        return redirect(url_for('autherror'))





@app.route('/about')
def about():
    loggIn =False
    if 'email' in session:
        loggIn = True
    return render_template('About.html', loggIn=loggIn)








@app.route('/myorders', methods = ['GET','POST'])
def myorders():
    if 'email' in session:
        loggIn = True
        email = session["email"]
        cur = connect_to_database()
        sql = "SELECT u_id FROM user_details WHERE email='"+email+"'"
        if cur.execute(sql):
            data = cur.fetchone()
            sql2 = "SELECT * FROM orders WHERE user_id = %s"
            cur.execute(sql2, data[0])
            n = cur.rowcount
            if n>0:
                data1 = cur.fetchall()
                print("data1: ", data1)
                final = list()
                for k in data1:
                    id = k[4]
                    id = id[1:]
                    print(id,k)
                    c = True
                    mylist = list()
                    while c:
                        if (len(id) != 0):
                            print(len(id))
                            x = id[:id.index(',')+1]
                            y = x[0:-1]
                            y = int(y)
                            mylist.append(y)
                            id = id[id.index(','):]
                            print(id)
                            print('length:', len(id))
                            if len(id) == 2:
                                id = ""
                            elif id[0] == ',' and id[-1] == ')' and len(id) ==5:
                                z = id[1:-1]
                                id =""
                                z = int(z)
                                mylist.append(z)
                                print(z)
                        else:
                            c = False
                    print(mylist)
                    myid = tuple(mylist)
                    final.append(myid)
                product_ids = tuple(final)
                print('product ids:', product_ids)
                return render_template("showmyorders.html",loggIn=loggIn,data=data1,Pid=product_ids)
            else:
                return render_template("showmyorders.html", loggIn=loggIn, msg="you have not placed any order")
    else:
        return redirect(url_for('login'))





















if __name__ == '__main__':
    app.run(debug=True)