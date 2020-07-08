import datetime
import enum
import jwt

from connexion.exceptions import ProblemException
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from itsdangerous import URLSafeTimedSerializer

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref

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


class MenuCourse(enum.Enum):
    STARTER = 0
    MAIN = 1
    DESERT = 2

    def __str__(self):
        return self.name


class GuestType(enum.Enum):
    ADULT = 0
    CHILD = 1
    BABY = 2

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

    @hybrid_property
    def fullname(self):
        return self.firstname + " " + self.lastname

    def generate_jwt(self):
        try:
            now = datetime.datetime.utcnow()
            payload = {
                "exp": now + (datetime.timedelta(days=7)),
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
                raise ProblemException(
                    401, "Unauthorized", "Token has been revoked. Please log in again."
                )
            if payload["exp"] < int(datetime.datetime.utcnow().timestamp()):
                raise ProblemException(
                    401, "Unauthorized", "Token has expired. Please log in again"
                )
            email = payload["sub"]

            user = cls.query.filter_by(email=email).first()
            if user is None:
                Token.revoke(auth_token)
                raise ProblemException(401, "Unauthorized", "No valid user found")
            return user
        except jwt.ExpiredSignatureError:
            raise ProblemException(
                401, "Unauthorized", "Signature expired. Please log in again."
            )
        except jwt.InvalidTokenError:
            raise ProblemException(
                401, "Unauthorized", "Invalid token. Please log in again."
            )

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
            raise Exception(
                "Code has expired. Please try and reset your password again"
            )

        user = cls.query.filter_by(email=email, password_recovery_code=code).first()
        if user is None:
            raise Exception(
                "Code is not valid. Please try and reset your password again"
            )

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
        staying_in_house = False
        if self.associated_guest is not None:
            group_name = self.associated_guest.invitation_group.friendly_name
            if (
                self.associated_guest.invitation_group.invitation.invitation_type
                == InvitationType.HOUSE
            ):
                if (
                    self.associated_guest.invitation_group.invitation.staying_in_house
                    != False
                ):
                    staying_in_house = True
        else:
            group_name = None
        return {
            "id": self.id,
            "email": self.email,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "fullname": self.fullname,
            "admin": self.admin,
            "group_name": group_name,
            "staying_in_house": staying_in_house,
        }


class Invitation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invitation_type = db.Column(db.Enum(InvitationType), nullable=False)
    response = db.Column(
        db.Enum(ResponseType), nullable=False, default=ResponseType.NO_RESPONSE
    )
    staying_in_house = db.Column(db.Boolean, nullable=True)
    requirements = db.Column(db.String(1000))
    arriving = db.Column(db.String(32), nullable=True)
    leaving = db.Column(db.String(32), nullable=True)
    shared_room = db.Column(db.Boolean, nullable=False, default=False)

    locked = db.Column(db.Boolean, nullable=False, default=False)
    invitation_group_id = db.Column(db.Integer, db.ForeignKey("invitation_group.id"))

    @property
    def users(self):
        return self.invitation_group.guests

    def dump(self):
        return {
            "type": str(self.invitation_type),
            "response": str(self.response),
            "requirements": self.requirements,
            "staying_in_house": self.staying_in_house,
            "arriving": self.arriving,
            "leaving": self.leaving,
            "locked": self.locked,
            "shared_room": self.shared_room,
        }


class InvitationGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    friendly_name = db.Column(db.String(255), nullable=False, unique=True)
    group_code = db.Column(db.String(16), nullable=False)
    invitation = db.relationship(
        "Invitation", backref="invitation_group", uselist=False, cascade="all,delete"
    )
    guests = db.relationship("Guest", backref="invitation_group")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.invitation = Invitation()

    def dump(self):
        rv = {
            "id": self.id,
            "code": self.group_code,
            "name": self.friendly_name,
            "invitation": self.invitation.dump(),
            "guests": [g.dump() for g in self.guests],
        }
        return rv


class Guest(db.Model):
    __tablename__ = "guests"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    type_ = db.Column(db.Enum(GuestType), nullable=False, default=GuestType.ADULT)
    is_coming = db.Column(db.Boolean, nullable=True)
    plus_one = db.Column(db.Boolean, nullable=False, default=False)

    first_course = db.Column(db.Integer, db.ForeignKey("menu_items.id"), nullable=True)
    main_course = db.Column(db.Integer, db.ForeignKey("menu_items.id"), nullable=True)
    desert_course = db.Column(db.Integer, db.ForeignKey("menu_items.id"), nullable=True)

    group_id = db.Column(db.Integer, db.ForeignKey("invitation_group.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    user = db.relationship("User", backref=backref("associated_guest", uselist=False))

    def dump(self):
        rv = {
            "id": self.id,
            "name": self.name,
            "user": None,
            "type": self.type_.name,
            "is_coming": self.is_coming,
            "plus_one": self.plus_one,
            "first_course": self.first_course,
            "main_course": self.main_course,
            "desert_course": self.desert_course,
        }
        if self.user:
            rv["user"] = self.user.dump()
        return rv


class MenuItem(db.Model):
    __tablename__ = "menu_items"
    id = db.Column(db.Integer, primary_key=True)
    course = db.Column(db.Enum(MenuCourse), nullable=False)
    description = db.Column(db.String(512), nullable=False)
    vegetarian = db.Column(db.Boolean, nullable=False, default=False)
    gluten_free = db.Column(db.Boolean, nullable=False, default=False)
    additional_info = db.Column(db.String(256), nullable=True)

    def dump(self):
        return {
            "id": self.id,
            "course": str(self.course),
            "description": self.description,
            "vegetarian": self.vegetarian,
            "gluten_free": self.gluten_free,
            "additional_info": self.additional_info,
        }


class GuestChoice(db.Model):
    __tablename__ = "guest_choices"
    id = db.Column(db.Integer, primary_key=True)

    guest_id = db.Column(db.Integer, db.ForeignKey("guests.id"))
    guest = db.relationship("Guest", backref=backref("menu_choice", uselist=False))

    starter_id = db.Column(db.Integer, db.ForeignKey("menu_items.id"))
    main_id = db.Column(db.Integer, db.ForeignKey("menu_items.id"))
    desert_id = db.Column(db.Integer, db.ForeignKey("menu_items.id"))

    starter = db.relationship("MenuItem", foreign_keys=[starter_id])
    main = db.relationship("MenuItem", foreign_keys=[main_id])
    desert = db.relationship("MenuItem", foreign_keys=[desert_id])


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
