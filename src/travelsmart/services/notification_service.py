"""Notification service for sending updates to users."""

import asyncio
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from typing import Dict, List, Any, Optional
from loguru import logger

from ..config import settings


class NotificationService:
    """Service for sending notifications to users."""
    
    def __init__(self):
        self.smtp_server = getattr(settings, 'smtp_server', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'smtp_port', 587)
        self.smtp_username = getattr(settings, 'smtp_username', '')
        self.smtp_password = getattr(settings, 'smtp_password', '')
    
    async def send_booking_confirmation(self, user_email: str, booking_details: Dict[str, Any]):
        """Send booking confirmation email."""
        
        subject = f"Travel Booking Confirmation - {booking_details.get('confirmation_number', 'N/A')}"
        
        html_content = self._generate_booking_email_html(booking_details)
        text_content = self._generate_booking_email_text(booking_details)
        
        return await self._send_email(
            to_email=user_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
    
    async def send_booking_update(self, user_email: str, booking_id: str, status: str, message: str):
        """Send booking status update."""
        
        subject = f"Booking Update - {booking_id}"
        
        html_content = f"""
        <html>
        <body>
            <h2>Booking Status Update</h2>
            <p><strong>Booking ID:</strong> {booking_id}</p>
            <p><strong>Status:</strong> {status}</p>
            <p><strong>Message:</strong> {message}</p>
            <p>Thank you for using TravelSmart!</p>
        </body>
        </html>
        """
        
        text_content = f"""
        Booking Status Update
        
        Booking ID: {booking_id}
        Status: {status}
        Message: {message}
        
        Thank you for using TravelSmart!
        """
        
        return await self._send_email(
            to_email=user_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
    
    async def send_travel_reminder(self, user_email: str, booking_details: Dict[str, Any], days_until_travel: int):
        """Send travel reminder email."""
        
        subject = f"Travel Reminder - {days_until_travel} days until your trip!"
        
        html_content = f"""
        <html>
        <body>
            <h2>Travel Reminder</h2>
            <p>Your trip to <strong>{booking_details.get('destination', 'N/A')}</strong> is coming up in {days_until_travel} days!</p>
            
            <h3>Trip Details:</h3>
            <ul>
                <li><strong>Confirmation Number:</strong> {booking_details.get('confirmation_number', 'N/A')}</li>
                <li><strong>Destination:</strong> {booking_details.get('destination', 'N/A')}</li>
                <li><strong>Departure Date:</strong> {booking_details.get('start_date', 'N/A')}</li>
                <li><strong>Return Date:</strong> {booking_details.get('end_date', 'N/A')}</li>
            </ul>
            
            <h3>Pre-travel Checklist:</h3>
            <ul>
                <li>Check passport and visa requirements</li>
                <li>Confirm flight details</li>
                <li>Pack according to weather forecast</li>
                <li>Arrange transportation to airport</li>
                <li>Check travel insurance</li>
            </ul>
            
            <p>Have a wonderful trip!</p>
        </body>
        </html>
        """
        
        return await self._send_email(
            to_email=user_email,
            subject=subject,
            html_content=html_content
        )
    
    def _generate_booking_email_html(self, booking_details: Dict[str, Any]) -> str:
        """Generate HTML content for booking confirmation email."""
        
        flights = booking_details.get('flights', [])
        hotels = booking_details.get('hotels', [])
        total_cost = booking_details.get('total_cost', 0)
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #2E86AB; color: white; padding: 20px; text-align: center;">
                <h1>🌍 TravelSmart</h1>
                <h2>Booking Confirmation</h2>
            </div>
            
            <div style="padding: 20px;">
                <h3>Booking Details</h3>
                <p><strong>Confirmation Number:</strong> {booking_details.get('confirmation_number', 'N/A')}</p>
                <p><strong>Destination:</strong> {booking_details.get('destination', 'N/A')}</p>
                <p><strong>Travel Dates:</strong> {booking_details.get('start_date', 'N/A')} - {booking_details.get('end_date', 'N/A')}</p>
                <p><strong>Total Cost:</strong> ${total_cost:.2f}</p>
                
                {self._format_flights_html(flights)}
                {self._format_hotels_html(hotels)}
                
                <div style="background-color: #f8f9fa; padding: 15px; margin-top: 20px; border-radius: 5px;">
                    <h4>Important Information</h4>
                    <ul>
                        <li>Please arrive at the airport at least 2 hours before domestic flights and 3 hours before international flights</li>
                        <li>Check-in online to save time</li>
                        <li>Ensure your travel documents are valid</li>
                        <li>Review baggage policies</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <p>Thank you for choosing TravelSmart!</p>
                    <p style="color: #666;">Safe travels! ✈️</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _generate_booking_email_text(self, booking_details: Dict[str, Any]) -> str:
        """Generate plain text content for booking confirmation email."""
        
        flights = booking_details.get('flights', [])
        hotels = booking_details.get('hotels', [])
        total_cost = booking_details.get('total_cost', 0)
        
        text = f"""
        TravelSmart - Booking Confirmation
        
        Booking Details:
        Confirmation Number: {booking_details.get('confirmation_number', 'N/A')}
        Destination: {booking_details.get('destination', 'N/A')}
        Travel Dates: {booking_details.get('start_date', 'N/A')} - {booking_details.get('end_date', 'N/A')}
        Total Cost: ${total_cost:.2f}
        
        {self._format_flights_text(flights)}
        {self._format_hotels_text(hotels)}
        
        Important Information:
        - Please arrive at the airport at least 2 hours before domestic flights and 3 hours before international flights
        - Check-in online to save time
        - Ensure your travel documents are valid
        - Review baggage policies
        
        Thank you for choosing TravelSmart!
        Safe travels!
        """
        
        return text
    
    def _format_flights_html(self, flights: List[Dict]) -> str:
        """Format flights for HTML email."""
        if not flights:
            return ""
        
        html = "<h4>Flight Details</h4>"
        for flight in flights:
            html += f"""
            <div style="border: 1px solid #ddd; padding: 10px; margin: 10px 0; border-radius: 5px;">
                <p><strong>{flight.get('airline', 'N/A')} {flight.get('flight_number', 'N/A')}</strong></p>
                <p>{flight.get('origin', 'N/A')} → {flight.get('destination', 'N/A')}</p>
                <p>Departure: {flight.get('departure_time', 'N/A')} | Arrival: {flight.get('arrival_time', 'N/A')}</p>
                <p>Price: ${flight.get('price', 0):.2f}</p>
            </div>
            """
        
        return html
    
    def _format_hotels_html(self, hotels: List[Dict]) -> str:
        """Format hotels for HTML email."""
        if not hotels:
            return ""
        
        html = "<h4>Hotel Details</h4>"
        for hotel in hotels:
            html += f"""
            <div style="border: 1px solid #ddd; padding: 10px; margin: 10px 0; border-radius: 5px;">
                <p><strong>{hotel.get('name', 'N/A')}</strong></p>
                <p>Rating: {hotel.get('rating', 'N/A')}/5 ⭐</p>
                <p>Location: {hotel.get('location', 'N/A')}</p>
                <p>Price per night: ${hotel.get('price_per_night', 0):.2f}</p>
            </div>
            """
        
        return html
    
    def _format_flights_text(self, flights: List[Dict]) -> str:
        """Format flights for plain text email."""
        if not flights:
            return ""
        
        text = "Flight Details:\n"
        for flight in flights:
            text += f"""
        {flight.get('airline', 'N/A')} {flight.get('flight_number', 'N/A')}
        {flight.get('origin', 'N/A')} → {flight.get('destination', 'N/A')}
        Departure: {flight.get('departure_time', 'N/A')} | Arrival: {flight.get('arrival_time', 'N/A')}
        Price: ${flight.get('price', 0):.2f}
        
            """
        
        return text
    
    def _format_hotels_text(self, hotels: List[Dict]) -> str:
        """Format hotels for plain text email."""
        if not hotels:
            return ""
        
        text = "Hotel Details:\n"
        for hotel in hotels:
            text += f"""
        {hotel.get('name', 'N/A')}
        Rating: {hotel.get('rating', 'N/A')}/5
        Location: {hotel.get('location', 'N/A')}
        Price per night: ${hotel.get('price_per_night', 0):.2f}
        
            """
        
        return text
    
    async def _send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None):
        """Send email using SMTP."""
        
        if not self.smtp_username or not self.smtp_password:
            logger.warning("SMTP credentials not configured - email not sent")
            return False
        
        try:
            msg = MimeMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_username
            msg['To'] = to_email
            
            if text_content:
                msg.attach(MimeText(text_content, 'plain'))
            
            msg.attach(MimeText(html_content, 'html'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False


# Global notification service instance
notification_service = NotificationService()
