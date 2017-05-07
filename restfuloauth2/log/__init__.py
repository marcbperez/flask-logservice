from ..database import db
from ..database.model import Model
from werkzeug.security import gen_salt
from datetime import datetime


class Log(db.Model, Model):
    """Minimal implementation of a REST model."""

    __tablename__ = 'log'

    message = db.Column(db.String(1000))

    def serialize(self):
        """Returns the serialized version of this model."""
        serialized = Model.serialize(self)
        serialized['message'] = self.message
        return serialized

    @classmethod
    def add_parser_args(cls, parser):
        """Adds model parameters to parser validation."""
        parser.add_argument('public', required=True, help='Model visibility.')
        parser.add_argument('message', required=True, help='Model message.')

    @classmethod
    def update(cls, model, etag, public, message):
        """Updates a model if the etag matches."""
        if model.etag != etag:
            return False

        model.etag = gen_salt(40)
        model.updated = datetime.utcnow()
        model.public = public == '1'
        model.message = message
        db.session.commit()

        return model

    @classmethod
    def create(cls, user, public, message):
        """Creates a model owned by the provided user."""
        model = cls()
        model.user_id = user.id
        model.etag = gen_salt(40)
        model.created = model.updated = datetime.utcnow()
        model.public = public == '1'
        model.message = message
        db.session.add(model)
        db.session.commit()

        return model
