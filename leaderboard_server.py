from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import os
import traceback
from datetime import timedelta
from sqlalchemy.exc import SQLAlchemyError

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

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    games_played = db.Column(db.Integer, default=0)
    total_score = db.Column(db.Integer, default=0)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)


@app.errorhandler(Exception)
def handle_exception(e):
    # Log the error
    app.logger.error(f"Unhandled exception: {str(e)}\n{traceback.format_exc()}")
    # Return JSON instead of HTML for HTTP errors
    return jsonify(error=str(e), stack_trace=traceback.format_exc()), 500

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    if 'username' not in data or 'password' not in data:
        return jsonify({"error": "Username and password required"}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Username already exists"}), 400
    
    new_user = User(
        username=data['username'],
        password_hash=generate_password_hash(data['password'])
    )
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password_hash, data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token}), 200
    return jsonify({"error": "Invalid username or password"}), 401


@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    try:
        app.logger.info("Fetching leaderboard data...")
        
        # Check database connection
        try:
            db.session.query("1").from_statement("SELECT 1").all()
            app.logger.info("Database connection successful")
        except SQLAlchemyError as e:
            app.logger.error(f"Database connection error: {str(e)}")
            return jsonify({"error": "Database connection error", "details": str(e)}), 500

        # Fetch leaderboard data
        scores = db.session.query(User.username, db.func.max(Score.score).label('max_score')).\
            join(Score).group_by(User.id).order_by(db.desc('max_score')).limit(10).all()
        
        app.logger.info(f"Leaderboard data fetched: {scores}")
        return jsonify([{'name': score.username, 'score': score.max_score} for score in scores])
    except Exception as e:
        app.logger.error(f"Error fetching leaderboard: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": "An error occurred while fetching the leaderboard", "details": str(e), "stack_trace": traceback.format_exc()}), 500

@app.route('/api/player_stats', methods=['GET'])
@jwt_required()
def get_player_stats():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    highest_score = db.session.query(db.func.max(Score.score)).filter(Score.user_id == user_id).scalar()
    
    return jsonify({
        "username": user.username,
        "games_played": user.games_played,
        "total_score": user.total_score,
        "average_score": user.total_score / user.games_played if user.games_played > 0 else 0,
        "highest_score": highest_score or 0
    }), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)