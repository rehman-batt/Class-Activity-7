import pytest
from app import app, db, User

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

    # Cleanup
    with app.app_context():
        db.drop_all()

# Helper function to create a user
def create_user(email, password):
    user = User(email=email, password=password)
    db.session.add(user)
    db.session.commit()

# Test home route
def test_home_redirect(client):
    response = client.get('/')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

# Test signup route
def test_signup(client):
    response = client.post('/signup', data={'email': 'test@example.com', 'password': 'password123'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'User registered successfully' not in response.data  # Check if successful signup message is logged

# Test login route
def test_login(client):
    create_user('test@example.com', 'password123')

    response = client.post('/login', data={'email': 'test@example.com', 'password': 'password123'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid email or password' not in response.data

# Test main route without login
def test_main_redirect(client):
    response = client.get('/main')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

# Test main route with login
def test_main(client):
    create_user('test@example.com', 'password123')

    client.post('/login', data={'email': 'test@example.com', 'password': 'password123'}, follow_redirects=True)
    response = client.get('/main')
    assert response.status_code == 200

# Test logout
def test_logout(client):
    create_user('test@example.com', 'password123')

    client.post('/login', data={'email': 'test@example.com', 'password': 'password123'}, follow_redirects=True)
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert '/login' in response.request.path

# Test prediction route
def test_predict(client):
    create_user('test@example.com', 'password123')

    client.post('/login', data={'email': 'test@example.com', 'password': 'password123'}, follow_redirects=True)

    response = client.post('/predict', data={'humid': '50', 'wind_sp': '10'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'prediction' in response.data  # Verify the prediction is displayed
