"""Database utilities for TravelSmart application."""

import sqlite3
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from loguru import logger

from ..config import settings


class DatabaseManager:
    """Simple SQLite database manager for TravelSmart."""
    
    def __init__(self, db_path: str = "travelsmart.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create bookings table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS bookings (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    destination TEXT NOT NULL,
                    departure_city TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    booking_data TEXT,
                    total_cost REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
                
                # Create user_preferences table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id TEXT PRIMARY KEY,
                    preferences TEXT,
                    travel_history TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
                
                # Create travel_cache table for caching API responses
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS travel_cache (
                    cache_key TEXT PRIMARY KEY,
                    data TEXT,
                    expires_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def save_booking(self, booking_data: Dict[str, Any]) -> str:
        """Save booking to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                INSERT INTO bookings 
                (id, user_id, destination, departure_city, start_date, end_date, 
                 status, booking_data, total_cost) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    booking_data["booking_id"],
                    booking_data.get("user_id", "anonymous"),
                    booking_data.get("destination", ""),
                    booking_data.get("departure_city", ""),
                    booking_data.get("start_date", ""),
                    booking_data.get("end_date", ""),
                    booking_data.get("status", "pending"),
                    json.dumps(booking_data),
                    booking_data.get("total_cost", 0.0)
                ))
                
                conn.commit()
                logger.info(f"Booking {booking_data['booking_id']} saved successfully")
                return booking_data["booking_id"]
                
        except Exception as e:
            logger.error(f"Error saving booking: {e}")
            raise
    
    def get_booking(self, booking_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve booking by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                SELECT booking_data FROM bookings WHERE id = ?
                """, (booking_id,))
                
                result = cursor.fetchone()
                if result:
                    return json.loads(result[0])
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving booking {booking_id}: {e}")
            return None
    
    def update_booking_status(self, booking_id: str, status: str) -> bool:
        """Update booking status."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                UPDATE bookings 
                SET status = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
                """, (status, booking_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error updating booking status: {e}")
            return False
    
    def get_user_bookings(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all bookings for a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                SELECT booking_data FROM bookings 
                WHERE user_id = ? 
                ORDER BY created_at DESC
                """, (user_id,))
                
                results = cursor.fetchall()
                return [json.loads(row[0]) for row in results]
                
        except Exception as e:
            logger.error(f"Error retrieving user bookings: {e}")
            return []
    
    def save_to_cache(self, cache_key: str, data: Dict[str, Any], expires_hours: int = 24):
        """Save data to cache with expiration."""
        try:
            expires_at = datetime.now().timestamp() + (expires_hours * 3600)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                INSERT OR REPLACE INTO travel_cache 
                (cache_key, data, expires_at) 
                VALUES (?, ?, ?)
                """, (cache_key, json.dumps(data), expires_at))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error saving to cache: {e}")
    
    def get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve data from cache if not expired."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                SELECT data FROM travel_cache 
                WHERE cache_key = ? AND expires_at > ?
                """, (cache_key, datetime.now().timestamp()))
                
                result = cursor.fetchone()
                if result:
                    return json.loads(result[0])
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving from cache: {e}")
            return None
    
    def save_user_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """Save user travel preferences."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                INSERT OR REPLACE INTO user_preferences 
                (user_id, preferences, updated_at) 
                VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (user_id, json.dumps(preferences)))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error saving user preferences: {e}")
    
    def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user travel preferences."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                SELECT preferences FROM user_preferences WHERE user_id = ?
                """, (user_id,))
                
                result = cursor.fetchone()
                if result:
                    return json.loads(result[0])
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving user preferences: {e}")
            return None


# Global database instance
db_manager = DatabaseManager()