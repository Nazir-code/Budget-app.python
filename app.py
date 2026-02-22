from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from passlib.hash import pbkdf2_sha256
from datetime import datetime, timedelta
import os

app = Flask(__name__)
CORS(app)

# Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "budget.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "super-secret-key-change-this-in-production"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)

db = SQLAlchemy(app)
jwt = JWTManager(app)

# -------------------
# Models
# -------------------

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade="all, delete-orphan")
    goals = db.relationship('Goal', backref='user', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = pbkdf2_sha256.hash(password)

    def check_password(self, password):
        return pbkdf2_sha256.verify(password, self.password_hash)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # income / expense
    description = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "description": self.description,
            "amount": self.amount,
            "category": self.category,
            "date": self.date.strftime("%Y-%m-%d")
        }

class Goal(db.Model):
    __tablename__ = 'goals'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)

    def to_dict(self):
        progress = (self.current_amount / self.target_amount * 100) if self.target_amount > 0 else 0
        return {
            "id": self.id,
            "name": self.name,
            "target_amount": self.target_amount,
            "current_amount": self.current_amount,
            "progress": min(progress, 100)
        }

# -------------------
# Auth Routes
# -------------------

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"error": "Nom d'utilisateur et mot de passe requis"}), 400
    
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Cet utilisateur existe déjà"}), 400
    
    user = User(username=data["username"])
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    
    return jsonify({"message": "Utilisateur créé avec succès"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get("username")).first()
    
    if user and user.check_password(data.get("password")):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({"access_token": access_token, "username": user.username}), 200
    
    return jsonify({"error": "Identifiants invalides"}), 401

# -------------------
# Data Routes (Protected)
# -------------------

@app.route("/transactions", methods=["GET"])
@jwt_required()
def get_transactions():
    user_id = get_jwt_identity()
    transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.date.desc()).all()
    return jsonify([t.to_dict() for t in transactions])

@app.route("/transactions", methods=["POST"])
@jwt_required()
def add_transaction():
    user_id = get_jwt_identity()
    data = request.json
    
    if not data or not all(k in data for k in ("type", "description", "amount", "category")):
        return jsonify({"error": "Données manquantes"}), 400

    new_transaction = Transaction(
        user_id=user_id,
        type=data["type"],
        description=data["description"],
        amount=float(data["amount"]),
        category=data["category"]
    )

    db.session.add(new_transaction)
    db.session.commit()

    return jsonify({"message": "Transaction ajoutée", "transaction": new_transaction.to_dict()}), 201

@app.route("/transactions/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_transaction(id):
    user_id = get_jwt_identity()
    transaction = Transaction.query.filter_by(id=id, user_id=user_id).first_or_404()
    db.session.delete(transaction)
    db.session.commit()
    return jsonify({"message": "Transaction supprimée"})

@app.route("/goals", methods=["GET"])
@jwt_required()
def get_goals():
    user_id = get_jwt_identity()
    goals = Goal.query.filter_by(user_id=user_id).all()
    return jsonify([g.to_dict() for g in goals])

@app.route("/goals", methods=["POST"])
@jwt_required()
def add_goal():
    user_id = get_jwt_identity()
    data = request.json
    if not data or not all(k in data for k in ("name", "target_amount")):
        return jsonify({"error": "Données manquantes"}), 400
    
    new_goal = Goal(
        user_id=user_id,
        name=data["name"],
        target_amount=float(data["target_amount"])
    )
    db.session.add(new_goal)
    db.session.commit()
    return jsonify(new_goal.to_dict()), 201

@app.route("/goals/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_goal(id):
    user_id = get_jwt_identity()
    goal = Goal.query.filter_by(id=id, user_id=user_id).first_or_404()
    db.session.delete(goal)
    db.session.commit()
    return jsonify({"message": "Objectif supprimé"})

@app.route("/balance", methods=["GET"])
@jwt_required()
def get_balance():
    user_id = get_jwt_identity()
    income = db.session.query(db.func.sum(Transaction.amount))\
        .filter(Transaction.type == "income", Transaction.user_id == user_id).scalar() or 0

    expense = db.session.query(db.func.sum(Transaction.amount))\
        .filter(Transaction.type == "expense", Transaction.user_id == user_id).scalar() or 0

    return jsonify({
        "income": income,
        "expense": expense,
        "balance": income - expense
    })

if __name__ == "__main__":
    with app.app_context():
        # Force recreation to apply schema changes (adding user_id and users table)
        db.drop_all() 
        db.create_all()
    app.run(debug=True)
