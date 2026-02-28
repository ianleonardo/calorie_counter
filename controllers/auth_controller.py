from flask import Blueprint, redirect, url_for, session, render_template, current_app
from functools import wraps

auth_bp = Blueprint('auth', __name__)


def login_required(f):
    """Decorator to require login for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/login')
def login():
    """Show the login page."""
    if 'user' in session:
        return redirect(url_for('main.index'))
    return render_template('login.html')


@auth_bp.route('/auth/google')
def google_login():
    """Redirect to Google OAuth."""
    oauth = current_app.extensions['oauth']
    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route('/auth/callback')
def google_callback():
    """Handle Google OAuth callback."""
    oauth = current_app.extensions['oauth']
    token = oauth.google.authorize_access_token()
    user_info = token.get('userinfo')

    if user_info:
        session['user'] = {
            'name': user_info.get('name', ''),
            'email': user_info.get('email', ''),
            'picture': user_info.get('picture', ''),
        }

    return redirect(url_for('main.index'))


@auth_bp.route('/auth/guest')
def guest_login():
    """Log in as a guest without Google OAuth."""
    session['user'] = {
        'name': 'Guest',
        'email': '',
        'picture': '',
    }
    return redirect(url_for('main.index'))


@auth_bp.route('/logout')
def logout():
    """Clear session and redirect to login."""
    session.pop('user', None)
    session.pop('user_profile', None)
    return redirect(url_for('auth.login'))


@auth_bp.route('/privacy')
def privacy():
    """Show the privacy policy page."""
    return render_template('privacy.html')


@auth_bp.route('/terms')
def terms():
    """Show the terms of service page."""
    return render_template('terms.html')
