from pyramid.view import view_config
from pd.models import session
from pd.models import Signup, Profile
from pd.crypto import encode_password
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from pyramid.security import remember, forget
import datetime
import json
import random
import string


@view_config(route_name='sign_in', renderer='json')
def sign_in(request):
    identification = request.POST['identification']
    password = request.POST['password']
    try:
        profile = session.query(Profile).filter(Profile.email==identification)[0]
    except IndexError:
        request.response.status = '401 Unauthorized'
        request.response.content_type = 'application/vnd.api+json'
        return {'message':'Account does not exist.'}
    
    algorithm, iterations, salt, hash = profile.password.split('$', 3)
    if profile.password == encode_password(password, salt):
        # authentication success
        authtkt_ticket = remember(request, identification)
        return {'token':authtkt_ticket,'email':identification}
    else:
        request.response.status = '401 Unauthorized'
        request.response.content_type = 'application/vnd.api+json'
        return {'message':'Password does not match.'}


@view_config(route_name='get_profile', request_method='GET', renderer='json', permission='view')
def get_profile(request):
    request.response.content_type = 'application/vnd.api+json'
    profileid = request.matchdict['profileid']
    try:
        profile = session.query(Profile).filter(Profile.id==profileid)[0]
    except IndexError:
        request.response.status = '404 Not Found'
        return {}
    
    return {
        'data': {
            'type':'profile',
            'id':profileid,
            'attributes': {
              'orientation':profile.orientation,
              'gender':profile.gender,
              'city':profile.city,
              'country':profile.country,
              'birthdate':str(profile.birthdate),
              'name':profile.name,
              'about_me':profile.about_me,
              'interests':profile.interests,
              'looking_for':profile.looking_for
             },
        },
    }


@view_config(route_name='edit_profile', request_method='PUT', renderer='json')
def edit_profile(request):
    pass

    
@view_config(route_name='set_password', renderer='json')
def set_password(request):
    secret_key = request.POST['k']
    signup_id = request.POST['id']
    password = request.POST['p']
    
    signup = session.query(Signup).filter(Signup.id==signup_id)[0]
    profile = session.query(Profile).filter(Profile.email==signup.email)[0]
    
    if signup.secret_key == secret_key:
        profile.password = encode_password(password)


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


def validate_signup(request):
    signup = session.query(Signup).filter(Signup.id==request.GET['id'])[0]
    if signup.secret_key != request.GET['k']:
        # probably just a 200 and an error message is OK?
        request.response.status = '400 Bad Request'
        return 'foo!'

    if not session.query(Profile).filter(Profile.id==request.GET['id']):    
        profile = Profile()
        profile.id = str(signup.id)
        profile.orientation = signup.orientation
        profile.gender = signup.gender
        profile.country = signup.country
        profile.city = signup.city
        profile.birthdate = signup.birthdate
        profile.email = signup.email
        session.add(profile)
        session.flush()

    # handle response
    request.response.status = '200 OK'
    request.response.content_type = 'application/vnd.api+json'
    request.response.headers['Location'] = 'http://localhost/api/1/signups/%s' % signup.id
    
    return {
       "data": {
         "type": "signups",
         "id": str(signup.id),
         "attributes": {
             'orientation':signup.orientation,
             'gender':signup.gender,
             'country':signup.country,
             'city':signup.city,
             'birthdate':signup.birthdate.isoformat(),
             'email':signup.email,
         },
       },
    }


@view_config(route_name='create_signup', renderer='json')
def create_or_validate_signup(request):
    """
    Route to two views:
    
    1) Creates a Sign-up request with a secret key that is emailed to the user.
    
    2) Validate a sign-up request. Called with query params of the id and secret key
    to validate that the email has been recieved.
    """
    if request.body:
        return create_signup(request)
    else:
        return validate_signup(request)

