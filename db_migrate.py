import os
from flask_migrate import Migrate
from flask.cli import FlaskGroup

from leaderboard_server import app, db

migrate = Migrate(app, db)

cli = FlaskGroup(app)

if __name__ == '__main__':
    os.environ['FLASK_APP'] = 'leaderboard_server.py'
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Recreate all tables
        db.create_all()
        
        print("Database schema recreated successfully.")
    
    print("Database migration completed successfully.")