from app import create_app, db

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    print("🚀 Numero Annand AI Premium is starting on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
