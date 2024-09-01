from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import os
import logging
from datetime import timedelta

app = Flask(__name__)
CORS(app)

# Configure SQLite database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'leaderboard.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this to a secure random key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

db = SQLAlchemy(app)
jwt = JWTManager(app)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    user = db.relationship('User', backref=db.backref('scores', lazy=True))

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    logger.debug(f"Registration attempt for username: {data.get('username')}")
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Missing username or password"}), 400
    
    if User.query.filter_by(username=data['username']).first():
        logger.warning(f"Registration failed: Username {data['username']} already exists")
        return jsonify({"error": "Username already exists"}), 400
    
    new_user = User(
        username=data['username'],
        password_hash=generate_password_hash(data['password'])
    )
    db.session.add(new_user)
    db.session.commit()
    
    logger.info(f"User registered successfully: {data['username']}")
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    logger.debug(f"Login attempt for username: {data.get('username')}")
    
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password_hash, data['password']):
        access_token = create_access_token(identity=user.id)
        logger.info(f"Login successful for user: {user.username}")
        return jsonify(access_token=access_token), 200
    
    logger.warning(f"Login failed for username: {data.get('username')}")
    return jsonify({"error": "Invalid username or password"}), 401

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    try:
        scores = db.session.query(User.username, db.func.max(Score.score).label('max_score')).\
            join(Score).group_by(User.id).order_by(db.desc('max_score')).limit(10).all()
        
        leaderboard = [{'name': score.username, 'score': score.max_score} for score in scores]
        logger.info("Leaderboard fetched successfully")
        return jsonify(leaderboard)
    except Exception as e:
        logger.error(f"Error fetching leaderboard: {str(e)}")
        return jsonify({"error": "Failed to fetch leaderboard"}), 500

@app.route('/api/submit_score', methods=['POST'])
@jwt_required()
def submit_score():
    data = request.json
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        logger.warning(f"Score submission failed: User not found for id {user_id}")
        return jsonify({"error": "User not found"}), 404
    
    new_score = Score(user_id=user.id, score=data['score'])
    db.session.add(new_score)
    db.session.commit()
    
    logger.info(f"Score submitted successfully for user {user.username}: {data['score']}")
    return jsonify({"message": "Score submitted successfully"}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)