active_sessions = {}  # Store active user sessions

def add_session(email, token):
    """Store user session with token."""
    active_sessions[email] = token

def remove_session(email):
    """Remove user session."""
    active_sessions.pop(email, None)

def is_user_logged_in(email):
    """Check if user is logged in."""
    return email in active_sessions
