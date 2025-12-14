from pyramid.config import Configurator


def main(global_config, **settings):
    """Main application entry point"""
    config = Configurator(settings=settings)
    
    # Include pyramid services
    config.include('pyramid_jinja2')
    config.include('.models')
    config.include('.routes')
    
    # Scan for view decorators
    config.scan()
    
    return config.make_wsgi_app()
