from pyramid.view import view_config
from pd.models import session
from pd.models import Signup
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
import datetime
import json
import random
import string


@view_config(route_name='get_profile', renderer='json')
def get_profile(request):
    
    return {
        'data': {
            'type':'profile',
            'id':'1',
            'attributes': {
              'firstname':'Jimbo','lastlogin':'August 24, 2015',
             },
        },
    }


@view_config(route_name='create_signup', renderer='json')
def create_signup(request):
    data = json.loads(request.body.decode('UTF-8'))['data']['attributes']
    signup = Signup()
    signup.orientation = data['orientation']
    signup.gender = data['gender']
    signup.country = data['country']
    signup.city = data['city']
    signup.email = data['email']
    signup.birthdate = datetime.date(int(data['year']), int(data['month']), int(data['day']))
    signup.secret_key = ''.join(random.choice(
        string.ascii_letters + string.digits) for _ in range(20))
    
    session.add(signup)
    session.flush()
    
    # send activation email
    mailer = get_mailer(request)
    body = """
Your account on Passport Date is almost active!

Click on the link below to get started:

http://localhost/activate?id=%s&k=%s
""" % (signup.id, signup.secret_key)
    message = Message(
        subject="Validate your Passport Date account",
        sender="accounts@passportdate.com",
        recipients=[signup.email],
        body=body,
    )
    mailer.send(message)
    
    # handle response
    request.response.status = '201 Created'
    request.response.content_type = 'application/vnd.api+json'
    request.response.headers['Location'] = 'http://localhost/api/1/signups/%s' % signup.id
    
    return {
          "data": {
            "type": "signups",
            "id": str(signup.id),
            "attributes": data,
          },
    }

