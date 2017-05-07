from . import Log
from ..oauth.models import User
from ..database.query import Query
from flask import request
from flask_restful import abort, Resource


class LogItem(Resource):
    """Log model item endpoint."""

    def get(self, log_id):
        """Gets a model given its id and outputs the serialized version."""
        user = User.get_authorized()
        log = Query.get_item_or_abort(Log, log_id, user)

        return log.serialize()

    def delete(self, log_id):
        """Deletes a model given its id."""
        user = User.get_authorized()
        log = Query.get_item_or_abort(Log, log_id, user)
        args = Log.parse_delete_arguments()
        delete = Log.delete(log, args['etag'])

        if not delete:
            abort(401, message=Query.ETAG_NOT_MATCHING)

        return '', 204

    def put(self, log_id):
        """Updates a model given its id and outputs the serialized version."""
        user = User.get_authorized()
        log = Query.get_item_or_abort(Log, log_id, user)
        args = Log.parse_put_arguments()
        update = Log.update(log, args['etag'], args['public'], args['message'])

        if not update:
            abort(401, message=Query.ETAG_NOT_MATCHING)

        return update.serialize(), 201


class LogIndex(Resource):
    """Log model index endpoint."""

    def get(self):
        """Outputs a serialized, paginated collection of models."""
        page = request.args.get('page', Query.DEFAULT_PAGE)
        max_results = request.args.get(
            'max_results', Query.DEFAULT_MAX_RESULTS)
        sort = request.args.get('sort', Query.DEFAULT_SORT)
        sort_direction = Query.get_sort_attribute(Log, sort)
        search = request.args.get('search', Query.DEFAULT_SEARCH)

        user = User.get_authorized()
        logs = Log.get_permitted_models(
            user, sort_direction, page, max_results, search)

        return Log.serialize_list(logs)

    def post(self):
        """Adds a model to the colletion and outputs the serialized version."""
        user = User.get_authorized()
        args = Log.parse_post_arguments()
        log = Log.create(user, args['public'], args['message'])

        return log.serialize(), 201
