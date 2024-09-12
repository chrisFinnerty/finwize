
from unittest import TestCase, main
from app import create_app
from models import db


class AppTestCase(TestCase):
    def setUp(self):
        """Setup test app and client/login."""

        self.app = create_app('finwize_db_test', testing=True)
        self.client = self.app.test_client()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///finwize_db_test'
        self.app.config['WTF_CSRF_ENABLED'] = False
        with self.app.app_context():
            db.create_all()
            self.client.post('/signup', data={
               'email': 'test@test.com',
               'password': 'password' 
            })

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_homepage(self):
        with self.client as c:
            response = c.get('/')

            self.assertEqual(response.status_code, 200)
            self.assertIn(b'<li class="nav-item"><a class="nav-link text-light" href="/user/1/profile">Profile</a></li>', response.data)

if __name__ == '__main__':
    main()
