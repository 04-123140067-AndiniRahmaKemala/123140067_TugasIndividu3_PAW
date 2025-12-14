from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest, HTTPInternalServerError
from pyramid.response import Response
from ..models.review import Review
import json
import google.generativeai as genai
import requests
from datetime import datetime

# API Keys
GEMINI_API_KEY = "AIzaSyDyHFIHxBXuzUippL4hL4OI2lPdh-NgQe4"
HUGGINGFACE_API_KEY = "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"

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Hugging Face API endpoint for sentiment analysis
HF_SENTIMENT_API = "https://api-inference.huggingface.co/models/distilbert-base-uncased-finetuned-sst-2-english"


def add_cors_to_response(func):
    """Decorator to add CORS headers to response"""
    def wrapper(request):
        # Handle OPTIONS
        if request.method == 'OPTIONS':
            response = Response()
            response.status = 200
        else:
            result = func(request)
            response = request.response
            response.json_body = result
        
        # Add CORS headers
        response.headers.update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '3600'
        })
        return response
    return wrapper


@view_config(route_name='options')
def options_handler(request):
    """Handle OPTIONS requests for CORS"""
    response = Response()
    response.headers.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Max-Age': '3600'
    })
    return response


@view_config(route_name='home', renderer='json')
@add_cors_to_response
def home_view(request):
    """Home endpoint"""
    return {
        'project': 'Product Review Analyzer API',
        'version': '1.0',
        'endpoints': {
            'POST /api/analyze-review': 'Analyze new product review',
            'GET /api/reviews': 'Get all reviews with optional filters',
            'GET /api/reviews/stats': 'Get review statistics'
        }
    }


def analyze_sentiment_huggingface(text):
    """
    Analyze sentiment using Hugging Face API
    Returns: (sentiment, confidence)
    """
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    
    try:
        response = requests.post(
            HF_SENTIMENT_API,
            headers=headers,
            json={"inputs": text},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                # Get the highest confidence prediction
                predictions = result[0]
                top_prediction = max(predictions, key=lambda x: x['score'])
                
                # Map Hugging Face labels to our format
                label = top_prediction['label'].upper()
                confidence = top_prediction['score']
                
                # Convert POSITIVE/NEGATIVE to our format
                if 'POSITIVE' in label:
                    sentiment = 'POSITIVE'
                elif 'NEGATIVE' in label:
                    sentiment = 'NEGATIVE'
                else:
                    sentiment = 'NEUTRAL'
                
                return sentiment, confidence
        
        # Fallback if API fails
        return 'NEUTRAL', 0.5
        
    except Exception as e:
        print(f"Hugging Face API error: {str(e)}")
        # Fallback: simple keyword-based analysis
        text_lower = text.lower()
        positive_words = ['bagus', 'baik', 'luar biasa', 'mantap', 'suka', 'puas', 
                         'recommended', 'cepat', 'hebat', 'good', 'great', 'excellent', 
                         'amazing', 'love', 'best', 'perfect']
        negative_words = ['buruk', 'jelek', 'kurang', 'kecewa', 'lambat', 'parah', 
                         'cacat', 'rusak', 'bad', 'poor', 'terrible', 'worst', 
                         'hate', 'awful', 'disappointing']
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            return 'POSITIVE', min(1.0, 0.6 + 0.1 * pos_count)
        elif neg_count > pos_count:
            return 'NEGATIVE', min(1.0, 0.6 + 0.1 * neg_count)
        else:
            return 'NEUTRAL', 0.6


def extract_keypoints_gemini(text):
    """
    Extract key points using Gemini API
    Returns: list of key points
    """
    try:
        prompt = f"""
Analyze this product review and extract 3-5 main key points or highlights.
Return ONLY a JSON array of strings, no markdown, no extra text.

Review: {text}

Format: ["point 1", "point 2", "point 3"]
"""
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Try to parse JSON
        try:
            # Remove markdown code blocks if present
            if '```' in response_text:
                import re
                json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(1)
            
            key_points = json.loads(response_text)
            if isinstance(key_points, list) and len(key_points) > 0:
                return key_points
        except json.JSONDecodeError:
            pass
        
        # Fallback: split by sentences
        import re
        sentences = [s.strip() for s in re.split(r'[\.!?\n]+', text) if s.strip()]
        return sentences[:3] if sentences else ["Review analyzed"]
        
    except Exception as e:
        print(f"Gemini API error: {str(e)}")
        # Fallback
        import re
        sentences = [s.strip() for s in re.split(r'[\.!?\n]+', text) if s.strip()]
        return sentences[:3] if sentences else ["Review analyzed"]


@view_config(route_name='analyze_review', renderer='json', request_method='POST')
@add_cors_to_response
def analyze_review(request):
    """
    Analyze product review using Hugging Face (sentiment) and Gemini (key points)
    """
    try:
        # Get JSON data from request
        data = request.json_body
        product_name = data.get('product_name', '').strip()
        review_text = data.get('review_text', '').strip()

        if not product_name or not review_text:
            return HTTPBadRequest(json_body={
                'error': 'Missing required fields: product_name, review_text'
            })

        # Step 1: Sentiment Analysis using Hugging Face
        sentiment, confidence = analyze_sentiment_huggingface(review_text)

        # Step 2: Extract Key Points using Gemini
        key_points_list = extract_keypoints_gemini(review_text)
        key_points = json.dumps(key_points_list)

        # Step 3: Save to database
        new_review = Review(
            product_name=product_name,
            review_text=review_text,
            sentiment=sentiment,
            confidence=confidence,
            key_points=key_points,
            created_at=datetime.utcnow()
        )

        request.dbsession.add(new_review)
        request.dbsession.flush()

        return {
            'success': True,
            'id': new_review.id,
            'product_name': new_review.product_name,
            'review_text': new_review.review_text,
            'sentiment': new_review.sentiment,
            'confidence': new_review.confidence,
            'key_points': json.loads(new_review.key_points),
            'created_at': new_review.created_at.isoformat(),
            'message': 'Review analyzed successfully'
        }

    except Exception as e:
        import traceback
        print(f"\nERROR in analyze_review: {str(e)}")
        traceback.print_exc()
        return HTTPInternalServerError(json_body={
            'error': f'Error analyzing review: {str(e)}'
        })


@view_config(route_name='get_reviews', renderer='json', request_method='GET')
@add_cors_to_response
def get_reviews(request):
    """
    Get all reviews from database with optional filtering, pagination, and sorting
    """
    try:
        # Get filters
        sentiment_filter = request.GET.get('sentiment')
        product_filter = request.GET.get('product_name')
        
        # Pagination
        try:
            page = int(request.GET.get('page', '1'))
            page_size = int(request.GET.get('page_size', '10'))
            if page < 1:
                page = 1
            if page_size < 1 or page_size > 100:
                page_size = 10
        except ValueError:
            page = 1
            page_size = 10

        # Sorting
        sort = (request.GET.get('sort') or 'created_at_desc').lower()

        # Build query
        query = request.dbsession.query(Review)

        if sentiment_filter:
            query = query.filter(Review.sentiment == sentiment_filter.upper())

        if product_filter:
            query = query.filter(Review.product_name.ilike(f'%{product_filter}%'))

        # Apply sort
        if sort == 'created_at_asc':
            query = query.order_by(Review.created_at.asc())
        elif sort == 'confidence_desc':
            query = query.order_by(Review.confidence.desc())
        elif sort == 'confidence_asc':
            query = query.order_by(Review.confidence.asc())
        else:
            query = query.order_by(Review.created_at.desc())

        # Get total and paginated results
        total = query.count()
        reviews = query.offset((page - 1) * page_size).limit(page_size).all()

        result = []
        for review in reviews:
            result.append({
                'id': review.id,
                'product_name': review.product_name,
                'review_text': review.review_text,
                'sentiment': review.sentiment,
                'confidence': review.confidence,
                'key_points': json.loads(review.key_points) if review.key_points else [],
                'created_at': review.created_at.isoformat()
            })

        return {
            'success': True,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size,
            'reviews': result
        }

    except Exception as e:
        import traceback
        print(f"\nERROR in get_reviews: {str(e)}")
        traceback.print_exc()
        return HTTPInternalServerError(json_body={
            'error': f'Error fetching reviews: {str(e)}'
        })


@view_config(route_name='get_review_stats', renderer='json', request_method='GET')
@add_cors_to_response
def get_review_stats(request):
    """
    Get statistics about reviews
    """
    try:
        total = request.dbsession.query(Review).count()
        
        positive = request.dbsession.query(Review).filter(
            Review.sentiment == 'POSITIVE'
        ).count()
        
        negative = request.dbsession.query(Review).filter(
            Review.sentiment == 'NEGATIVE'
        ).count()
        
        neutral = request.dbsession.query(Review).filter(
            Review.sentiment == 'NEUTRAL'
        ).count()

        return {
            'success': True,
            'total': total,
            'positive': positive,
            'negative': negative,
            'neutral': neutral,
            'positive_percentage': round((positive / total * 100), 1) if total > 0 else 0,
            'negative_percentage': round((negative / total * 100), 1) if total > 0 else 0,
            'neutral_percentage': round((neutral / total * 100), 1) if total > 0 else 0
        }

    except Exception as e:
        import traceback
        print(f"\nERROR in get_review_stats: {str(e)}")
        traceback.print_exc()
        return HTTPInternalServerError(json_body={
            'error': f'Error fetching stats: {str(e)}'
        })
