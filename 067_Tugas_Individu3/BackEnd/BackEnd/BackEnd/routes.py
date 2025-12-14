def includeme(config):
    """Configure routes for the application"""
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    
    # API Routes for Review Analysis
    config.add_route('analyze_review', '/api/analyze-review')
    config.add_route('get_reviews', '/api/reviews')
    config.add_route('get_review_stats', '/api/reviews/stats')
    
    # OPTIONS route for CORS preflight
    config.add_route('options', '/*traverse', request_method='OPTIONS')
