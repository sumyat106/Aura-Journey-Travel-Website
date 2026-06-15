from flask import Flask, render_template, request, redirect, session, flash, url_for
from db_config import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
from flask_compress import Compress
from flask import Flask
import mysql.connector
import os
from werkzeug.utils import secure_filename
# import sqlite3

# def get_db():
#     conn = sqlite3.connect("travel_db.db")   # မင်း project သုံးတဲ့ DB file name ကိုပြင်
#     conn.row_factory = sqlite3.Row
#     return conn
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",   # XAMPP password မရှိရင် blank
    database="travel_db"
)

cur = conn.cursor()
app = Flask(__name__)
Compress(app)
app.secret_key = "gihut_secret_very_long_for_security_2026"
from werkzeug.security import generate_password_hash, check_password_hash

# ==== HOME PAGE (Database ကနေ Top Attractions ပါ ဆွဲထုတ်မယ်) ====
# app.py
@app.route("/")
def home():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM top_destinations LIMIT 3")
    cities = cursor.fetchall()
    
    # tags က NULL ဖြစ်နေရင် "" (empty string) လို့ သတ်မှတ်ပေးဖို့ IFNULL သုံးမယ်
    cursor.execute("""
        SELECT id, name, description, img, rating, reviews, 
               IFNULL(tags, '') as tags 
        FROM top_attractions LIMIT 2
    """)
    attractions = cursor.fetchall()
    
    conn.close()
    return render_template("index.html", cities=cities, attractions=attractions)

# ==== ADMIN: UPDATE TOP DESTINATION ====
@app.route("/admin/update_top_destination/<int:id>", methods=["POST"])
def update_top_destination(id):
    name = request.form.get("name")
    description = request.form.get("description")
    img = request.form.get("img")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # popular=%s ဆိုတာကို ဖယ်လိုက်ပါ
    cursor.execute("""
        UPDATE top_destinations 
        SET name=%s, description=%s, img=%s 
        WHERE id=%s
    """, (name, description, img, id))
    
    conn.commit()
    conn.close()
    return redirect("/admin_dashboard")

# ==== ADMIN: UPDATE TOP ATTRACTION ====
@app.route("/admin/update_attraction/<int:id>", methods=["POST"])
def update_attraction(id):
    if session.get("role") != "admin": return redirect("/login")
    
    name = request.form.get('name')
    desc = request.form.get('description')
    img = request.form.get('img')
    tags = request.form.get('tags')
    rating = request.form.get('rating')
    reviews = request.form.get('reviews')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE top_attractions 
        SET name=%s, description=%s, img=%s, tags=%s, rating=%s, reviews=%s 
        WHERE id=%s
    """, (name, desc, img, tags, rating, reviews, id))
    
    conn.commit()
    conn.close()
    flash("Top Attraction Updated!", "success")
    return redirect("/admin_dashboard")
# ==== CITY DETAIL ====
@app.route("/city/<int:id>")
def city_detail(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM cities WHERE id=%s", (id,))
    city = cursor.fetchone()

    cursor.execute("SELECT * FROM attractions WHERE city_id=%s", (id,))
    attractions = cursor.fetchall()

    cursor.execute("SELECT * FROM hotels WHERE city_id=%s", (id,))
    hotels = cursor.fetchall()

    cursor.execute("""
        SELECT buses.*, c1.name AS from_city, c2.name AS to_city
        FROM buses
        JOIN cities c1 ON buses.city_from=c1.id
        JOIN cities c2 ON buses.city_to=c2.id
        WHERE buses.city_from=%s
    """, (id,))
    buses = cursor.fetchall()
    conn.close()

    return render_template("city_detail.html", city=city, attractions=attractions, hotels=hotels, buses=buses, title=f"{city['name']} - ခရီးသွားအချက်အလက်များ")

#Admin Dashboard rough
# Admin Dashboard function ကို အောက်ပါအတိုင်း အစားထိုးပါ
import os

@app.route("/admin_dashboard")
def admin_dashboard():
    if "user_id" not in session or session.get("role") != "admin":
        flash("Admin သာ ဝင်ရောက်ခွင့်ရှိပါသည်။", "warning")
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM top_destinations")
    top_destinations = cursor.fetchall()
    cursor.execute("SELECT * FROM top_attractions")
    all_top_attractions = cursor.fetchall()

    # ပုံမှန်ရှိပြီးသား Database ဆွဲထုတ်တဲ့ code များ...
    cursor.execute("SELECT COUNT(id) as total_users FROM users WHERE role != 'admin'")
    user_count = cursor.fetchone()['total_users']
    cursor.execute("SELECT username, email, phone FROM users WHERE role != 'admin'")
    all_users = cursor.fetchall()
    cursor.execute("SELECT * FROM packages")
    all_packages = cursor.fetchall()
    cursor.execute("SELECT b.*, p.name AS package_name FROM bookings b JOIN packages p ON b.tour_id = p.id")
    all_bookings = cursor.fetchall()

    image_dir = os.path.join('static', 'images')
    if os.path.exists(image_dir):
        available_images = [f for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    else:
        available_images = []

    conn.close()
    
    return render_template("admin_dashboard.html", 
                           user_count=user_count, 
                           users_list=all_users,
                           booking_count=len(all_bookings),
                           bookings_list=all_bookings,
                           packages_list=all_packages,
                           top_destinations=top_destinations,
                           top_attractions_list=all_top_attractions,
                           available_images=available_images) # HTML ဆီ ပုံစာရင်း ပို့ပေးမယ်

# ///////////Accept Booking///////////
@app.route("/admin/accept_booking/<int:id>")
def accept_booking(id):
    if session.get("role") != "admin": return redirect("/login")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE bookings SET status='confirmed' WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    flash("Booking confirmed successfully!", "success")
    return redirect("/admin_dashboard")
# ==== REGISTER ====
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        raw_password = request.form["password"]
        phone = request.form.get("phone")


        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        if cursor.fetchone():
            conn.close()
            flash("Email တူနေပါသည်။ ပြန်ကြိုးစားပါ။", "danger")
            return redirect("/register")

        # Secure password storage!
        hashed_password = generate_password_hash(raw_password)
        cursor.execute("INSERT INTO users (username, email, password, phone) VALUES (%s,%s,%s,%s)", (username, email, hashed_password, phone))
        conn.commit()
        conn.close()
        flash("Regestration successful!", "success")
        return redirect("/login")
    return render_template("register.html", title="စာရင်းသွင်းခြင်း")
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        # ၁။ Email ကို database မှာ အရင်ရှာမယ်
        cur.execute("SELECT id, username, role, password FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        conn.close()

        # ၂။ User ရှိမရှိ အရင်စစ်မယ်
        if user:
            # ၃။ ရိုက်လိုက်တဲ့ password နဲ့ DB ထဲက hash လုပ်ထားတဲ့ password တူမတူ စစ်မယ်
            if check_password_hash(user["password"], password):
                # Password မှန်မှ Session ထဲ ထည့်မယ်
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                session["role"] = user["role"]

                # Admin ဆိုရင် Admin Dashboard၊ ရိုးရိုး User ဆိုရင် Home ကို ပို့မယ်
                if user["role"] == "admin":
                    return redirect("/admin_dashboard")
                else:
                    return redirect("/")
            else:
                # Password မှားရင်
                flash("Password မှားယွင်းနေပါသည်။", "danger")
        else:
            # Email မရှိရင်
            flash("ဤ Email ဖြင့် အကောင့်ဖွင့်ထားခြင်း မရှိပါ။", "danger")

    return render_template("login.html")

# ==== ADMIN: ADD PACKAGE ====
# ပုံတွေသိမ်းမယ့် Folder (static/images ထဲမှာ ဖြစ်ရပါမယ်)
# folder လမ်းကြောင်း သတ်မှတ်မယ်
UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# အကယ်၍ static/images folder မရှိသေးရင် အလိုအလျောက် ဆောက်ပေးပါ
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/admin/add_package", methods=["POST"])
def add_package():
    if session.get("role") != "admin": return redirect("/login")
    
    # Text Data များယူခြင်း
    name = request.form.get('name')
    price = request.form.get('price')
    city = request.form.get('city')
    hotel = request.form.get('hotel_name')
    trans = request.form.get('transport')
    people = request.form.get('people_count')
    duration = request.form.get('duration')
    breakfast = request.form.get('breakfast')
    desc = request.form.get('description')
    details = request.form.get('details_description')

    # Image Filenames (Text) များကို Form ထဲကနေ တိုက်ရိုက်ယူခြင်း
    # HTML ထဲမှာ name="img1", name="img2" စသဖြင့် ပေးထားတာနဲ့ ကိုက်ရပါမယ်
    img1 = request.form.get('img1') 
    img2 = request.form.get('img2')
    img3 = request.form.get('img3')
    img4 = request.form.get('img4')

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Database ထဲက Column အစဉ်လိုက်အတိုင်း ထည့်ပါမယ်
    sql = """INSERT INTO packages 
             (name, price, city, hotel_name, transport, people_count, duration, includes_breakfast, description, details_description, img_main, img2, img3, img4) 
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    
    cursor.execute(sql, (name, price, city, hotel, trans, people, duration, breakfast, desc, details, 
                         img1, img2, img3, img4)) # နေရာမှန်အောင် ပြန်စီထားပါတယ်
    
    conn.commit()
    conn.close()
    
    flash("Package added successfully with image names!", "success")
    return redirect("/admin_dashboard")
# ==== ADMIN: UPDATE PACKAGE ====
@app.route("/admin/update_package/<int:id>", methods=["POST"])
def update_package(id):
    if session.get("role") != "admin": return redirect("/login")
    
    # Form ထဲက data အားလုံးကို ယူခြင်း
    name = request.form.get('name')
    price = request.form.get('price')
    city = request.form.get('city')
    hotel = request.form.get('hotel_name')
    trans = request.form.get('transport')
    people = request.form.get('people_count')
    duration = request.form.get('duration')
    breakfast = request.form.get('breakfast')
    desc = request.form.get('description')
    details = request.form.get('details_description')
    img1 = request.form.get('img1')
    img2 = request.form.get('img2')
    img3 = request.form.get('img3')
    img4 = request.form.get('img4')

    conn = get_db_connection()
    cursor = conn.cursor()
    
    sql = """UPDATE packages SET 
             name=%s, price=%s, city=%s, hotel_name=%s, transport=%s, 
             people_count=%s, duration=%s, includes_breakfast=%s, 
             description=%s, details_description=%s, 
             img_main=%s, img2=%s, img3=%s, img4=%s 
             WHERE id=%s"""
             
    cursor.execute(sql, (name, price, city, hotel, trans, people, duration, breakfast, desc, details, img1, img2, img3, img4, id))
    
    conn.commit()
    conn.close()
    flash("Package Updated Successfully!", "info")
    return redirect("/admin_dashboard")
# ==== ADMIN: DELETE PACKAGE ====
@app.route("/admin/delete_package/<int:id>")
def delete_package(id):
    if session.get("role") != "admin": return redirect("/login")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # ၁။ အရင်ဆုံး ဒီ tour_id နဲ့ ပတ်သက်တဲ့ reviews တွေကို အရင်ဖျက်ပါ
        cursor.execute("DELETE FROM reviews WHERE tour_id=%s", (id,))
        
        # ၂။ ပြီးမှ Package ကို ဖျက်ပါ
        cursor.execute("DELETE FROM packages WHERE id=%s", (id,))
        
        conn.commit()
        flash("Package and related reviews deleted successfully!", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error: {str(e)}", "danger")
    finally:
        conn.close()
        
    return redirect("/admin_dashboard")
# ==== SEARCH TOURS (Database ကနေ Package အားလုံးကို ဆွဲထုတ်မယ်) ====
@app.route("/search_tours")
def search_tours():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # Database ထဲက packages table ထဲက အကုန်ယူမယ်
    cursor.execute("SELECT * FROM packages")
    all_packages = cursor.fetchall()
    conn.close()
    # packages ဆိုတဲ့ variable နဲ့ HTML ဆီ ပို့ပေးလိုက်ပါတယ်
    return render_template("search_tours.html", packages=all_packages)

# ==== TOUR DETAILS (ID အလိုက် အသေးစိတ်ကြည့်မယ်) ====
# ==== TOUR DETAILS (ID အလိုက် အသေးစိတ်ကြည့်မယ် + Reviews ပါပြမယ်) ====
@app.route("/tour_details/<int:tour_id>")
def tour_details(tour_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # ၁. Tour info
    cursor.execute("SELECT * FROM packages WHERE id=%s", (tour_id,))
    tour = cursor.fetchone()

    # ၂. Reviews (user table နဲ့ join ပြီး username ယူမယ်)
    cursor.execute("""
        SELECT r.comment, r.created_at, u.username 
        FROM reviews r 
        JOIN users u ON r.user_id = u.id 
        WHERE r.tour_id = %s 
        ORDER BY r.created_at DESC
    """, (tour_id,))
    reviews = cursor.fetchall()
    
    conn.close()
    return render_template("tour_details.html", tour=tour, reviews=reviews)

# ==== USER DASHBOARD ====
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session: return redirect("/login")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # p.price * b.guests ကို total_price အနေနဲ့ တွက်ထုတ်ပေးလိုက်ပါတယ်
    cursor.execute("""
        SELECT b.id, b.tour_id, p.name AS package_name, b.travel_date, b.status, b.guests, 
               (p.price * b.guests) AS total_price
        FROM bookings b
        JOIN packages p ON b.tour_id = p.id
        WHERE b.user_id = %s
        ORDER BY b.id DESC
    """, (session["user_id"],))
    
    bookings = cursor.fetchall()
    conn.close()
    return render_template("user_dashboard.html", bookings=bookings)
# ///////////Booking//////////////
# အရင်က tour_booking_post လို့ ရှိနေရင် tour_booking လို့ ပြန်ပြင်ပါ
@app.route("/tour_booking/<int:tour_id>", methods=["GET", "POST"])
def tour_booking(tour_id):
    if "user_id" not in session: 
        flash("Login လုပ်ရန်လိုအပ်ပါသည်။", "warning")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        travel_date = request.form.get("travel_date")
        guests = request.form.get("guests")

        cursor.execute("""
            INSERT INTO bookings (user_id, tour_id, full_name, email, phone, travel_date, guests, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending')
        """, (session["user_id"], tour_id, full_name, email, phone, travel_date, guests))
        conn.commit()
        conn.close()
        
        return redirect(url_for("booking_success"))

    # GET method အတွက် package အချက်အလက်ယူခြင်း
    cursor.execute("SELECT * FROM packages WHERE id=%s", (tour_id,))
    tour = cursor.fetchone()
    conn.close()
    return render_template("booking.html", tour=tour)

@app.route("/booking_success")
def booking_success():
    return render_template("booking_success.html")


# =========== LOGOUT ==========
@app.route("/logout")
def logout():
    session.clear()
    flash("Logout ဖြစ်ပြီးပါပြီ။", "info")
    return redirect("/")

# =========== ERROR HANDLING ==========
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html", title="Error 404"), 404

#=============Search Package name==================
@app.route("/search")
def search():
    query = request.args.get('q', '').strip()
    
    if not query:
        return redirect(url_for('home'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Package name နဲ့ အတိအကျတူတာကို အရင်ရှာမယ် (Case-insensitive ဖြစ်အောင် LIKE သုံးထားပါတယ်)
    # ရှာတဲ့အခါ %query% မသုံးဘဲ query အတိအကျတူတာကို ဦးစားပေးရှာပါမယ်
    cursor.execute("SELECT id FROM packages WHERE name LIKE %s LIMIT 1", (query,))
    result = cursor.fetchone()
    conn.close()

    if result:
        # တူတာရှိရင် အဲ့ဒီ tour ရဲ့ details page ကို သွားမယ်
        return redirect(url_for('tour_details', tour_id=result['id']))
    else:
        # မရှိရင် Search Tours (Package အားလုံးရှိတဲ့နေရာ) ကို ပြန်ပို့ပြီး flash message ပြမယ်
        flash(f"'{query}' နှင့် ပတ်သက်သော Package မတွေ့ရှိပါ။", "info")
        return redirect(url_for('search_tours'))
# //////////////Cancel///////////
# /////////// Cancel Booking ///////////
@app.route("/admin/cancel_booking/<int:id>")
def cancel_booking(id):
    if session.get("role") != "admin": 
        return redirect("/login")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    # Status ကို 'cancelled' ဟု ပြောင်းလဲခြင်း
    cursor.execute("UPDATE bookings SET status='cancelled' WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    
    flash("Booking has been cancelled.", "warning")
    return redirect("/admin_dashboard")
@app.route("/change_password", methods=["POST"])
def change_password():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    new_password = request.form.get("new_password")
    hashed_password = generate_password_hash(new_password)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password=%s WHERE id=%s", (hashed_password, session["user_id"]))
    conn.commit()
    conn.close()
    
    flash("Password ပြောင်းလဲမှု အောင်မြင်ပါသည်။", "success")
    return redirect(url_for("dashboard"))  
@app.route("/submit_review/<int:tour_id>", methods=["POST"])
def submit_review(tour_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    comment = request.form.get("comment")
    user_id = session["user_id"]

    if comment:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Table structure နဲ့ column နာမည် (tour_id, user_id, comment) မှန်ပါစေ
            cursor.execute("INSERT INTO reviews (tour_id, user_id, comment) VALUES (%s, %s, %s)", 
                           (tour_id, user_id, comment))
            conn.commit()
            flash("Review submitted!", "success")
        except Exception as e:
            print(f"Error: {e}")
            conn.rollback()
        finally:
            conn.close()

    # အရေးကြီးဆုံးအပိုင်း: Review ပေးပြီးရင် အဲဒီ Tour ရဲ့ Details page ကို ပြန်ပို့ပေးရပါမယ်
    return redirect(url_for('tour_details', tour_id=tour_id))
if __name__ == "__main__":
    app.run(debug=True)