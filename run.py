from app import create_app

app = create_app()

if __name__ == '__main__':
    print("🚀 Numero Annand AI Premium Booting Successfully...")
    print("👉 Portal URL: http://127.0.0.1:5000")
    print("🔒 Default Admin User: 'admin' | Password: 'AnnandSarmaAI2026'")
    app.run(host='127.0.0.1', port=5000, debug=True)
