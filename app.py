# app.py — CampusVault Flask backend
# Handles: signup, login (by college_id), page rendering
 
from flask import Flask, request, jsonify, render_template, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
import jwt, datetime, re, uuid
 
# ── App setup ──────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder="static", template_folder="templates")
app.config.from_object(Config)
CORS(app)
db = SQLAlchemy(app)
 
# ── Model ──────────────────────────────────────────────────────────────────
class User(db.Model):
    __tablename__ = "users"
 
    id          = db.Column(db.Integer,     primary_key=True)
    unique_id   = db.Column(db.String(36),  unique=True, nullable=False,
                            default=lambda: str(uuid.uuid4()))
    name        = db.Column(db.String(120), nullable=False)
    email       = db.Column(db.String(120), unique=True,  nullable=False)
    password    = db.Column(db.String(256), nullable=False)
    role        = db.Column(db.String(20),  nullable=False, default="student")
    college_id  = db.Column(db.String(60),  unique=True, nullable=True)
    created_at  = db.Column(db.DateTime,    default=datetime.datetime.utcnow)
 
    def to_dict(self):
        return {
            "unique_id":  self.unique_id,
            "name":       self.name,
            "email":      self.email,
            "role":       self.role,
            "college_id": self.college_id or "",
        }
 
# ── Helpers ────────────────────────────────────────────────────────────────
def make_token(user: User) -> str:
    payload = {
        "sub":  user.unique_id,
        "role": user.role,
        "exp":  datetime.datetime.utcnow() + datetime.timedelta(days=7),
    }
    return jwt.encode(payload, app.config["JWT_SECRET"], algorithm="HS256")
 
# ── Regex patterns ─────────────────────────────────────────────────────────
 
EMAIL_RE = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
 
FACULTY_CODE_RE = re.compile(r'^[A-Za-z0-9\-_]{4,16}$')
 
# College ID must follow:  GNIT/<one or more digits>/<one or more digits>
# Examples of VALID IDs  : GNIT/2021/001  |  GNIT/24/10045  |  GNIT/2024/123456
# Examples of INVALID IDs: gnit/2021/001  (lowercase)
#                          GNIT/2021      (missing second segment)
#                          GNIT/abc/001   (non-numeric segment)
#                          GNT/2021/001   (wrong prefix)
COLLEGE_ID_RE = re.compile(r'^GNIT/\d{4}/\d{4}$')
 
def validate_college_id(college_id: str) -> str | None:
    """
    Returns None if valid, or an error message string if invalid.
    Runs checks in order so the message is always specific.
    """
    if not college_id:
        return "College ID is required."
 
    if not college_id.startswith("GNIT"):
        return "College ID must start with 'GNIT' (e.g. GNIT/2024/001)."
 
    if not COLLEGE_ID_RE.match(college_id):
        return (
            "College ID format is invalid. "
            "Expected format: GNIT/<year or batch>/<roll number>  "
            "e.g. GNIT/2024/001"
        )
 
    return None   # all good
 
# ── Auth blueprint ─────────────────────────────────────────────────────────
auth = Blueprint("auth", __name__, url_prefix="/auth")
 
# ────────────────────────────── SIGNUP ────────────────────────────────────
@auth.post("/signup")
def signup():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400
 
    name         = (data.get("name")         or "").strip()
    email        = (data.get("email")        or "").strip().lower()
    password     =  data.get("password")     or ""
    role         = (data.get("role")         or "student").strip().lower()
    college_id   = (data.get("college_id")   or "").strip()
    faculty_code = (data.get("faculty_code") or "").strip()
 
    # ── Field validation ───────────────────────────────────────────────────
    if not name:
        return jsonify({"error": "Name is required."}), 422
 
    if not EMAIL_RE.match(email):
        return jsonify({"error": "Invalid email address."}), 422
 
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 422
 
    if role not in ("student", "faculty"):
        return jsonify({"error": "Role must be 'student' or 'faculty'."}), 422
 
    # ── College ID validation ──────────────────────────────────────────────
    college_id_error = validate_college_id(college_id)
    if college_id_error:
        return jsonify({"error": college_id_error}), 422
 
    # ── Faculty code validation ────────────────────────────────────────────
    if role == "faculty":
        if not faculty_code:
            return jsonify({"error": "Faculty verification code is required."}), 422
        if not FACULTY_CODE_RE.match(faculty_code):
            return jsonify({"error": "Faculty code format is invalid."}), 422
        if faculty_code != app.config["FACULTY_CODE"]:
            return jsonify({"error": "Incorrect faculty verification code."}), 403
 
    # ── Duplicate checks ───────────────────────────────────────────────────
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "An account with this email already exists."}), 409
 
    if User.query.filter_by(college_id=college_id).first():
        return jsonify({"error": "This College ID is already registered."}), 409
 
    # ── Create user ────────────────────────────────────────────────────────
    user = User(
        name       = name,
        email      = email,
        password   = generate_password_hash(password),
        role       = role,
        college_id = college_id,
    )
    db.session.add(user)
    db.session.commit()
 
    return jsonify({"token": make_token(user), "user": user.to_dict()}), 201
 
 
# ────────────────────────────── LOGIN ─────────────────────────────────────
@auth.post("/login")
def login():
    data = request.get_json(silent=True) or {}
 
    # Accept login by college_id OR email
    college_id = (data.get("college_id") or "").strip()
    email      = (data.get("email")      or "").strip().lower()
    password   =  data.get("password")   or ""
 
    if not password:
        return jsonify({"error": "Password is required."}), 422
 
    # ── Validate college_id format if that's what was provided ────────────
    if college_id:
        college_id_error = validate_college_id(college_id)
        if college_id_error:
            return jsonify({"error": college_id_error}), 422
 
    # ── Look up user ───────────────────────────────────────────────────────
    user = None
    if college_id:
        user = User.query.filter_by(college_id=college_id).first()
    elif email:
        user = User.query.filter_by(email=email).first()
    else:
        return jsonify({"error": "Please provide your College ID or email."}), 422
 
    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid credentials. Please try again."}), 401
 
    return jsonify({"token": make_token(user), "user": user.to_dict()}), 200
 
 
app.register_blueprint(auth)
 
# ── Page routes ────────────────────────────────────────────────────────────
 
# "frontend" blueprint keeps url_for('frontend', filename=...) working in signup.html
frontend_bp = Blueprint(
    "frontend", __name__,
    static_folder="static",
    static_url_path="/frontend",
)
app.register_blueprint(frontend_bp)
 
@app.get("/")
@app.get("/signup")
def signup_page():
    return render_template("signup.html")
 
@app.get("/sign_in.html")
@app.get("/login")
def login_page():
    return render_template("sign_in.html")
 
@app.get("/dashboard.student.html")
def student_dashboard():
    return "<h2>Student Dashboard — coming soon</h2>", 200
 
@app.get("/dashboard.faculty.html")
def faculty_dashboard():
    return "<h2>Faculty Dashboard — coming soon</h2>", 200
 
@app.get("/admin_dashboard.html")
def admin_dashboard():
    return "<h2>Admin Dashboard — coming soon</h2>", 200
 
# ── DB init ────────────────────────────────────────────────────────────────
with app.app_context():
    db.create_all()
 
if __name__ == "__main__":
    app.run(debug=True, port=5000)