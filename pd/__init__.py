from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid.events import NewRequest
from .models import (
    session,
    Base,
)


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
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.include('pyramid_mailer')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_subscriber(add_cors_headers_response_callback, NewRequest)
    
    # routes
    config.add_route('get_profile', 'api/1/profiles/{one}')
    config.add_route('create_signup', 'api/1/signups')
    
    config.scan()
    return config.make_wsgi_app()

