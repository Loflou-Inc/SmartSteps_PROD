using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace SmartSteps.AI
{
    /// <summary>
    /// Main manager for the Smart Steps AI integration in Unity.
    /// Provides access to AI personas, session management, and conversation handlers.
    /// </summary>
    public class SmartStepsAIManager : MonoBehaviour
    {
        #region Singleton
        
        private static SmartStepsAIManager _instance;
        
        /// <summary>
        /// Singleton instance of the Smart Steps AI Manager.
        /// </summary>
        public static SmartStepsAIManager Instance
        {
            get
            {
                if (_instance == null)
                {
                    GameObject go = new GameObject("SmartStepsAIManager");
                    _instance = go.AddComponent<SmartStepsAIManager>();
                    DontDestroyOnLoad(go);
                }
                return _instance;
            }
        }
        
        private void Awake()
        {
            if (_instance != null && _instance != this)
            {
                Destroy(gameObject);
                return;
            }
            
            _instance = this;
            DontDestroyOnLoad(gameObject);
            
            // Initialize the manager
            Initialize();
        }
        
        #endregion
        
        #region Public Properties
        
        /// <summary>
        /// API client for interacting with the Smart Steps AI system.
        /// </summary>
        public SmartStepsApiClient ApiClient { get; private set; }
        
        /// <summary>
        /// Current active therapy session.
        /// </summary>
        public SessionResponse CurrentSession { get; private set; }
        
        /// <summary>
        /// Currently selected persona.
        /// </summary>
        public PersonaResponse CurrentPersona { get; private set; }
        
        /// <summary>
        /// List of available personas.
        /// </summary>
        public List<PersonaResponse> AvailablePersonas { get; private set; } = new List<PersonaResponse>();
        
        /// <summary>
        /// Event fired when the authentication state changes.
        /// </summary>
        public event Action<bool> OnAuthenticationChanged;
        
        /// <summary>
        /// Event fired when a new message is received.
        /// </summary>
        public event Action<MessageResponse> OnMessageReceived;
        
        /// <summary>
        /// Event fired when the session list is updated.
        /// </summary>
        public event Action<List<SessionResponse>> OnSessionListUpdated;
        
        /// <summary>
        /// Event fired when the persona list is updated.
        /// </summary>
        public event Action<List<PersonaResponse>> OnPersonaListUpdated;
        
        /// <summary>
        /// Event fired when the current session changes.
        /// </summary>
        public event Action<SessionResponse> OnCurrentSessionChanged;
        
        /// <summary>
        /// Event fired when an error occurs.
        /// </summary>
        public event Action<string> OnError;
        
        #endregion
        
        #region Configuration Properties
        
        [SerializeField] private string _apiUrl = "http://localhost:8000";
        [SerializeField] private string _username = "therapist";
        [SerializeField] private string _password = "password";
        [SerializeField] private bool _autoLogin = true;
        
        #endregion
        
        #region Private Fields
        
        private bool _isInitialized = false;
        private bool _isAuthenticated = false;
        private string _clientId = "unity_client";
        
        #endregion
        
        #region Initialization
        
        /// <summary>
        /// Initialize the manager.
        /// </summary>
        private void Initialize()
        {
            if (_isInitialized)
                return;
            
            Debug.Log("Initializing SmartStepsAIManager");
            
            // Create the API client
            ApiClient = new SmartStepsApiClient(_apiUrl, this);
            
            // Set up the client ID
            _clientId = SystemInfo.deviceUniqueIdentifier;
            
            // Auto-login if configured
            if (_autoLogin)
            {
                Login(_username, _password);
            }
            
            _isInitialized = true;
        }
        
        #endregion
        
        #region Authentication
        
        /// <summary>
        /// Log in to the Smart Steps AI system.
        /// </summary>
        /// <param name="username">Username</param>
        /// <param name="password">Password</param>
        public void Login(string username, string password)
        {
            Debug.Log($"Logging in as {username}");
            
            ApiClient.Authenticate(username, password, (success, error) =>
            {
                if (success)
                {
                    _isAuthenticated = true;
                    OnAuthenticationChanged?.Invoke(true);
                    
                    // Load initial data
                    LoadAvailablePersonas();
                    LoadSessionList();
                }
                else
                {
                    Debug.LogError($"Login failed: {error}");
                    _isAuthenticated = false;
                    OnAuthenticationChanged?.Invoke(false);
                    OnError?.Invoke($"Login failed: {error}");
                }
            });
        }
        
        /// <summary>
        /// Check if the user is currently authenticated.
        /// </summary>
        public bool IsAuthenticated()
        {
            return _isAuthenticated;
        }
        
        #endregion
        
        #region Session Management
        
        /// <summary>
        /// Load the list of available therapy sessions.
        /// </summary>
        public void LoadSessionList()
        {
            if (!_isAuthenticated)
            {
                OnError?.Invoke("Not authenticated");
                return;
            }
            
            ApiClient.ListSessions(_clientId, null, 50, 0, (response, error) =>
            {
                if (response != null)
                {
                    OnSessionListUpdated?.Invoke(response.sessions);
                }
                else
                {
                    Debug.LogError($"Failed to load sessions: {error}");
                    OnError?.Invoke($"Failed to load sessions: {error}");
                }
            });
        }
        
        /// <summary>
        /// Create a new therapy session.
        /// </summary>
        /// <param name="title">Session title</param>
        /// <param name="personaId">Persona ID</param>
        /// <param name="metadata">Additional session metadata</param>
        public void CreateSession(string title, string personaId, Dictionary<string, object> metadata = null)
        {
            if (!_isAuthenticated)
            {
                OnError?.Invoke("Not authenticated");
                return;
            }
            
            var sessionData = new SessionCreateRequest
            {
                title = title,
                client_id = _clientId,
                persona_id = personaId,
                metadata = metadata ?? new Dictionary<string, object>()
            };
            
            ApiClient.CreateSession(sessionData, (response, error) =>
            {
                if (response != null)
                {
                    CurrentSession = response;
                    OnCurrentSessionChanged?.Invoke(response);
                    LoadSessionList();  // Refresh the session list
                }
                else
                {
                    Debug.LogError($"Failed to create session: {error}");
                    OnError?.Invoke($"Failed to create session: {error}");
                }
            });
        }
        
        /// <summary>
        /// Load a specific therapy session and set it as the current session.
        /// </summary>
        /// <param name="sessionId">Session ID</param>
        public void LoadSession(string sessionId)
        {
            if (!_isAuthenticated)
            {
                OnError?.Invoke("Not authenticated");
                return;
            }
            
            ApiClient.GetSession(sessionId, (response, error) =>
            {
                if (response != null)
                {
                    CurrentSession = response;
                    OnCurrentSessionChanged?.Invoke(response);
                    
                    // Load the session's persona
                    LoadPersona(response.persona_id);
                }
                else
                {
                    Debug.LogError($"Failed to load session: {error}");
                    OnError?.Invoke($"Failed to load session: {error}");
                }
            });
        }
        
        /// <summary>
        /// Send a message in the current session.
        /// </summary>
        /// <param name="content">Message content</param>
        /// <param name="metadata">Additional message metadata</param>
        public void SendMessage(string content, Dictionary<string, object> metadata = null)
        {
            if (!_isAuthenticated)
            {
                OnError?.Invoke("Not authenticated");
                return;
            }
            
            if (CurrentSession == null)
            {
                OnError?.Invoke("No active session");
                return;
            }
            
            var messageData = new MessageCreateRequest
            {
                content = content,
                client_id = _clientId,
                metadata = metadata ?? new Dictionary<string, object>()
            };
            
            ApiClient.SendMessage(CurrentSession.id, messageData, (response, error) =>
            {
                if (response != null)
                {
                    OnMessageReceived?.Invoke(response);
                }
                else
                {
                    Debug.LogError($"Failed to send message: {error}");
                    OnError?.Invoke($"Failed to send message: {error}");
                }
            });
        }
        
        /// <summary>
        /// Get the conversation history for the current session.
        /// </summary>
        /// <param name="limit">Maximum number of messages to return</param>
        /// <param name="callback">Callback function with the message list</param>
        public void GetConversationHistory(int limit, Action<List<MessageResponse>, string> callback)
        {
            if (!_isAuthenticated)
            {
                OnError?.Invoke("Not authenticated");
                callback?.Invoke(null, "Not authenticated");
                return;
            }
            
            if (CurrentSession == null)
            {
                OnError?.Invoke("No active session");
                callback?.Invoke(null, "No active session");
                return;
            }
            
            ApiClient.GetConversationHistory(CurrentSession.id, limit, null, (response, error) =>
            {
                if (response != null)
                {
                    callback?.Invoke(response.messages, null);
                }
                else
                {
                    Debug.LogError($"Failed to get conversation history: {error}");
                    OnError?.Invoke($"Failed to get conversation history: {error}");
                    callback?.Invoke(null, error);
                }
            });
        }
        
        #endregion
        
        #region Persona Management
        
        /// <summary>
        /// Load the list of available personas.
        /// </summary>
        public void LoadAvailablePersonas()
        {
            if (!_isAuthenticated)
            {
                OnError?.Invoke("Not authenticated");
                return;
            }
            
            ApiClient.ListPersonas(null, null, 50, 0, (response, error) =>
            {
                if (response != null)
                {
                    AvailablePersonas = response.personas;
                    OnPersonaListUpdated?.Invoke(response.personas);
                }
                else
                {
                    Debug.LogError($"Failed to load personas: {error}");
                    OnError?.Invoke($"Failed to load personas: {error}");
                }
            });
        }
        
        /// <summary>
        /// Load a specific persona and set it as the current persona.
        /// </summary>
        /// <param name="personaId">Persona ID</param>
        public void LoadPersona(string personaId)
        {
            if (!_isAuthenticated)
            {
                OnError?.Invoke("Not authenticated");
                return;
            }
            
            ApiClient.GetPersona(personaId, (response, error) =>
            {
                if (response != null)
                {
                    CurrentPersona = response;
                }
                else
                {
                    Debug.LogError($"Failed to load persona: {error}");
                    OnError?.Invoke($"Failed to load persona: {error}");
                }
            });
        }
        
        #endregion
        
        #region Analysis
        
        /// <summary>
        /// Analyze the current session.
        /// </summary>
        /// <param name="depth">Analysis depth (basic, standard, deep)</param>
        /// <param name="callback">Callback function with the analysis results</param>
        public void AnalyzeCurrentSession(string depth, Action<SessionAnalysisResponse, string> callback)
        {
            if (!_isAuthenticated)
            {
                OnError?.Invoke("Not authenticated");
                callback?.Invoke(null, "Not authenticated");
                return;
            }
            
            if (CurrentSession == null)
            {
                OnError?.Invoke("No active session");
                callback?.Invoke(null, "No active session");
                return;
            }
            
            ApiClient.AnalyzeSession(CurrentSession.id, depth, callback);
        }
        
        /// <summary>
        /// Get insights for the current client.
        /// </summary>
        /// <param name="timeframe">Timeframe for insights (recent, month, year, all)</param>
        /// <param name="limit">Maximum number of insights to return</param>
        /// <param name="callback">Callback function with the insights</param>
        public void GetClientInsights(string timeframe, int limit, Action<List<InsightResponse>, string> callback)
        {
            if (!_isAuthenticated)
            {
                OnError?.Invoke("Not authenticated");
                callback?.Invoke(null, "Not authenticated");
                return;
            }
            
            ApiClient.GetClientInsights(_clientId, timeframe, limit, (response, error) =>
            {
                if (response != null)
                {
                    callback?.Invoke(response.insights, null);
                }
                else
                {
                    Debug.LogError($"Failed to get client insights: {error}");
                    OnError?.Invoke($"Failed to get client insights: {error}");
                    callback?.Invoke(null, error);
                }
            });
        }
        
        /// <summary>
        /// Generate a report for the current client.
        /// </summary>
        /// <param name="format">Report format (json, markdown, html, pdf)</param>
        /// <param name="timeframe">Timeframe for report (recent, month, year, all)</param>
        /// <param name="callback">Callback function with the report</param>
        public void GenerateClientReport(string format, string timeframe, Action<ReportResponse, string> callback)
        {
            if (!_isAuthenticated)
            {
                OnError?.Invoke("Not authenticated");
                callback?.Invoke(null, "Not authenticated");
                return;
            }
            
            ApiClient.GenerateClientReport(_clientId, format, timeframe, null, callback);
        }
        
        #endregion
        
        #region Utilities
        
        /// <summary>
        /// Set the API URL.
        /// </summary>
        /// <param name="url">API URL</param>
        public void SetApiUrl(string url)
        {
            _apiUrl = url;
            ApiClient = new SmartStepsApiClient(_apiUrl, this);
            _isAuthenticated = false;
            OnAuthenticationChanged?.Invoke(false);
        }
        
        /// <summary>
        /// Set the client ID.
        /// </summary>
        /// <param name="clientId">Client ID</param>
        public void SetClientId(string clientId)
        {
            _clientId = clientId;
        }
        
        #endregion
    }
}
