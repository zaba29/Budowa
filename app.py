import os
import sqlite3
from functools import wraps
from typing import Dict, List

from flask import (
    Flask,
    Response,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

EXPENSE_TYPES: List[str] = ["Materialy", "Zaliczka", "Usluga", "Robocizna", "Inne"]
CATEGORIES: List[str] = [f"ETAP {i}" for i in range(6)]
ROLE_LABELS: Dict[str, str] = {"admin": "Admin", "user": "Użytkownik", "guest": "Gość"}


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

    def ensure_schema() -> None:
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
                expense_type TEXT NOT NULL,
                display_order INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        expense_columns = {
            row["name"] for row in db.execute("PRAGMA table_info(expenses)").fetchall()
        }
        if "display_order" not in expense_columns:
            db.execute(
                "ALTER TABLE expenses ADD COLUMN display_order INTEGER NOT NULL DEFAULT 0"
            )
            db.execute("UPDATE expenses SET display_order = id WHERE display_order = 0")

        db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                can_add INTEGER NOT NULL DEFAULT 1,
                can_edit INTEGER NOT NULL DEFAULT 1,
                can_delete INTEGER NOT NULL DEFAULT 1,
                can_view_reports INTEGER NOT NULL DEFAULT 1
            )
            """
        )

        ensure_default_admin(db)
        db.commit()

    def ensure_default_admin(db: sqlite3.Connection) -> None:
        existing = db.execute(
            "SELECT id FROM users WHERE username = ?", (app.config["USERNAME"],)
        ).fetchone()
        if existing is None:
            db.execute(
                """
                INSERT INTO users (
                    username, password, role, can_add, can_edit, can_delete, can_view_reports
                ) VALUES (?, ?, 'admin', 1, 1, 1, 1)
                """,
                (app.config["USERNAME"], app.config["PASSWORD"]),
            )

    @app.before_request
    def before_request() -> None:
        ensure_schema()
        g.user = None
        g.permissions = {}
        user_id = session.get("user_id")
        if user_id is not None:
            user = (
                get_db()
                .execute("SELECT * FROM users WHERE id = ?", (user_id,))
                .fetchone()
            )
            if user is not None:
                g.user = user
                g.permissions = {
                    "can_add": bool(user["can_add"]),
                    "can_edit": bool(user["can_edit"]),
                    "can_delete": bool(user["can_delete"]),
                    "can_view_reports": bool(user["can_view_reports"]),
                }
            else:
                session.clear()

    @app.teardown_appcontext
    def teardown_db(exception: Exception | None) -> None:
        close_db(exception)

    def login_required(view):
        @wraps(view)
        def wrapped_view(**kwargs):
            if g.get("user") is None:
                return redirect(url_for("login"))
            return view(**kwargs)

        return wrapped_view

    def permission_required(permission: str):
        def decorator(view):
            @wraps(view)
            def wrapped_view(**kwargs):
                if g.get("user") is None:
                    return redirect(url_for("login"))
                if not g.permissions.get(permission, False):
                    if request.accept_mimetypes.accept_json:
                        return jsonify({"error": "Brak uprawnień."}), 403
                    flash("Brak uprawnień do wykonania tej operacji.", "error")
                    return redirect(url_for("index"))
                return view(**kwargs)

            return wrapped_view

        return decorator

    def admin_required(view):
        @wraps(view)
        def wrapped_view(**kwargs):
            if g.get("user") is None:
                return redirect(url_for("login"))
            if g.user["role"] != "admin":
                flash("Ta sekcja wymaga uprawnień administratora.", "error")
                return redirect(url_for("index"))
            return view(**kwargs)

        return wrapped_view

    def parse_amount(raw_value: str) -> float:
        cleaned = (raw_value or "").replace(" ", "").replace(",", ".")
        try:
            return float(cleaned)
        except ValueError as exc:
            raise ValueError(
                "Nieprawidłowa kwota. Użyj cyfr oraz kropki lub przecinka."
            ) from exc

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

    def fetch_monthly_totals(db: sqlite3.Connection) -> List[sqlite3.Row]:
        return db.execute(
            """
            SELECT substr(expense_date, 1, 7) AS month, SUM(amount) AS total
            FROM expenses
            GROUP BY substr(expense_date, 1, 7)
            ORDER BY month
            """
        ).fetchall()

    @app.context_processor
    def inject_globals() -> Dict[str, object]:
        return {
            "current_user": g.get("user"),
            "permissions": g.get("permissions", {}),
            "role_labels": ROLE_LABELS,
            "expense_types": EXPENSE_TYPES,
            "categories": CATEGORIES,
        }

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            user = (
                get_db()
                .execute("SELECT * FROM users WHERE username = ?", (username,))
                .fetchone()
            )
            if user and user["password"] == password:
                session.clear()
                session["logged_in"] = True
                session["user_id"] = user["id"]
                flash("Zalogowano pomyślnie.", "success")
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
        sort_map = {
            "display_order": "display_order",
            "date": "expense_date",
            "amount": "amount",
            "category": "category",
            "type": "expense_type",
            "merchant": "merchant",
        }
        requested_sort = request.args.get("sort", "display_order")
        sort_column = sort_map.get(requested_sort, "display_order")
        direction = request.args.get("direction", "asc").lower()
        if sort_column == "display_order":
            direction = "asc"
        elif direction not in {"asc", "desc"}:
            direction = "asc"
        expenses_rows = db.execute(
            f"SELECT * FROM expenses ORDER BY {sort_column} {direction.upper()}, id ASC"
        ).fetchall()
        expenses = [dict(row) for row in expenses_rows]

        category_totals = fetch_category_totals(db)
        type_totals = fetch_type_totals(db)
        total_cost = sum(row["amount"] for row in expenses_rows)

        return render_template(
            "index.html",
            expenses=expenses,
            category_totals=category_totals,
            type_totals=type_totals,
            total_cost=total_cost,
            current_sort=requested_sort,
            current_direction=direction,
        )

    @app.post("/expenses")
    @login_required
    @permission_required("can_add")
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

        if (
            not expense_date
            or not merchant
            or not category
            or not expense_type
            or expense_type not in EXPENSE_TYPES
            or category not in CATEGORIES
        ):
            flash("Proszę uzupełnić wymagane pola poprawnymi wartościami.", "error")
            return redirect(url_for("index"))

        db = get_db()
        max_order_row = db.execute(
            "SELECT COALESCE(MAX(display_order), -1) AS max_order FROM expenses"
        ).fetchone()
        current_max = max_order_row["max_order"] if max_order_row is not None else -1
        next_order = current_max + 1
        db.execute(
            """
            INSERT INTO expenses (
                expense_date, merchant, amount, category, notes, bank, description,
                expense_type, display_order
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                next_order,
            ),
        )
        db.commit()
        flash("Wydatek został dodany.", "success")
        return redirect(url_for("index"))

    @app.post("/expenses/<int:expense_id>/update")
    @login_required
    @permission_required("can_edit")
    def update_expense(expense_id: int):
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

        if (
            not expense_date
            or not merchant
            or not category
            or not expense_type
            or expense_type not in EXPENSE_TYPES
            or category not in CATEGORIES
        ):
            flash("Proszę uzupełnić wymagane pola poprawnymi wartościami.", "error")
            return redirect(url_for("index"))

        db = get_db()
        db.execute(
            """
            UPDATE expenses
               SET expense_date = ?,
                   merchant = ?,
                   amount = ?,
                   category = ?,
                   notes = ?,
                   bank = ?,
                   description = ?,
                   expense_type = ?
             WHERE id = ?
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
                expense_id,
            ),
        )
        db.commit()
        flash("Wydatek został zaktualizowany.", "success")
        return redirect(url_for("index"))

    @app.post("/expenses/<int:expense_id>/delete")
    @login_required
    @permission_required("can_delete")
    def delete_expense(expense_id: int):
        db = get_db()
        db.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        db.commit()
        flash("Wpis został usunięty.", "success")
        return redirect(url_for("index"))

    @app.post("/expenses/reorder")
    @login_required
    @permission_required("can_edit")
    def reorder_expenses() -> Response:
        payload = request.get_json(silent=True) or {}
        order = payload.get("order", [])
        if not isinstance(order, list):
            return jsonify({"error": "Nieprawidłowe dane."}), 400
        db = get_db()
        try:
            normalized_order = [int(expense_id) for expense_id in order]
        except (TypeError, ValueError):
            return jsonify({"error": "Nieprawidłowe dane."}), 400
        for position, expense_id in enumerate(normalized_order):
            db.execute(
                "UPDATE expenses SET display_order = ? WHERE id = ?",
                (position, expense_id),
            )
        db.commit()
        return ("", 204)

    @app.route("/users")
    @login_required
    @admin_required
    def manage_users():
        users = [dict(row) for row in get_db().execute("SELECT * FROM users ORDER BY username").fetchall()]
        return render_template("users.html", users=users)

    def count_admins(db: sqlite3.Connection) -> int:
        row = db.execute("SELECT COUNT(*) AS total FROM users WHERE role = 'admin'").fetchone()
        return int(row["total"])

    @app.post("/users/add")
    @login_required
    @admin_required
    def add_user():
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "user")
        can_add = 1 if request.form.get("can_add") else 0
        can_edit = 1 if request.form.get("can_edit") else 0
        can_delete = 1 if request.form.get("can_delete") else 0
        can_view_reports = 1 if request.form.get("can_view_reports") else 0

        if not username or not password:
            flash("Nazwa użytkownika i hasło są wymagane.", "error")
            return redirect(url_for("manage_users"))

        if role not in ROLE_LABELS:
            role = "user"

        if role == "admin":
            can_add = can_edit = can_delete = can_view_reports = 1

        db = get_db()
        try:
            db.execute(
                """
                INSERT INTO users (
                    username, password, role, can_add, can_edit, can_delete, can_view_reports
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (username, password, role, can_add, can_edit, can_delete, can_view_reports),
            )
            db.commit()
            flash("Użytkownik został dodany.", "success")
        except sqlite3.IntegrityError:
            flash("Taki użytkownik już istnieje.", "error")
        return redirect(url_for("manage_users"))

    @app.post("/users/<int:user_id>/update")
    @login_required
    @admin_required
    def update_user(user_id: int):
        password = request.form.get("password", "")
        role = request.form.get("role", "user")
        can_add = 1 if request.form.get("can_add") else 0
        can_edit = 1 if request.form.get("can_edit") else 0
        can_delete = 1 if request.form.get("can_delete") else 0
        can_view_reports = 1 if request.form.get("can_view_reports") else 0

        if role not in ROLE_LABELS:
            role = "user"

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if user is None:
            flash("Nie znaleziono użytkownika.", "error")
            return redirect(url_for("manage_users"))

        if role == "admin":
            can_add = can_edit = can_delete = can_view_reports = 1

        if user["role"] == "admin" and role != "admin" and count_admins(db) <= 1:
            flash("Nie można pozbawić uprawnień ostatniego administratora.", "error")
            return redirect(url_for("manage_users"))

        if not password:
            password = user["password"]

        db.execute(
            """
            UPDATE users
               SET password = ?,
                   role = ?,
                   can_add = ?,
                   can_edit = ?,
                   can_delete = ?,
                   can_view_reports = ?
             WHERE id = ?
            """,
            (password, role, can_add, can_edit, can_delete, can_view_reports, user_id),
        )
        db.commit()
        flash("Dane użytkownika zostały zaktualizowane.", "success")
        return redirect(url_for("manage_users"))

    @app.post("/users/<int:user_id>/delete")
    @login_required
    @admin_required
    def delete_user(user_id: int):
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if user is None:
            flash("Nie znaleziono użytkownika.", "error")
            return redirect(url_for("manage_users"))

        if user["role"] == "admin" and count_admins(db) <= 1:
            flash("Nie można usunąć ostatniego administratora.", "error")
            return redirect(url_for("manage_users"))

        if session.get("user_id") == user_id:
            flash("Nie możesz usunąć aktualnie zalogowanego użytkownika.", "error")
            return redirect(url_for("manage_users"))

        db.execute("DELETE FROM users WHERE id = ?", (user_id,))
        db.commit()
        flash("Użytkownik został usunięty.", "success")
        return redirect(url_for("manage_users"))

    @app.route("/reports")
    @login_required
    @permission_required("can_view_reports")
    def reports():
        db = get_db()
        category_totals = fetch_category_totals(db)
        type_totals = fetch_type_totals(db)
        monthly_totals = fetch_monthly_totals(db)

        stage_labels = CATEGORIES
        stage_values = [round(category_totals.get(label, 0.0), 2) for label in stage_labels]

        type_labels = EXPENSE_TYPES
        type_values = [round(type_totals.get(label, 0.0), 2) for label in type_labels]

        month_labels = [row["month"] for row in monthly_totals]
        month_values = [round(row["total"], 2) for row in monthly_totals]

        return render_template(
            "reports.html",
            stage_labels=stage_labels,
            stage_values=stage_values,
            type_labels=type_labels,
            type_values=type_values,
            month_labels=month_labels,
            month_values=month_values,
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
