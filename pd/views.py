from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy.exc import DBAPIError
from pd.models import session
from pd.models import Signup


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
        one = session.query(Sigup).filter(Signup.id == 'one').first()
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)
    return {'one': one, 'project': 'pd'}


@view_config(route_name='create_signup', renderer='json')
def create_signup(request):
    import pdb; pdb.set_trace();
    Signup()
    
    request.response.status = '201 Created'
    request.response.content_type = 'application/vnd.api+json'
    request.response.headers['Location'] = 'http://localhost/api/1/signups/2'
    
    res = {
          "data": {
            "type": "profiles",
            "id": "2",
            "attributes": {
                "username":'bob',"orientation":'straight',"gender":'male',"firstname":'kevin',"lastlogin":'today'
            },
          },
    }

    return res

conn_err_msg = """Can not connect to database. Fix!"""
