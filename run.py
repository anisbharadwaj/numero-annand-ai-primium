import os
from app import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Ensure database tables exist locally
        db.create_all()
        # Create upload folder directory path if missing
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
    print("🚀 Numero Annand AI Premium starting on http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
