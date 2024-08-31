from flask import Flask, request, jsonify
from flask_cors import CORS
import operator

app = Flask(__name__)
CORS(app)  # This allows cross-origin requests, which is necessary for local development

# In-memory storage for leaderboard data
leaderboard = []

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    sorted_leaderboard = sorted(leaderboard, key=operator.itemgetter('score'), reverse=True)
    return jsonify(sorted_leaderboard[:10])  # Return top 10 scores

@app.route('/api/submit_score', methods=['POST'])
def submit_score():
    data = request.json
    if 'name' in data and 'score' in data:
        leaderboard.append({
            'name': data['name'],
            'score': data['score']
        })
        return jsonify({"message": "Score submitted successfully"}), 200
    else:
        return jsonify({"error": "Invalid data"}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)