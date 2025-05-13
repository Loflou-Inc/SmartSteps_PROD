using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

namespace SmartSteps.AI.Examples
{
    /// <summary>
    /// Example component for demonstrating Smart Steps AI conversation in Unity.
    /// </summary>
    public class AIConversationExample : MonoBehaviour
    {
        [Header("UI References")]
        [SerializeField] private TMP_InputField _messageInput;
        [SerializeField] private Button _sendButton;
        [SerializeField] private ScrollRect _conversationScroll;
        [SerializeField] private Transform _messageContainer;
        [SerializeField] private GameObject _clientMessagePrefab;
        [SerializeField] private GameObject _aiMessagePrefab;
        
        [Header("API Configuration")]
        [SerializeField] private string _apiUrl = "http://localhost:8000";
        [SerializeField] private string _username = "therapist";
        [SerializeField] private string _password = "password";
        
        [Header("Session Configuration")]
        [SerializeField] private string _sessionTitle = "Example Session";
        [SerializeField] private string _defaultPersonaId = "";
        [SerializeField] private TMP_Dropdown _personaDropdown;
        [SerializeField] private Button _createSessionButton;
        [SerializeField] private Button _refreshPersonasButton;
        
        private SmartStepsAIManager _aiManager;
        private List<MessageResponse> _messages = new List<MessageResponse>();
        
        private void Awake()
        {
            // Initialize UI components
            _sendButton.onClick.AddListener(OnSendButtonClicked);
            _createSessionButton.onClick.AddListener(OnCreateSessionButtonClicked);
            _refreshPersonasButton.onClick.AddListener(OnRefreshPersonasButtonClicked);
            
            // Disable send button until we have a session
            _sendButton.interactable = false;
        }
        
        private void Start()
        {
            // Get the AI manager
            _aiManager = SmartStepsAIManager.Instance;
            
            // Set up API URL if different from default
            if (!string.IsNullOrEmpty(_apiUrl) && _apiUrl != "http://localhost:8000")
            {
                _aiManager.SetApiUrl(_apiUrl);
            }
            
            // Register event listeners
            _aiManager.OnAuthenticationChanged += OnAuthenticationChanged;
            _aiManager.OnMessageReceived += OnMessageReceived;
            _aiManager.OnPersonaListUpdated += OnPersonaListUpdated;
            _aiManager.OnCurrentSessionChanged += OnCurrentSessionChanged;
            _aiManager.OnError += OnAIError;
            
            // Log in to the API
            _aiManager.Login(_username, _password);
        }
        
        private void OnDestroy()
        {
            // Unregister event listeners
            if (_aiManager != null)
            {
                _aiManager.OnAuthenticationChanged -= OnAuthenticationChanged;
                _aiManager.OnMessageReceived -= OnMessageReceived;
                _aiManager.OnPersonaListUpdated -= OnPersonaListUpdated;
                _aiManager.OnCurrentSessionChanged -= OnCurrentSessionChanged;
                _aiManager.OnError -= OnAIError;
            }
        }
        
        #region Event Handlers
        
        private void OnAuthenticationChanged(bool isAuthenticated)
        {
            Debug.Log($"Authentication changed: {isAuthenticated}");
            
            if (isAuthenticated)
            {
                // Refresh the persona list
                _aiManager.LoadAvailablePersonas();
            }
            else
            {
                // Reset UI
                _createSessionButton.interactable = false;
                _sendButton.interactable = false;
                _personaDropdown.ClearOptions();
            }
        }
        
        private void OnPersonaListUpdated(List<PersonaResponse> personas)
        {
            Debug.Log($"Persona list updated: {personas.Count} personas");
            
            // Update persona dropdown
            _personaDropdown.ClearOptions();
            
            List<TMP_Dropdown.OptionData> options = new List<TMP_Dropdown.OptionData>();
            
            foreach (var persona in personas)
            {
                options.Add(new TMP_Dropdown.OptionData($"{persona.name} ({persona.role})"));
                
                // If this is the default persona, select it
                if (persona.id == _defaultPersonaId)
                {
                    _personaDropdown.value = options.Count - 1;
                }
            }
            
            _personaDropdown.AddOptions(options);
            
            // Enable create session button
            _createSessionButton.interactable = personas.Count > 0;
        }
        
        private void OnCurrentSessionChanged(SessionResponse session)
        {
            Debug.Log($"Current session changed: {session.title}");
            
            // Enable send button
            _sendButton.interactable = true;
            
            // Load conversation history
            _aiManager.GetConversationHistory(50, (messages, error) =>
            {
                if (messages != null)
                {
                    // Clear existing messages
                    ClearMessages();
                    
                    // Add messages in reverse order (oldest first)
                    messages.Reverse();
                    foreach (var message in messages)
                    {
                        AddMessageToUI(message);
                    }
                }
            });
        }
        
        private void OnMessageReceived(MessageResponse message)
        {
            // Add message to UI
            AddMessageToUI(message);
        }
        
        private void OnAIError(string error)
        {
            Debug.LogError($"AI Error: {error}");
            // Could show error message to user here
        }
        
        #endregion
        
        #region UI Handlers
        
        private void OnSendButtonClicked()
        {
            if (string.IsNullOrEmpty(_messageInput.text))
                return;
            
            // Send message
            _aiManager.SendMessage(_messageInput.text);
            
            // Clear input field
            _messageInput.text = "";
            _messageInput.ActivateInputField();
        }
        
        private void OnCreateSessionButtonClicked()
        {
            if (_aiManager.AvailablePersonas.Count == 0)
                return;
            
            // Get selected persona
            var selectedPersona = _aiManager.AvailablePersonas[_personaDropdown.value];
            
            // Create session
            _aiManager.CreateSession(_sessionTitle, selectedPersona.id);
        }
        
        private void OnRefreshPersonasButtonClicked()
        {
            if (_aiManager.IsAuthenticated())
            {
                _aiManager.LoadAvailablePersonas();
            }
        }
        
        #endregion
        
        #region UI Helpers
        
        private void AddMessageToUI(MessageResponse message)
        {
            // Create message object
            GameObject messagePrefab = message.sender_type == "client" ? _clientMessagePrefab : _aiMessagePrefab;
            GameObject messageObject = Instantiate(messagePrefab, _messageContainer);
            
            // Set message text
            TMP_Text messageText = messageObject.GetComponentInChildren<TMP_Text>();
            if (messageText != null)
            {
                messageText.text = message.content;
            }
            
            // Add to message list
            _messages.Add(message);
            
            // Scroll to bottom
            StartCoroutine(ScrollToBottom());
        }
        
        private void ClearMessages()
        {
            // Clear message list
            _messages.Clear();
            
            // Clear UI
            foreach (Transform child in _messageContainer)
            {
                Destroy(child.gameObject);
            }
        }
        
        private IEnumerator ScrollToBottom()
        {
            // Wait for end of frame to ensure layout has been updated
            yield return new WaitForEndOfFrame();
            
            // Scroll to bottom
            _conversationScroll.normalizedPosition = new Vector2(0, 0);
        }
        
        #endregion
    }
}
