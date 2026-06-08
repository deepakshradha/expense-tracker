from flask import Flask, render_template, request, redirect, url_for, flash, session
from database.db import init_db, seed_db, create_user, get_user_by_email, get_user_by_id, get_user_total_spending, get_user_spending_by_category, get_recent_expenses, get_user_transaction_count
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'dev-key-for-spendly'


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        flash("You are already logged in", "info")
        return redirect(url_for("profile"))

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not name or not email or not password:
            flash("All fields are required", "error")
            return redirect(url_for("register"))

        hashed_pw = generate_password_hash(password)
        user_id = create_user(name, email, hashed_pw)

        if user_id is None:
            flash("An account with this email already exists", "error")
            return redirect(url_for("register"))

        flash("Account created successfully! Please sign in", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        flash("You are already logged in", "info")
        return redirect(url_for("profile"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("All fields are required", "error")
            return redirect(url_for("login"))

        user = get_user_by_email(email)
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for("profile"))

        flash("Invalid email or password", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.pop('user_id', None)
    flash("You have been logged out successfully", "success")
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to view your profile", "info")
        return redirect(url_for("login"))

    user = get_user_by_id(user_id)
    total_spending = get_user_total_spending(user_id)
    category_spending = get_user_spending_by_category(user_id)
    recent_expenses = get_recent_expenses(user_id)
    transaction_count = get_user_transaction_count(user_id)

    # Determine top category for summary stats
    top_category = category_spending[0]['category'] if category_spending else "N/A"

    return render_template(
        "profile.html",
        user=user,
        total_spending=total_spending,
        category_spending=category_spending,
        recent_expenses=recent_expenses,
        transaction_count=transaction_count,
        top_category=top_category
    )




@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    with app.app_context():
        init_db()
        seed_db()
    app.run(debug=True, port=5001)
