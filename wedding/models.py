import datetime
import enum
import jwt

from connexion.exceptions import ProblemException
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from itsdangerous import URLSafeTimedSerializer

from sqlalchemy.ext.hybrid import hybrid_property

from .config import key

db = SQLAlchemy()
flask_bcrypt = Bcrypt()


class ResponseType(enum.Enum):
    NO_RESPONSE = 0
    CONFIRMED = 1
    DECLINED = 2

    def __str__(self):
        return self.name


class InvitationType(enum.Enum):
    HOUSE = 0
    WEEKEND = 1
    DAY = 2

    def __str__(self):
        return self.name


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    firstname = db.Column(db.String(255), nullable=False)
    lastname = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    password_hash = db.Column(db.String(100))

    verified = db.Column(db.Boolean, nullable=False, default=False)
    verification_code = db.Column(db.String(256), nullable=True)
    verified_on = db.Column(db.DateTime, nullable=True)

    password_recovery_code = db.Column(db.String(256), nullable=True)
    password_recovery_gendate = db.Column(db.DateTime, nullable=True)

    invitation_group_id = db.Column(db.Integer, db.ForeignKey("invitation_group.id"))

    def __repr__(self):
        return ("<{} name={} email{}>").format(
            self.__class__.__name__, self.fullname, self.email
        )

    @property
    def password(self):
        raise AttributeError("password is write-only")

    @password.setter
    def password(self, password):
        self.password_hash = flask_bcrypt.generate_password_hash(password).decode(
            "utf-8"
        )

    def check_password(self, password):
        return flask_bcrypt.check_password_hash(self.password_hash, password)

    @property
    def invitation(self):
        return self.invitation_group.invitation

    @hybrid_property
    def fullname(self):
        return self.firstname + " " + self.lastname

    def generate_jwt(self):
        try:
            now = datetime.datetime.utcnow()
            payload = {
                "exp": now + (datetime.timedelta(days=1)),
                "iat": now,
                "sub": self.email,
                "name": self.fullname,
            }
            token_payload = jwt.encode(payload, key, algorithm="HS512")
            token_payload = token_payload.decode("utf-8")
        except Exception as e:
            return e

        token = Token(token=token_payload)
        db.session.add(token)
        db.session.commit()
        return token_payload

    @classmethod
    def validate_token(cls, auth_token: str):
        try:
            payload = jwt.decode(auth_token, key)
            revoked_token = Token.check_token(auth_token)
            if revoked_token:
                raise ProblemException(401, "Unauthorized", "Token has been revoked. Please log in again.")
            if payload["exp"] < int(datetime.datetime.utcnow().timestamp()):
                raise ProblemException(401, "Unauthorized", "Token has expired. Please log in again")
            email = payload["sub"]
            return (cls.query.filter_by(email=email)).first()
        except jwt.ExpiredSignatureError:
            raise ProblemException(401, "Unauthorized", "Signature expired. Please log in again.")
        except jwt.InvalidTokenError:
            raise ProblemException(401, "Unauthorized", "Invalid token. Please log in again.")

    @classmethod
    def validate_email_code(cls, code):
        serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        try:
            email = serializer.loads(code, max_age=current_app.config["EMAIL_EXP"])
        except Exception:
            raise Exception("Code has expired. Please try again")

        user = cls.query.filter_by(email=email).first()
        user.verified = True
        user.verification_code = None
        user.verified_on = datetime.datetime.now()

        db.session.add(user)
        db.session.commit()

    def untrust_email(self):
        email = self.email
        serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        code = serializer.dumps(email)
        print(code)

        self.verified = False
        self.verified_on = None
        self.verification_code = code

    @classmethod
    def validate_recovery_code(cls, code):
        serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        try:
            email = serializer.loads(code, max_age=current_app.config["EMAIL_EXP"])
        except Exception:
            raise Exception("Code has expired. Please try and reset your password again")

        user = cls.query.filter_by(email=email, password_recovery_code=code).first()
        if user is None:
            raise Exception("Code is not valid. Please try and reset your password again")

        user.password_recovery_code = None
        user.password_recovery_gendate = None

        return user

    def generate_recovery_code(self):
        email = self.email
        serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        code = serializer.dumps(email)
        print("recovery code: ", code)

        self.password_recovery_code = code
        self.password_recovery_gendate = datetime.datetime.now()
        db.session.commit()
    
    def dump(self):
        return {
            "id": self.id,
            "email": self.email,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "fullname": self.fullname,
            "admin": self.admin,
            "group_name": self.invitation_group.friendly_name
        }


class Invitation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invitation_type = db.Column(db.Enum(InvitationType), nullable=False)
    response = db.Column(
        db.Enum(ResponseType), nullable=False, default=ResponseType.NO_RESPONSE
    )
    requirements = db.Column(db.String(1000))
    plus_one = db.Column(db.Boolean, nullable=False, default=False)
    plus_one_name = db.Column(db.String(256), nullable=True)
    locked = db.Column(db.Boolean, nullable=False, default=False)
    invitation_group_id = db.Column(db.Integer, db.ForeignKey("invitation_group.id"))

    @property
    def users(self):
        return self.invitation_group.users


class InvitationGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    friendly_name = db.Column(db.String(255), nullable=False, unique=True)
    group_code = db.Column(db.String(16), nullable=False)
    users = db.relationship("User", backref="invitation_group")
    invitation = db.relationship(
        "Invitation", backref="invitation_group", uselist=False, cascade="all,delete"
    )
    names = db.relationship("InvitationName")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.invitation = Invitation()


class InvitationName(db.Model):
    __tablename__ = 'invitation_names'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey("invitation_group.id"))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship("User")


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(1024), nullable=False, unique=True)
    revoked = db.Column(db.Boolean, nullable=False, default=False)
    revoked_on = db.Column(db.DateTime)

    @classmethod
    def check_token(cls, token):
        rv = cls.query.filter_by(token=token).first()
        if rv:
            if rv.revoked:
                return True
            return False
        return True

    @classmethod
    def revoke(cls, token):
        rv = cls.query.filter_by(token=token).first()
        rv.revoked = True
        rv.revoked_on = datetime.datetime.now()
        db.session.commit()
        return True
