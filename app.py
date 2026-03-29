from flask import Flask, request, jsonify, render_template, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
import jwt
import datetime
import re
import uuid

# ── App setup ──────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder="static", template_folder="templates")
app.config.from_object(Config)
CORS(app)
db = SQLAlchemy(app)

# ── Database model ─────────────────────────────────────────────────────────
class User(db.Model):
    __tablename__ = "users"

    id          = db.Column(db.Integer, primary_key=True)
    unique_id   = db.Column(db.String(36), unique=True, nullable=False,
                            default=lambda: str(uuid.uuid4()))
    name        = db.Column(db.String(120), nullable=False)
    email       = db.Column(db.String(120), unique=True, nullable=False)
    password    = db.Column(db.String(256), nullable=False)
    role        = db.Column(db.String(20),  nullable=False, default="student")
    college_id  = db.Column(db.String(60),  nullable=True)
    created_at  = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            "unique_id":  self.unique_id,
            "name":       self.name,
            "email":      self.email,
            "role":       self.role,
            "college_id": self.college_id,
        }

# ── Helpers ────────────────────────────────────────────────────────────────
def make_token(user: User) -> str:
    payload = {
        "sub":  user.unique_id,
        "role": user.role,
        "exp":  datetime.datetime.utcnow() + datetime.timedelta(days=7),
    }
    return jwt.encode(payload, app.config["JWT_SECRET"], algorithm="HS256")

FACULTY_CODE_PATTERN = re.compile(r'^[A-Za-z0-9\-_]{4,16}$')

# ── Auth blueprint ─────────────────────────────────────────────────────────
auth = Blueprint("auth", __name__, url_prefix="/auth")

@auth.post("/signup")
def signup():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    # ── Pull fields ────────────────────────────────────────────────────────
    name        = (data.get("name") or "").strip()
    email       = (data.get("email") or "").strip().lower()
    password    = data.get("password") or ""
    role        = (data.get("role") or "student").strip().lower()
    college_id  = (data.get("college_id") or "").strip()   # from HTML field
    faculty_code= (data.get("faculty_code") or "").strip()

    # ── Server-side validation ─────────────────────────────────────────────
    if not name:
        return jsonify({"error": "Name is required"}), 422

    email_re = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
    if not email_re.match(email):
        return jsonify({"error": "Invalid email address"}), 422

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 422

    if role not in ("student", "faculty"):
        return jsonify({"error": "Role must be 'student' or 'faculty'"}), 422

    # ── Faculty code check ─────────────────────────────────────────────────
    if role == "faculty":
        if not faculty_code:
            return jsonify({"error": "Faculty verification code is required"}), 422
        if not FACULTY_CODE_PATTERN.match(faculty_code):
            return jsonify({"error": "Faculty code format is invalid"}), 422
        if faculty_code != app.config["FACULTY_CODE"]:
            return jsonify({"error": "Incorrect faculty verification code"}), 403

    # ── Duplicate email check ──────────────────────────────────────────────
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "An account with this email already exists"}), 409

    # ── Create user ────────────────────────────────────────────────────────
    user = User(
        name       = name,
        email      = email,
        password   = generate_password_hash(password),
        role       = role,
        college_id = college_id or None,
    )
    db.session.add(user)
    db.session.commit()

    token = make_token(user)

    return jsonify({
        "token": token,
        "user":  user.to_dict(),
    }), 201


@auth.post("/login")
def login():
    data  = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    pwd   = data.get("password") or ""

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, pwd):
        return jsonify({"error": "Invalid email or password"}), 401

    return jsonify({
        "token": make_token(user),
        "user":  user.to_dict(),
    }), 200


app.register_blueprint(auth)

# ── Page routes ────────────────────────────────────────────────────────────

# "frontend" blueprint so url_for('frontend', filename=...) works
frontend_bp = Blueprint(
    "frontend", __name__,
    static_folder="static",
    static_url_path="/frontend"
)
app.register_blueprint(frontend_bp)

@app.get("/")
@app.get("/signup")
def signup_page():
    return render_template("signup.html")

@app.get("/sign_in.html")
def signin_page():
    return render_template("sign_in.html")

# ── DB init + run ──────────────────────────────────────────────────────────
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, port=5000)