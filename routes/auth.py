from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)
from extensions import db
from models import User
from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)
auth_bp = Blueprint("auth", __name__)
@auth_bp.route("/")
def home():
    return render_template("index.html")
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        existing_user = User.query.filter_by(
            email=email
        ).first()
        if existing_user:
            flash("Email already exists", "danger")
            return redirect(url_for("auth.register"))
        hashed_password = generate_password_hash(password)
        user = User(
            username=username,
            email=email,
            password=hashed_password,
        )
        db.session.add(user)
        db.session.commit()
        flash("Registration successful", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html")
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(
            email=email
        ).first()
        if user and check_password_hash(
            user.password,
            password,
        ):
            session["user_id"] = user.id
            session["username"] = user.username
            flash("Login successful", "success")
            return redirect(url_for("notes.dashboard"))
        flash("Invalid email or password", "danger")
    return render_template("login.html")
@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Logout successful", "info")
    return redirect(url_for("auth.login"))