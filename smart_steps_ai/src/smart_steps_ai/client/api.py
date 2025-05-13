"""
Smart Steps AI Client Library

This module provides a simple client library for interacting with the Smart Steps AI API.
"""

import json
import os
import logging
from typing import Dict, List, Optional, Union, Any
from urllib.parse import urljoin

import requests

# Configure logging
logger = logging.getLogger(__name__)

class APIClient:
    """
    Client for the Smart Steps AI API.
    
    This class provides methods for interacting with the Smart Steps AI API,
    handling authentication, requests, and responses.
    """
    
    def __init__(
        self,
        base_url: str = "http://127.0.0.1:9500",
        api_key: Optional[str] = None,
        timeout: int = 30,
        verify_ssl: bool = True
    ):
        """
        Initialize the API client.
        
        Args:
            base_url (str): Base URL of the API (default: "http://127.0.0.1:9500")
            api_key (Optional[str]): API key for authentication (default: None)
                If None, looks for SMART_STEPS_API_KEY environment variable
            timeout (int): Request timeout in seconds (default: 30)
            verify_ssl (bool): Whether to verify SSL certificates (default: True)
        """
        self.base_url = base_url.rstrip("/")
        
        # Get API key from environment if not provided
        self.api_key = api_key or os.environ.get("SMART_STEPS_API_KEY")
        if not self.api_key:
            logger.warning("No API key provided. Authentication will fail.")
        
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        
        if self.api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}"
            })
    
    def _make_url(self, endpoint: str) -> str:
        """
        Create a full URL from an endpoint.
        
        Args:
            endpoint (str): API endpoint
            
        Returns:
            str: Full URL
        """
        # Ensure endpoint starts with /
        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"
        
        return urljoin(self.base_url, endpoint)
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle API response.
        
        Args:
            response (requests.Response): Response from the API
            
        Returns:
            Dict[str, Any]: Parsed response
            
        Raises:
            requests.HTTPError: If the response status code is not 2xx
        """
        if not response.ok:
            # Try to parse error response
            try:
                error_data = response.json()
                logger.error(f"API error: {error_data}")
            except Exception:
                logger.error(f"API error: {response.text}")
            
            # Raise exception
            response.raise_for_status()
        
        # Parse JSON response
        try:
            return response.json()
        except ValueError:
            logger.warning("Response is not valid JSON")
            return {"raw_response": response.text}
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a GET request to the API.
        
        Args:
            endpoint (str): API endpoint
            params (Optional[Dict[str, Any]]): Query parameters (default: None)
            
        Returns:
            Dict[str, Any]: API response
        """
        url = self._make_url(endpoint)
        logger.debug(f"GET {url}")
        
        response = self.session.get(
            url,
            params=params,
            timeout=self.timeout,
            verify=self.verify_ssl,
        )
        
        return self._handle_response(response)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a POST request to the API.
        
        Args:
            endpoint (str): API endpoint
            data (Optional[Dict[str, Any]]): Request data (default: None)
            
        Returns:
            Dict[str, Any]: API response
        """
        url = self._make_url(endpoint)
        logger.debug(f"POST {url}")
        
        response = self.session.post(
            url,
            json=data,
            timeout=self.timeout,
            verify=self.verify_ssl,
        )
        
        return self._handle_response(response)
    
    def patch(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a PATCH request to the API.
        
        Args:
            endpoint (str): API endpoint
            data (Optional[Dict[str, Any]]): Request data (default: None)
            
        Returns:
            Dict[str, Any]: API response
        """
        url = self._make_url(endpoint)
        logger.debug(f"PATCH {url}")
        
        response = self.session.patch(
            url,
            json=data,
            timeout=self.timeout,
            verify=self.verify_ssl,
        )
        
        return self._handle_response(response)
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """
        Make a DELETE request to the API.
        
        Args:
            endpoint (str): API endpoint
            
        Returns:
            Dict[str, Any]: API response
        """
        url = self._make_url(endpoint)
        logger.debug(f"DELETE {url}")
        
        response = self.session.delete(
            url,
            timeout=self.timeout,
            verify=self.verify_ssl,
        )
        
        return self._handle_response(response)
    
    # Authentication
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Log in to the API.
        
        Args:
            username (str): Username
            password (str): Password
            
        Returns:
            Dict[str, Any]: API response with authentication token
        """
        data = {
            "username": username,
            "password": password,
        }
        
        response = self.post("/api/v1/auth/login", data)
        
        # Update authorization header with token
        if "access_token" in response:
            self.api_key = response["access_token"]
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}"
            })
        
        return response
    
    # Health check
    def health_check(self) -> Dict[str, Any]:
        """
        Check API health.
        
        Returns:
            Dict[str, Any]: API health status
        """
        return self.get("/health")
    
    # Personas
    def list_personas(self) -> Dict[str, Any]:
        """
        List available personas.
        
        Returns:
            Dict[str, Any]: List of personas
        """
        return self.get("/api/v1/personas")
    
    def get_persona(self, persona_id: str) -> Dict[str, Any]:
        """
        Get persona details.
        
        Args:
            persona_id (str): Persona ID
            
        Returns:
            Dict[str, Any]: Persona details
        """
        return self.get(f"/api/v1/personas/{persona_id}")
    
    # Sessions
    def create_session(
        self,
        client_id: str,
        persona_id: str,
        title: str,
        provider_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new session.
        
        Args:
            client_id (str): Client ID
            persona_id (str): Persona ID
            title (str): Session title
            provider_id (Optional[str]): Provider ID (default: None)
            metadata (Optional[Dict[str, Any]]): Session metadata (default: None)
            
        Returns:
            Dict[str, Any]: Created session
        """
        data = {
            "client_id": client_id,
            "persona_id": persona_id,
            "title": title,
        }
        
        if provider_id:
            data["provider_id"] = provider_id
        
        if metadata:
            data["metadata"] = metadata
        
        return self.post("/api/v1/sessions", data)
    
    def list_sessions(
        self,
        client_id: Optional[str] = None,
        persona_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        List sessions.
        
        Args:
            client_id (Optional[str]): Filter by client ID (default: None)
            persona_id (Optional[str]): Filter by persona ID (default: None)
            limit (int): Maximum number of sessions to return (default: 50)
            offset (int): Number of sessions to skip (default: 0)
            
        Returns:
            Dict[str, Any]: List of sessions
        """
        params = {
            "limit": limit,
            "offset": offset,
        }
        
        if client_id:
            params["client_id"] = client_id
        
        if persona_id:
            params["persona_id"] = persona_id
        
        return self.get("/api/v1/sessions", params)
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        Get session details.
        
        Args:
            session_id (str): Session ID
            
        Returns:
            Dict[str, Any]: Session details
        """
        return self.get(f"/api/v1/sessions/{session_id}")
    
    def update_session(
        self,
        session_id: str,
        title: Optional[str] = None,
        status: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update a session.
        
        Args:
            session_id (str): Session ID
            title (Optional[str]): New session title (default: None)
            status (Optional[str]): New session status (default: None)
            metadata (Optional[Dict[str, Any]]): Updated metadata (default: None)
            
        Returns:
            Dict[str, Any]: Updated session
        """
        data = {}
        
        if title:
            data["title"] = title
        
        if status:
            data["status"] = status
        
        if metadata:
            data["metadata"] = metadata
        
        return self.patch(f"/api/v1/sessions/{session_id}", data)
    
    def delete_session(self, session_id: str) -> Dict[str, Any]:
        """
        Delete a session.
        
        Args:
            session_id (str): Session ID
            
        Returns:
            Dict[str, Any]: Deletion result
        """
        return self.delete(f"/api/v1/sessions/{session_id}")
    
    # Conversations
    def send_message(
        self,
        session_id: str,
        message: str,
        provider_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a message in a session.
        
        Args:
            session_id (str): Session ID
            message (str): Message content
            provider_id (Optional[str]): Provider ID (default: None)
            
        Returns:
            Dict[str, Any]: Response with assistant message
        """
        data = {
            "message": message,
        }
        
        if provider_id:
            data["provider_id"] = provider_id
        
        return self.post(f"/api/v1/conversations/{session_id}", data)
    
    def get_conversation_history(self, session_id: str) -> Dict[str, Any]:
        """
        Get conversation history for a session.
        
        Args:
            session_id (str): Session ID
            
        Returns:
            Dict[str, Any]: Conversation history
        """
        return self.get(f"/api/v1/conversations/{session_id}")
    
    # Analysis
    def analyze_session(self, session_id: str) -> Dict[str, Any]:
        """
        Analyze a session.
        
        Args:
            session_id (str): Session ID
            
        Returns:
            Dict[str, Any]: Session analysis
        """
        return self.post(f"/api/v1/analysis/sessions/{session_id}")
    
    def get_session_analysis(self, session_id: str) -> Dict[str, Any]:
        """
        Get session analysis.
        
        Args:
            session_id (str): Session ID
            
        Returns:
            Dict[str, Any]: Session analysis
        """
        return self.get(f"/api/v1/analysis/sessions/{session_id}")
    
    def get_session_report(
        self,
        session_id: str,
        format: str = "markdown",
    ) -> Dict[str, Any]:
        """
        Get session report.
        
        Args:
            session_id (str): Session ID
            format (str): Report format (default: "markdown")
                Supported formats: markdown, text, html, json
            
        Returns:
            Dict[str, Any]: Session report
        """
        params = {
            "format": format,
        }
        
        return self.get(f"/api/v1/analysis/sessions/{session_id}/report", params)
