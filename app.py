import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, g, abort
from database.db import init_db, seed_db, create_user, get_user_by_email, get_user_by_id, get_user_total_spending, get_user_spending_by_category, get_recent_expenses, get_user_transaction_count, add_expense as db_add_expense, get_expense_by_id as db_get_expense_by_id, update_expense as db_update_expense
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-for-spendly')

# Shared allowlist — must stay in sync with the DB CHECK constraint
ALLOWED_CATEGORIES = ('Food', 'Transport', 'Bills', 'Health', 'Entertainment', 'Shopping', 'Other')


@app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


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

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    user = get_user_by_id(user_id)
    total_spending = get_user_total_spending(user_id, start_date, end_date)
    category_spending = get_user_spending_by_category(user_id, start_date, end_date)
    recent_expenses = get_recent_expenses(user_id, start_date=start_date, end_date=end_date)
    transaction_count = get_user_transaction_count(user_id, start_date, end_date)

    # Determine top category for summary stats
    top_category = category_spending[0]['category'] if category_spending else "N/A"

    return render_template(
        "profile.html",
        user=user,
        total_spending=total_spending,
        category_spending=category_spending,
        recent_expenses=recent_expenses,
        transaction_count=transaction_count,
        top_category=top_category,
        start_date=start_date,
        end_date=end_date
    )


@app.route("/expenses/add", methods=["GET", "POST"])
def add_expense():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to add an expense", "info")
        return redirect(url_for("login"))

    if request.method == "POST":
        amount_str = request.form.get("amount")
        category = request.form.get("category")
        date_str = request.form.get("date")
        description = request.form.get("description")

        if not amount_str or not category or not date_str:
            flash("Amount, category, and date are required", "error")
            return redirect(url_for("add_expense"))

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except ValueError:
            flash("Please enter a valid positive amount", "error")
            return redirect(url_for("add_expense"))

        # Validation for allowed categories is partially handled by HTML select
        # but we should check here too just in case of direct POST requests.
        if category not in ALLOWED_CATEGORIES:
            flash("Invalid category selected", "error")
            return redirect(url_for("add_expense"))

        # Ensure date is valid (basic check, since it's from input type="date")
        if not date_str:
            flash("Please provide a valid date", "error")
            return redirect(url_for("add_expense"))

        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD", "error")
            return redirect(url_for("add_expense"))

        try:
            db_add_expense(user_id, amount, category, date_str, description)
            flash("Expense added successfully!", "success")
            return redirect(url_for("profile"))
        except Exception as e:
            flash(f"An error occurred while saving: {str(e)}", "error")
            return redirect(url_for("add_expense"))

    # GET request
    today = date.today().isoformat()
    return render_template("add_expense.html", today=today)


@app.route("/expenses/<int:id>/edit", methods=["GET", "POST"])
def edit_expense(id):  # noqa: A002 — 'id' is the URL param name; use expense_id internally
    expense_id = id  # rename to avoid shadowing Python built-in in the rest of the function
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to edit an expense", "info")
        return redirect(url_for("login"))

    expense = db_get_expense_by_id(expense_id)
    if expense is None:
        abort(404)
    if expense["user_id"] != user_id:
        abort(403)

    if request.method == "POST":
        amount_str = request.form.get("amount")
        category = request.form.get("category")
        date_str = request.form.get("date")
        description = request.form.get("description")

        if not amount_str or not category or not date_str:
            flash("Amount, category, and date are required", "error")
            return redirect(url_for("edit_expense", id=expense_id))

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except ValueError:
            flash("Please enter a valid positive amount", "error")
            return redirect(url_for("edit_expense", id=expense_id))

        if category not in ALLOWED_CATEGORIES:
            flash("Invalid category selected", "error")
            return redirect(url_for("edit_expense", id=expense_id))

        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD", "error")
            return redirect(url_for("edit_expense", id=expense_id))

        try:
            db_update_expense(expense_id, amount, category, date_str, description, user_id)
            flash("Expense updated successfully!", "success")
            return redirect(url_for("profile"))
        except Exception as e:
            flash(f"An error occurred while saving: {str(e)}", "error")
            return redirect(url_for("edit_expense", id=expense_id))

    return render_template("edit_expense.html", expense=expense)


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    with app.app_context():
        init_db()
        seed_db()
    app.run(debug=True, port=5001)
