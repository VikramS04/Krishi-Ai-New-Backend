from flask import Blueprint, request, jsonify
from src.models.user import db, CommunityPost, CommunityComment, User
import json
from datetime import datetime

community_bp = Blueprint('community', __name__)

@community_bp.route('/community/posts', methods=['GET'])
def get_posts():
    """Get community posts with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        category = request.args.get('category')
        language = request.args.get('language')
        
        query = CommunityPost.query
        
        if category:
            query = query.filter_by(category=category)
        if language:
            query = query.filter_by(language=language)
        
        posts = query.order_by(CommunityPost.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': [post.to_dict() for post in posts.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': posts.total,
                'pages': posts.pages,
                'has_next': posts.has_next,
                'has_prev': posts.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@community_bp.route('/community/posts', methods=['POST'])
def create_post():
    """Create a new community post"""
    try:
        data = request.get_json()
        
        required_fields = ['user_id', 'title', 'content']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        post = CommunityPost(
            user_id=data['user_id'],
            title=data['title'],
            content=data['content'],
            category=data.get('category'),
            language=data.get('language', 'english')
        )
        
        db.session.add(post)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': post.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@community_bp.route('/community/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """Get a specific post with comments"""
    try:
        post = CommunityPost.query.get_or_404(post_id)
        comments = CommunityComment.query.filter_by(post_id=post_id).order_by(CommunityComment.created_at.asc()).all()
        
        post_data = post.to_dict()
        post_data['comments'] = [comment.to_dict() for comment in comments]
        
        return jsonify({
            'success': True,
            'data': post_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@community_bp.route('/community/posts/<int:post_id>/comments', methods=['POST'])
def add_comment():
    """Add a comment to a post"""
    try:
        data = request.get_json()
        
        required_fields = ['user_id', 'content']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        comment = CommunityComment(
            post_id=post_id,
            user_id=data['user_id'],
            content=data['content']
        )
        
        db.session.add(comment)
        
        # Update comment count
        post = CommunityPost.query.get(post_id)
        if post:
            post.comments_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': comment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@community_bp.route('/community/posts/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    """Like a post"""
    try:
        post = CommunityPost.query.get_or_404(post_id)
        post.likes_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'likes_count': post.likes_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@community_bp.route('/community/categories', methods=['GET'])
def get_categories():
    """Get available post categories"""
    categories = [
        'Crop Management',
        'Soil Health',
        'Pest Control',
        'Weather Discussion',
        'Market Prices',
        'Technology',
        'Success Stories',
        'Questions',
        'General Discussion'
    ]
    
    return jsonify({
        'success': True,
        'data': categories
    }), 200

@community_bp.route('/community/search', methods=['GET'])
def search_posts():
    """Search posts by keyword"""
    try:
        query = request.args.get('q', '')
        category = request.args.get('category')
        language = request.args.get('language')
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        search_query = CommunityPost.query.filter(
            CommunityPost.title.contains(query) | 
            CommunityPost.content.contains(query)
        )
        
        if category:
            search_query = search_query.filter_by(category=category)
        if language:
            search_query = search_query.filter_by(language=language)
        
        posts = search_query.order_by(CommunityPost.created_at.desc()).limit(20).all()
        
        return jsonify({
            'success': True,
            'data': [post.to_dict() for post in posts],
            'query': query
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@community_bp.route('/community/trending', methods=['GET'])
def get_trending_posts():
    """Get trending posts based on likes and comments"""
    try:
        # Get posts from last 7 days with high engagement
        from datetime import timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        posts = CommunityPost.query.filter(
            CommunityPost.created_at >= week_ago
        ).order_by(
            (CommunityPost.likes_count + CommunityPost.comments_count).desc()
        ).limit(10).all()
        
        return jsonify({
            'success': True,
            'data': [post.to_dict() for post in posts]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

