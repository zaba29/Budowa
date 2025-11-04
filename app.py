import os
import sqlite3
from functools import wraps
from typing import Dict, List

from flask import (
    Flask,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "super-secret-key"),
        DATABASE=os.path.join(app.root_path, "expenses.db"),
        USERNAME=os.environ.get("APP_USERNAME", "lukasz"),
        PASSWORD=os.environ.get("APP_PASSWORD", "lukasz29"),
    )

    os.makedirs(app.root_path, exist_ok=True)

    def get_db() -> sqlite3.Connection:
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
        return g.db

    def close_db(_: Exception | None) -> None:
        db = g.pop("db", None)
        if db is not None:
            db.close()

    def init_db() -> None:
        db = get_db()
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expense_date TEXT NOT NULL,
                merchant TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                notes TEXT,
                bank TEXT,
                description TEXT,
                expense_type TEXT NOT NULL
            )
            """
        )
        db.commit()

    @app.before_request
    def before_request() -> None:
        init_db()

    @app.teardown_appcontext
    def teardown_db(exception: Exception | None) -> None:
        close_db(exception)

    def login_required(view):
        @wraps(view)
        def wrapped_view(**kwargs):
            if not session.get("logged_in"):
                return redirect(url_for("login"))
            return view(**kwargs)

        return wrapped_view

    def parse_amount(raw_value: str) -> float:
        cleaned = (raw_value or "").replace(" ", "").replace(",", ".")
        try:
            return float(cleaned)
        except ValueError:
            raise ValueError("Nieprawidłowa kwota. Użyj cyfr i kropki lub przecinka.")

    def fetch_category_totals(db: sqlite3.Connection) -> Dict[str, float]:
        results = db.execute(
            "SELECT category, SUM(amount) as total FROM expenses GROUP BY category"
        ).fetchall()
        return {row["category"]: row["total"] for row in results}

    def fetch_type_totals(db: sqlite3.Connection) -> Dict[str, float]:
        results = db.execute(
            "SELECT expense_type, SUM(amount) as total FROM expenses GROUP BY expense_type"
        ).fetchall()
        return {row["expense_type"]: row["total"] for row in results}

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            if (
                username == app.config["USERNAME"]
                and password == app.config["PASSWORD"]
            ):
                session["logged_in"] = True
                return redirect(url_for("index"))
            flash("Niepoprawny login lub hasło", "error")
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        flash("Zostałeś poprawnie wylogowany.", "success")
        return redirect(url_for("login"))

    @app.route("/")
    @login_required
    def index():
        db = get_db()
        expenses = db.execute(
            "SELECT * FROM expenses ORDER BY expense_date DESC, id DESC"
        ).fetchall()
        category_totals = fetch_category_totals(db)
        type_totals = fetch_type_totals(db)
        total_cost = sum(row["amount"] for row in expenses)

        categories: List[str] = [f"ETAP {i}" for i in range(6)]
        expense_types = ["Materiały", "Zaliczka", "Zaliczki", "Inne"]

        return render_template(
            "index.html",
            expenses=expenses,
            categories=categories,
            expense_types=expense_types,
            category_totals=category_totals,
            type_totals=type_totals,
            total_cost=total_cost,
        )

    @app.post("/expenses")
    @login_required
    def add_expense():
        expense_date = request.form.get("expense_date", "").strip()
        merchant = request.form.get("merchant", "").strip()
        amount_raw = request.form.get("amount", "")
        category = request.form.get("category", "").strip()
        notes = request.form.get("notes", "").strip()
        bank = request.form.get("bank", "").strip()
        description = request.form.get("description", "").strip()
        expense_type = request.form.get("expense_type", "").strip()

        try:
            amount = parse_amount(amount_raw)
        except ValueError as exc:
            flash(str(exc), "error")
            return redirect(url_for("index"))

        if not expense_date or not merchant or not category or not expense_type:
            flash("Proszę uzupełnić wymagane pola.", "error")
            return redirect(url_for("index"))

        db = get_db()
        db.execute(
            """
            INSERT INTO expenses (
                expense_date, merchant, amount, category, notes, bank, description, expense_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                expense_date,
                merchant,
                amount,
                category,
                notes,
                bank,
                description,
                expense_type,
            ),
        )
        db.commit()
        flash("Wydatek został dodany.", "success")
        return redirect(url_for("index"))

    @app.post("/expenses/<int:expense_id>/delete")
    @login_required
    def delete_expense(expense_id: int):
        db = get_db()
        db.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        db.commit()
        flash("Wpis został usunięty.", "success")
        return redirect(url_for("index"))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
