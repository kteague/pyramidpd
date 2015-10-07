from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    MyModel,
    )


@view_config(route_name='get_profile', renderer='json')
def get_profile(request):
    #import pdb; pdb.set_trace();

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


@view_config(route_name='create_profile', renderer='json')
def create_profile(request):
    #import pdb; pdb.set_trace();
    request.response.status = '201 Created'
    request.response.content_type = 'application/vnd.api+json'
    request.response.headers['Location'] = 'http://localhost/api/1/profiles/2'
    
    return {
          "data": {
            "type": "profile",
            "id": "2",
            "attributes": {
                "username":'bob',"orientation":'straight',"gender":'male',"firstname":'kevin',"lastlogin":'today'
            },
          },
    }
    

conn_err_msg = """Can not connect to database. Fix!"""
