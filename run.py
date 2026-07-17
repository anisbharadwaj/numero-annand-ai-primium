<<<<<<< HEAD
from app import create_app

app = create_app()

if __name__ == '__main__':
    print('🚀 Booting Server...')
    app.run(host='127.0.0.1', port=5000, debug=True)
=======
from app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
>>>>>>> db8c57642ee8a1a88b5dfa33e9f79afc16febeeb
