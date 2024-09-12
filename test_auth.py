
from unittest import TestCase, main
from app import create_app
from models import db, User


class UserAuthTestCase(TestCase):

    def setUp(self):
        self.app = create_app('finwize_db_test', testing=True)
        self.client = self.app.test_client()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///finwize_db_test'
        self.app.config['WTF_CSRF_ENABLED'] = False
        with self.app.app_context():
            db.create_all()

            self.user = User.signup(email='authtest@email.com', password='password')
            db.session.add(self.user)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_user_authenticate(self):
        with self.app.app_context():
            user = db.session.merge(self.user)

            auth_user = User.authenticate('authtest@email.com', 'password')

            self.assertEqual(auth_user, user)

    def test_user_authenticate_invalid_user(self):
        with self.app.app_context():
            auth_user = User.authenticate('invaliduser@email.com', 'password')

            self.assertFalse(auth_user)

    def test_user_authenticate_invalid_password(self):
        with self.app.app_context():
            auth_user = User.authenticate('authtest@email.com', 'wrongpassword')

            self.assertFalse(auth_user)

if __name__ == '__main__':
    main()