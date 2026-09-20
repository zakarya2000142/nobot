from flask import Flask, render_template, request, redirect, session
from datetime import datetime, timedelta
import database

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "nobat_secret_key_2026"
database.init_db()

def current_business():
    return session.get("business_id")

# ---------- صفحه اصلی ----------

@app.route("/")
def index():
    return render_template("index.html")

# ---------- ثبت‌نام کسب‌وکار ----------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        owner_name = request.form["owner_name"]
        phone = request.form["phone"]
        address = request.form.get("address", "")
        username = request.form["username"]
        password = request.form["password"]

        if database.get_business_by_username(username):
            return render_template("register.html", error="این نام کاربری قبلاً گرفته شده")

        if database.add_business(name, owner_name, phone, address, username, password):
            return redirect("/login")
        return render_template("register.html", error="خطا در ثبت‌نام")
    return render_template("register.html")

# ---------- ورود ----------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        business = database.get_business(username, password)
        if business:
            session["business_id"] = business["id"]
            session["business_name"] = business["name"]
            return redirect("/dashboard")
        return render_template("login.html", error="نام کاربری یا رمز اشتباهه")
    return render_template("login.html")

# ---------- فراموشی ----------

@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        phone = request.form["phone"]
        conn = database.get_connection()
        business = conn.execute("SELECT * FROM businesses WHERE phone = ?", (phone,)).fetchone()
        conn.close()

        if not business:
            return render_template("forgot.html", error="این شماره ثبت نشده")

        return render_template("forgot.html", success="نام کاربری شما: " + business["username"])

    return render_template("forgot.html")

# ---------- خروج ----------

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------- داشبورد ----------

@app.route("/dashboard")
def dashboard():
    if not current_business():
        return redirect("/login")
    bid = current_business()
    business = database.get_business_by_id(bid)
    today_appointments = database.get_today_appointments(bid)
    services = database.get_services(bid)

    return render_template("dashboard.html",
                           business=business,
                           today_appointments=today_appointments,
                           services=services)

# ---------- خدمات ----------

@app.route("/services")
def services():
    if not current_business():
        return redirect("/login")
    bid = current_business()
    return render_template("services.html", services=database.get_services(bid))

@app.route("/add_service", methods=["POST"])
def add_service():
    if not current_business():
        return redirect("/login")
    bid = current_business()
    name = request.form["name"]
    price = int(request.form["price"])
    duration = int(request.form["duration"])
    database.add_service(bid, name, price, duration)
    return redirect("/services")

@app.route("/delete_service/<int:service_id>")
def delete_service(service_id):
    if not current_business():
        return redirect("/login")
    database.delete_service(current_business(), service_id)
    return redirect("/services")

# ---------- ساعات کاری ----------

@app.route("/working_hours", methods=["GET", "POST"])
def working_hours():
    if not current_business():
        return redirect("/login")
    bid = current_business()

    if request.method == "POST":
        for day in range(7):
            start = request.form.get(f"start_{day}", "09:00")
            end = request.form.get(f"end_{day}", "21:00")
            is_closed = 1 if request.form.get(f"closed_{day}") else 0
            database.set_working_hours(bid, day, start, end, is_closed)
        return redirect("/working_hours")

    return render_template("working_hours.html", hours=database.get_working_hours(bid))

# ---------- نوبت‌ها ----------

@app.route("/appointments")
def appointments():
    if not current_business():
        return redirect("/login")
    bid = current_business()
    return render_template("appointments.html", appointments=database.get_appointments(bid))

@app.route("/update_appointment/<int:appointment_id>/<status>")
def update_appointment(appointment_id, status):
    if not current_business():
        return redirect("/login")
    database.update_appointment_status(appointment_id, status)
    return redirect("/appointments")

# ---------- صفحه مشتری ----------

@app.route("/customer")
def customer():
    businesses = database.get_all_businesses()
    return render_template("customer.html", businesses=businesses)

@app.route("/book/<int:business_id>", methods=["GET", "POST"])
def book(business_id):
    business = database.get_business_by_id(business_id)
    services = database.get_services(business_id)

    if request.method == "POST":
        service_id = int(request.form["service_id"])
        customer_name = request.form["customer_name"]
        customer_phone = request.form["customer_phone"]
        date = request.form["date"]
        time = request.form["time"]

        database.add_appointment(business_id, service_id, customer_name, customer_phone, date, time)
        return render_template("book.html", business=business, services=services, success="نوبت شما ثبت شد!")

    return render_template("book.html", business=business, services=services)

# ---------- ادمین ----------

@app.route("/admin")
def admin():
    businesses = database.get_all_businesses()
    return render_template("admin.html", businesses=businesses)

if __name__ == "__main__":
    app.run()
