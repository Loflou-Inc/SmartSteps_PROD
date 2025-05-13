"""
FastAPI dependencies for the Smart Steps AI API.

This module provides dependency injection functions for the FastAPI routes.
"""

from typing import Optional

from fastapi import Depends, HTTPException, Request, status

from smart_steps_ai.config import ConfigManager
from smart_steps_ai.session import SessionManager
from smart_steps_ai.persona import PersonaManager
from smart_steps_ai.provider import ProviderManager
from smart_steps_ai.analysis import AnalysisManager
from smart_steps_ai.memory import MemoryManager
from smart_steps_ai.persistence import PersistenceManager

# Try to import enhanced security components
try:
    from .security.enhanced_auth import jwt_bearer, verify_scope
except ImportError:
    # Fallback to standard auth
    from .security.auth import get_current_user


# Singletons for dependency injection
_config_manager = None
_session_manager = None
_persona_manager = None
_provider_manager = None
_analysis_manager = None
_memory_manager = None
_persistence_manager = None
_conversation_handler = None

def get_config_manager():
    """Get or create the config manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def get_persistence_manager(config_manager=Depends(get_config_manager)):
    """Get or create the persistence manager instance."""
    global _persistence_manager
    if _persistence_manager is None:
        _persistence_manager = PersistenceManager(config_manager)
    return _persistence_manager

# Enhanced security dependencies
async def get_current_user(request: Request):
    """Get the current authenticated user with enhanced security."""
    try:
        # Try to use enhanced security
        credentials = await jwt_bearer(request)
        return request.state.user
    except NameError:
        # Fallback to standard auth
        from .security.auth import get_current_user as standard_get_user
        return await standard_get_user()

def require_scope(scope: str):
    """Require a specific scope for access."""
    try:
        # Try to use enhanced security
        return verify_scope(scope)
    except NameError:
        # Fallback implementation
        async def _verify_scope(request: Request):
            user = getattr(request.state, "user", None)
            if user and "scopes" in user and scope in user["scopes"]:
                return True
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required scope: {scope}"
            )
        return _verify_scope

def get_persona_manager(config_manager=Depends(get_config_manager)):
    """Get or create the persona manager instance."""
    global _persona_manager
    if _persona_manager is None:
        # FIXED: PersonaManager only accepts a directory path, not config_manager + persistence_manager
        personas_dir = config_manager.get().paths.personas_dir
        _persona_manager = PersonaManager(personas_dir)
    return _persona_manager

def get_memory_manager(config_manager=Depends(get_config_manager)):
    """Get or create the memory manager instance."""
    global _memory_manager
    if _memory_manager is None:
        # FIXED: MemoryManager only accepts a directory path, not config_manager + persistence_manager
        memory_dir = config_manager.get().memory.memory_dir
        _memory_manager = MemoryManager(memory_dir)
    return _memory_manager

def get_provider_manager(
    config_manager=Depends(get_config_manager),
    persona_manager=Depends(get_persona_manager)
):
    """Get or create the provider manager instance."""
    global _provider_manager
    if _provider_manager is None:
        _provider_manager = ProviderManager(config_manager, persona_manager)
    return _provider_manager

def get_session_manager(
    config_manager=Depends(get_config_manager),
    persistence_manager=Depends(get_persistence_manager),
    memory_manager=Depends(get_memory_manager)
):
    """Get or create the session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager(config_manager, persistence_manager, memory_manager)
    return _session_manager

def get_analysis_manager(
    config_manager=Depends(get_config_manager),
    session_manager=Depends(get_session_manager),
    provider_manager=Depends(get_provider_manager)
):
    """Get or create the analysis manager instance."""
    global _analysis_manager
    if _analysis_manager is None:
        _analysis_manager = AnalysisManager(config_manager, session_manager, provider_manager)
    return _analysis_manager

def get_conversation_handler(
    session_manager=Depends(get_session_manager),
    provider_manager=Depends(get_provider_manager),
    memory_manager=Depends(get_memory_manager)
):
    """Get or create the conversation handler instance."""
    global _conversation_handler
    if _conversation_handler is None:
        # The ConversationHandler only takes these specific parameters
        from smart_steps_ai.session import ConversationHandler
        _conversation_handler = ConversationHandler(
            session_manager=session_manager,
            provider_manager=provider_manager,
            memory_manager=memory_manager
        )
    return _conversation_handler
