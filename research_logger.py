"""
Encrypted Session Logger for Deep Research Assistant
Tracks authenticated user sessions with Fernet encryption for surveillance.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Fernet key from environment
FERNET_KEY = os.getenv('FERNET_KEY')
if not FERNET_KEY:
    raise ValueError('FERNET_KEY environment variable is not set. Please set it in your environment.')

fernet = Fernet(FERNET_KEY.encode())

class SessionLogger:
    """
    Simple encrypted session logger for tracking authenticated user activities.
    All session data is encrypted with Fernet encryption.
    """
    
    def __init__(self, log_file: str = "research.log"):
        self.log_file = log_file
        self.fernet = fernet
    
    def log_session(self, email: str, report_name: str, button_clicked: str, 
                   timestamp: Optional[str] = None, additional_data: Optional[Dict] = None):
        """
        Log an authenticated session with encryption.
        
        Args:
            email: User's email address
            report_name: Name/title of the research report
            button_clicked: Which button was clicked (e.g., "start_research", "download_pdf")
            timestamp: Optional timestamp (defaults to current time)
            additional_data: Optional additional data to log
        """
        if not timestamp:
            timestamp = datetime.now().isoformat()
        
        # Create session data
        session_data = {
            "email": email,
            "timestamp": timestamp,
            "report_name": report_name,
            "button_clicked": button_clicked
        }
        
        # Add additional data if provided
        if additional_data:
            session_data.update(additional_data)
        
        # Convert to JSON string
        json_data = json.dumps(session_data, indent=2)
        
        # Encrypt the data
        encrypted_data = self.fernet.encrypt(json_data.encode())
        
        # Append to log file
        with open(self.log_file, "ab") as f:
            f.write(encrypted_data + b"\n")
    
    def decrypt_logs(self, output_file: Optional[str] = None) -> list:
        """
        Decrypt all logs and return as list of dictionaries.
        
        Args:
            output_file: Optional file to save decrypted logs as JSON
            
        Returns:
            List of decrypted session dictionaries
        """
        if not os.path.exists(self.log_file):
            return []
        
        decrypted_sessions = []
        
        with open(self.log_file, "rb") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        # Decrypt the line
                        decrypted_data = self.fernet.decrypt(line)
                        session_data = json.loads(decrypted_data.decode())
                        decrypted_sessions.append(session_data)
                    except Exception as e:
                        print(f"Error decrypting line: {e}")
                        continue
        
        # Save to output file if specified
        if output_file:
            with open(output_file, "w") as f:
                json.dump(decrypted_sessions, f, indent=2)
        
        return decrypted_sessions
    
    def get_user_sessions(self, email: str) -> list:
        """
        Get all sessions for a specific user.
        
        Args:
            email: User's email address
            
        Returns:
            List of sessions for the user
        """
        all_sessions = self.decrypt_logs()
        return [session for session in all_sessions if session.get("email") == email]
    
    def get_recent_sessions(self, hours: int = 24) -> list:
        """
        Get sessions from the last N hours.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List of recent sessions
        """
        from datetime import timedelta
        
        all_sessions = self.decrypt_logs()
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_sessions = []
        for session in all_sessions:
            try:
                session_time = datetime.fromisoformat(session["timestamp"])
                if session_time >= cutoff_time:
                    recent_sessions.append(session)
            except Exception:
                continue
        
        return recent_sessions
    
    def search_sessions(self, search_term: str) -> list:
        """
        Search sessions by report name or email.
        
        Args:
            search_term: Term to search for
            
        Returns:
            List of matching sessions
        """
        all_sessions = self.decrypt_logs()
        search_term = search_term.lower()
        
        matching_sessions = []
        for session in all_sessions:
            email = session.get("email", "").lower()
            report_name = session.get("report_name", "").lower()
            
            if search_term in email or search_term in report_name:
                matching_sessions.append(session)
        
        return matching_sessions
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get basic statistics about logged sessions.
        
        Returns:
            Dictionary with statistics
        """
        all_sessions = self.decrypt_logs()
        
        if not all_sessions:
            return {
                "total_sessions": 0,
                "unique_users": 0,
                "most_active_user": None,
                "most_common_action": None,
                "date_range": None
            }
        
        # Count unique users
        unique_users = set(session.get("email") for session in all_sessions)
        
        # Count user activity
        user_activity = {}
        for session in all_sessions:
            email = session.get("email")
            if email:
                user_activity[email] = user_activity.get(email, 0) + 1
        
        # Count button clicks
        button_clicks = {}
        for session in all_sessions:
            button = session.get("button_clicked")
            if button:
                button_clicks[button] = button_clicks.get(button, 0) + 1
        
        # Get date range
        timestamps = [session.get("timestamp") for session in all_sessions if session.get("timestamp")]
        if timestamps:
            try:
                dates = [datetime.fromisoformat(ts) for ts in timestamps]
                date_range = {
                    "earliest": min(dates).isoformat(),
                    "latest": max(dates).isoformat()
                }
            except Exception:
                date_range = None
        else:
            date_range = None
        
        return {
            "total_sessions": len(all_sessions),
            "unique_users": len(unique_users),
            "most_active_user": max(user_activity.items(), key=lambda x: x[1])[0] if user_activity else None,
            "most_common_action": max(button_clicks.items(), key=lambda x: x[1])[0] if button_clicks else None,
            "date_range": date_range,
            "user_activity": user_activity,
            "button_clicks": button_clicks
        }

# Global logger instance
session_logger = SessionLogger()

# Convenience functions for easy integration
def log_authenticated_session(email: str, report_name: str, button_clicked: str, 
                             additional_data: Optional[Dict] = None):
    """Log an authenticated user session"""
    session_logger.log_session(email, report_name, button_clicked, additional_data=additional_data)

def decrypt_all_logs(output_file: Optional[str] = None) -> list:
    """Decrypt all logs and optionally save to file"""
    return session_logger.decrypt_logs(output_file)

def get_user_history(email: str) -> list:
    """Get all sessions for a specific user"""
    return session_logger.get_user_sessions(email)

def get_recent_activity(hours: int = 24) -> list:
    """Get recent sessions from the last N hours"""
    return session_logger.get_recent_sessions(hours)

def search_user_activity(search_term: str) -> list:
    """Search sessions by email or report name"""
    return session_logger.search_sessions(search_term)

def get_surveillance_stats() -> Dict[str, Any]:
    """Get surveillance statistics"""
    return session_logger.get_statistics() 