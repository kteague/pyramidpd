from pyramid.config import Configurator
from pd.authentication import EmberAuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.events import NewRequest
from sqlalchemy import engine_from_config
from pd.models import session, Base


def add_cors_headers_response_callback(event):
    def cors_headers(request, response):
        
        # This is being set in Apache ...
        # 'Access-Control-Allow-Origin': '*',
        # 'Access-Control-Allow-Headers': 'Origin, Content-Type, Accept, Authorization',
        # 'Access-Control-Allow-Methods': 'POST,GET,DELETE,PUT,OPTIONS',
        # 'Access-Control-Max-Age': '1728000',
        
        response.headers.update({
        'Access-Control-Allow-Credentials': 'true',
        })
    event.request.add_response_callback(cors_headers)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    session.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings, root_factory='pd.models.RootFactory')
    config.include('pyramid_chameleon')
    config.include('pyramid_mailer')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_subscriber(add_cors_headers_response_callback, NewRequest)
    config.set_authentication_policy(
        EmberAuthTktAuthenticationPolicy('secret_in_development_XXX')
    )
    config.set_authorization_policy(
        ACLAuthorizationPolicy()
    )
    
    # routes
    config.add_route('get_profile', 'api/1/profiles/{one}')
    config.add_route('edit_profile', 'api/1/profiles/{one}')
    config.add_route('set_password', 'api/1/set_password')
    config.add_route('create_signup', 'api/1/signups')
    config.add_route('sign_in', 'api/1/sign_in')
    
    config.scan()
    return config.make_wsgi_app()

