"""
Database layer for persistent session and file storage.
Uses SQLite for lightweight persistence with automatic cleanup.
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict

try:
    from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Boolean
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, Session
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    # Fallback to in-memory storage
    print("SQLAlchemy not available, using in-memory storage")

# Database configuration
DB_DIR = Path(__file__).parent / "data"
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "cz_career_architect.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Session expiry (default: 7 days)
SESSION_EXPIRY_DAYS = int(os.getenv("SESSION_EXPIRY_DAYS", "7"))
FILE_EXPIRY_DAYS = int(os.getenv("FILE_EXPIRY_DAYS", "7"))

if SQLALCHEMY_AVAILABLE:
    Base = declarative_base()
    engine = create_engine(DATABASE_URL, echo=False)
    SessionLocal = sessionmaker(bind=engine)

    class ChatSession(Base):
        """Chat session with conversation history."""
        __tablename__ = "chat_sessions"
        
        id = Column(String, primary_key=True)
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        messages_json = Column(Text, default="[]")  # JSON array of messages
        active = Column(Boolean, default=True)

    class UploadedFile(Base):
        """Metadata for uploaded files."""
        __tablename__ = "uploaded_files"
        
        id = Column(String, primary_key=True)
        filename = Column(String, nullable=False)
        size = Column(Integer, nullable=False)
        file_type = Column(String, nullable=False)
        file_path = Column(String, nullable=False)
        uploaded_at = Column(DateTime, default=datetime.utcnow)
        text_content = Column(Text)  # Extracted text
        preview = Column(Text)  # First 300 chars
        issues_json = Column(Text, default="[]")  # JSON array of issues
        active = Column(Boolean, default=True)

    # Create tables
    Base.metadata.create_all(engine)

    class DatabaseManager:
        """Manager for database operations with automatic cleanup."""
        
        def __init__(self):
            self.Session = SessionLocal
        
        def get_session(self) -> Session:
            """Get database session."""
            return self.Session()
        
        # ========== Chat Sessions ==========
        
        def create_chat_session(self, session_id: str) -> None:
            """Create new chat session."""
            with self.get_session() as db:
                session = ChatSession(id=session_id)
                db.add(session)
                db.commit()
        
        def get_chat_history(self, session_id: str) -> List[Dict]:
            """Get chat history for session."""
            with self.get_session() as db:
                session = db.query(ChatSession).filter_by(id=session_id, active=True).first()
                if session:
                    return json.loads(session.messages_json)
                return []
        
        def update_chat_history(self, session_id: str, messages: List[Dict]) -> None:
            """Update chat history for session."""
            with self.get_session() as db:
                session = db.query(ChatSession).filter_by(id=session_id).first()
                if session:
                    session.messages_json = json.dumps(messages)
                    session.updated_at = datetime.utcnow()
                    session.active = True
                    db.commit()
                else:
                    # Create new session
                    new_session = ChatSession(
                        id=session_id,
                        messages_json=json.dumps(messages)
                    )
                    db.add(new_session)
                    db.commit()
        
        def clear_chat_session(self, session_id: str) -> None:
            """Clear chat session (soft delete)."""
            with self.get_session() as db:
                session = db.query(ChatSession).filter_by(id=session_id).first()
                if session:
                    session.active = False
                    session.messages_json = "[]"
                    db.commit()
        
        def cleanup_old_sessions(self) -> int:
            """Remove sessions older than expiry date."""
            cutoff = datetime.utcnow() - timedelta(days=SESSION_EXPIRY_DAYS)
            with self.get_session() as db:
                count = db.query(ChatSession).filter(
                    ChatSession.updated_at < cutoff
                ).delete()
                db.commit()
                return count
        
        # ========== Uploaded Files ==========
        
        def save_uploaded_file(
            self,
            file_id: str,
            filename: str,
            size: int,
            file_type: str,
            file_path: str,
            text_content: str,
            preview: str,
            issues: List[str]
        ) -> None:
            """Save uploaded file metadata."""
            with self.get_session() as db:
                file = UploadedFile(
                    id=file_id,
                    filename=filename,
                    size=size,
                    file_type=file_type,
                    file_path=file_path,
                    text_content=text_content,
                    preview=preview,
                    issues_json=json.dumps(issues)
                )
                db.add(file)
                db.commit()
        
        def get_uploaded_file(self, file_id: str) -> Optional[Dict]:
            """Get uploaded file metadata."""
            with self.get_session() as db:
                file = db.query(UploadedFile).filter_by(id=file_id, active=True).first()
                if file:
                    return {
                        'id': file.id,
                        'name': file.filename,
                        'size': file.size,
                        'type': file.file_type,
                        'path': file.file_path,
                        'text': file.text_content,
                        'uploaded_at': file.uploaded_at.isoformat(),
                        'preview': file.preview,
                        'issues': json.loads(file.issues_json)
                    }
                return None
        
        def list_uploaded_files(self) -> List[Dict]:
            """List all active uploaded files."""
            with self.get_session() as db:
                files = db.query(UploadedFile).filter_by(active=True).all()
                return [
                    {
                        'id': f.id,
                        'name': f.filename,
                        'size': f.size,
                        'type': f.file_type,
                        'uploaded_at': f.uploaded_at.isoformat(),
                        'preview': f.preview,
                        'issues': json.loads(f.issues_json)
                    }
                    for f in files
                ]
        
        def delete_uploaded_file(self, file_id: str) -> bool:
            """Delete uploaded file (soft delete)."""
            with self.get_session() as db:
                file = db.query(UploadedFile).filter_by(id=file_id).first()
                if file:
                    file.active = False
                    db.commit()
                    # Delete physical file
                    Path(file.file_path).unlink(missing_ok=True)
                    return True
                return False
        
        def cleanup_old_files(self) -> int:
            """Remove files older than expiry date."""
            cutoff = datetime.utcnow() - timedelta(days=FILE_EXPIRY_DAYS)
            with self.get_session() as db:
                files = db.query(UploadedFile).filter(
                    UploadedFile.uploaded_at < cutoff
                ).all()
                count = 0
                for file in files:
                    Path(file.file_path).unlink(missing_ok=True)
                    count += 1
                db.query(UploadedFile).filter(
                    UploadedFile.uploaded_at < cutoff
                ).delete()
                db.commit()
                return count

    # Global instance
    db_manager = DatabaseManager()

else:
    # Fallback: In-memory storage when SQLAlchemy not available
    class InMemoryManager:
        """Fallback in-memory storage manager."""
        
        def __init__(self):
            self.sessions = {}
            self.files = {}
        
        def create_chat_session(self, session_id: str) -> None:
            self.sessions[session_id] = []
        
        def get_chat_history(self, session_id: str) -> List[Dict]:
            return self.sessions.get(session_id, [])
        
        def update_chat_history(self, session_id: str, messages: List[Dict]) -> None:
            self.sessions[session_id] = messages
        
        def clear_chat_session(self, session_id: str) -> None:
            self.sessions.pop(session_id, None)
        
        def cleanup_old_sessions(self) -> int:
            return 0  # No cleanup for in-memory
        
        def save_uploaded_file(self, file_id, filename, size, file_type, file_path, 
                              text_content, preview, issues) -> None:
            self.files[file_id] = {
                'id': file_id,
                'name': filename,
                'size': size,
                'type': file_type,
                'path': file_path,
                'text': text_content,
                'uploaded_at': datetime.utcnow().isoformat(),
                'preview': preview,
                'issues': issues
            }
        
        def get_uploaded_file(self, file_id: str) -> Optional[Dict]:
            return self.files.get(file_id)
        
        def list_uploaded_files(self) -> List[Dict]:
            return [
                {k: v for k, v in f.items() if k not in ['path', 'text']}
                for f in self.files.values()
            ]
        
        def delete_uploaded_file(self, file_id: str) -> bool:
            if file_id in self.files:
                Path(self.files[file_id]['path']).unlink(missing_ok=True)
                del self.files[file_id]
                return True
            return False
        
        def cleanup_old_files(self) -> int:
            return 0

    db_manager = InMemoryManager()


# Export
__all__ = ['db_manager', 'SQLALCHEMY_AVAILABLE']
