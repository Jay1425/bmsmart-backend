"""
Notification service for Firebase Cloud Messaging integration.
"""
import os
import logging
from typing import Optional, Dict, Any

try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    logging.warning("firebase-admin not installed. Push notifications will be disabled.")


class NotificationService:
    """Service class for sending push notifications via Firebase Cloud Messaging."""
    
    _initialized = False
    
    @classmethod
    def initialize(cls, credentials_path: Optional[str] = None):
        """
        Initialize Firebase Admin SDK.
        
        Args:
            credentials_path: Path to Firebase credentials JSON file
        """
        if not FIREBASE_AVAILABLE:
            logging.warning("Firebase Admin SDK not available. Skipping initialization.")
            return
        
        if cls._initialized:
            return
        
        try:
            # Check if credentials file exists
            if credentials_path and os.path.exists(credentials_path):
                cred = credentials.Certificate(credentials_path)
                firebase_admin.initialize_app(cred)
                cls._initialized = True
                logging.info(f"Firebase initialized successfully with credentials from {credentials_path}")
            else:
                logging.warning(f"Firebase credentials not found at {credentials_path}. Push notifications disabled.")
        except Exception as e:
            logging.error(f"Failed to initialize Firebase: {str(e)}")
    
    @classmethod
    def send_push_notification(
        cls,
        device_token: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send a push notification to a device via FCM.
        
        Args:
            device_token: FCM device token of the recipient
            title: Notification title
            message: Notification body message
            data: Optional additional data to send with notification
        
        Returns:
            dict: Response with success status and message ID or error
        """
        if not FIREBASE_AVAILABLE:
            return {
                'success': False,
                'error': 'Firebase Admin SDK not installed'
            }
        
        if not cls._initialized:
            return {
                'success': False,
                'error': 'Firebase not initialized. Check credentials file.'
            }
        
        if not device_token:
            return {
                'success': False,
                'error': 'Device token is required'
            }
        
        try:
            # Create notification payload
            notification = messaging.Notification(
                title=title,
                body=message
            )
            
            # Create message with notification and optional data
            fcm_message = messaging.Message(
                notification=notification,
                data=data or {},
                token=device_token
            )
            
            # Send message
            response = messaging.send(fcm_message)
            
            logging.info(f"Push notification sent successfully: {response}")
            return {
                'success': True,
                'message_id': response
            }
            
        except messaging.UnregisteredError:
            logging.error(f"Device token is invalid or unregistered: {device_token}")
            return {
                'success': False,
                'error': 'Device token is invalid or unregistered'
            }
        except messaging.InvalidArgumentError as e:
            logging.error(f"Invalid argument for FCM: {str(e)}")
            return {
                'success': False,
                'error': f'Invalid argument: {str(e)}'
            }
        except Exception as e:
            logging.error(f"Failed to send push notification: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @classmethod
    def send_visitor_arrival_notification(
        cls,
        device_token: str,
        visitor_name: str,
        flat_number: str
    ) -> Dict[str, Any]:
        """
        Send a visitor arrival notification to a resident.
        
        Args:
            device_token: FCM device token of the resident
            visitor_name: Name of the visitor
            flat_number: Flat/apartment number of the resident
        
        Returns:
            dict: Response with success status
        """
        title = "Visitor Arrived"
        message = f"{visitor_name} is waiting at the gate for {flat_number}"
        
        data = {
            'type': 'visitor_arrival',
            'visitor_name': visitor_name,
            'flat_number': flat_number
        }
        
        return cls.send_push_notification(
            device_token=device_token,
            title=title,
            message=message,
            data=data
        )
