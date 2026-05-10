"""
Database Connection Module
Handles all database operations using SQLAlchemy ORM
"""

import os
import logging
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLAlchemy setup
Base = declarative_base()

class DatabaseConnection:
    """
    Manages database connection and operations
    """
    
    def __init__(self):
        """Initialize database connection"""
        self.engine = None
        self.SessionLocal = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Create SQLAlchemy engine with connection pool"""
        try:
            database_url = config.DATABASE_URL
            
            # SQLite requires special handling for threading
            if 'sqlite' in database_url:
                self.engine = create_engine(
                    database_url,
                    connect_args={"check_same_thread": False},
                    poolclass=StaticPool
                )
            else:
                # PostgreSQL and MySQL configurations
                self.engine = create_engine(
                    database_url,
                    echo=False,  # Set to True for SQL query logging
                    pool_pre_ping=True,  # Test connections before using
                    pool_recycle=3600,  # Recycle connections after 1 hour
                    max_overflow=10,
                    pool_size=5
                )
            
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info(f"Database engine initialized: {config.DB_TYPE}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            raise
    
    def get_session(self):
        """Get a new database session"""
        if self.SessionLocal is None:
            self._initialize_engine()
        return self.SessionLocal()
    
    def test_connection(self):
        """Test database connectivity"""
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                logger.info("Database connection successful")
                return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def create_tables(self):
        """Create all tables from models"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            return False
    
    def init_db(self):
        """Initialize database with schema"""
        try:
            # Read and execute schema.sql
            schema_path = os.path.join(
                os.path.dirname(__file__),
                'schema.sql'
            )
            
            if not os.path.exists(schema_path):
                logger.warning(f"Schema file not found: {schema_path}")
                return False
            
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            # Execute schema for non-SQLite databases
            if 'sqlite' not in config.DATABASE_URL:
                with self.engine.connect() as connection:
                    # Split by semicolon and execute each statement
                    statements = schema_sql.split(';')
                    for statement in statements:
                        statement = statement.strip()
                        if statement:
                            try:
                                connection.execute(text(statement))
                            except Exception as e:
                                logger.warning(f"Schema statement failed: {e}")
                    connection.commit()
            
            logger.info("Database schema initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize database schema: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        try:
            if self.engine:
                self.engine.dispose()
                logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")


# Global database connection instance
db = DatabaseConnection()


def get_db():
    """
    Dependency injection for database session
    Used with Flask/FastAPI
    """
    db_session = db.get_session()
    try:
        yield db_session
    finally:
        db_session.close()


if __name__ == '__main__':
    """
    Test database connection and schema
    Run with: python database/db_connection.py
    """
    print("\n" + "="*50)
    print("Database Connection Test")
    print("="*50)
    
    # Test connection
    print("\n[1] Testing database connection...")
    if db.test_connection():
        print("✓ Connection successful")
    else:
        print("✗ Connection failed")
        exit(1)
    
    # Initialize database
    print("\n[2] Initializing database schema...")
    if db.init_db():
        print("✓ Schema initialized successfully")
    else:
        print("✗ Schema initialization failed")
    
    print("\n" + "="*50)
    print("Database ready for use!")
    print("="*50 + "\n")
