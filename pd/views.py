from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    MyModel,
    )


@view_config(route_name='api', renderer='json')
def api(request):
    #import pdb; pdb.set_trace();

    request.response.content_type = 'application/vnd.api+json'
    
    request.response.headers['Access-Control-Allow-Origin'] = 'http://localhost:4200'
    request.response.headers['Access-Control-Allow-Headers'] = 'X-Requested-With, Content-Type'
    request.response.headers['Access-Control-Allow-Credentials'] = 'true'
    request.response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE'
    
    return {
    'data': {
        'type':'profile',
        'id':'1',
        'attributes': {
          'firstname':'Jimbo','lastlogin':'August 24, 2015',
         },
    },
    }
    
    
    try:
        one = DBSession.query(MyModel).filter(MyModel.name == 'one').first()
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)
    return {'one': one, 'project': 'pd'}


conn_err_msg = """Can not connect to database. Fix!"""
