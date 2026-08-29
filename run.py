import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

if __name__ == '__main__':
    from backend.app import app
    app.run(host='0.0.0.0', port=5000, debug=True)
