using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

namespace SmartSteps.UI
{
    /// <summary>
    /// Manages the UI system for the Smart Steps application.
    /// Handles UI navigation, transitions, and state.
    /// </summary>
    public class UIManager : MonoBehaviour
    {
        #region Singleton
        
        private static UIManager _instance;
        
        /// <summary>
        /// Gets the singleton instance of the UIManager.
        /// </summary>
        public static UIManager Instance
        {
            get
            {
                if (_instance == null)
                {
                    _instance = FindObjectOfType<UIManager>();
                    
                    if (_instance == null)
                    {
                        GameObject managerObject = new GameObject("UIManager");
                        _instance = managerObject.AddComponent<UIManager>();
                        DontDestroyOnLoad(managerObject);
                    }
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
            
            Initialize();
        }
        
        #endregion
        
        #region Properties and Fields
        
        [Header("UI Components")]
        [SerializeField] private Canvas _mainCanvas;
        [SerializeField] private RectTransform _screenContainer;
        [SerializeField] private GameObject _loadingOverlay;
        [SerializeField] private TextMeshProUGUI _loadingText;
        [SerializeField] private Image _loadingProgressBar;
        
        [Header("Transitions")]
        [SerializeField] private float _transitionDuration = 0.3f;
        [SerializeField] private AnimationCurve _transitionCurve = AnimationCurve.EaseInOut(0, 0, 1, 1);
        
        [Header("Configuration")]
        [SerializeField] private bool _useAnimations = true;
        
        // Keep track of UI screens and current screen
        private Dictionary<string, UIScreen> _screens = new Dictionary<string, UIScreen>();
        private UIScreen _currentScreen;
        private UIScreen _previousScreen;
        
        // Screen history for navigation
        private Stack<UIScreen> _screenHistory = new Stack<UIScreen>();
        
        // Transition coroutine reference
        private Coroutine _transitionCoroutine;
        
        #endregion
        
        #region Initialization
        
        /// <summary>
        /// Initialize the UI system.
        /// </summary>
        private void Initialize()
        {
            Debug.Log("Initializing UI Manager");
            
            // Find all UI screens in the scene
            UIScreen[] screens = FindObjectsOfType<UIScreen>();
            
            foreach (UIScreen screen in screens)
            {
                RegisterScreen(screen);
                screen.gameObject.SetActive(false);
            }
            
            // Setup loading overlay
            if (_loadingOverlay != null)
            {
                _loadingOverlay.SetActive(false);
            }
        }
        
        /// <summary>
        /// Register a UI screen with the manager.
        /// </summary>
        /// <param name="screen">The screen to register.</param>
        public void RegisterScreen(UIScreen screen)
        {
            if (screen == null)
            {
                Debug.LogError("Attempted to register a null screen");
                return;
            }
            
            string screenId = screen.ScreenId;
            
            if (string.IsNullOrEmpty(screenId))
            {
                Debug.LogError("Screen has no ID: " + screen.gameObject.name);
                return;
            }
            
            if (_screens.ContainsKey(screenId))
            {
                Debug.LogWarning("Screen with ID already registered: " + screenId);
                return;
            }
            
            _screens[screenId] = screen;
            screen.Initialize(this);
            
            Debug.Log("Registered screen: " + screenId);
        }
        
        #endregion
        
        #region Screen Navigation
        
        /// <summary>
        /// Navigate to a screen by ID.
        /// </summary>
        /// <param name="screenId">The ID of the target screen.</param>
        /// <param name="addToHistory">Whether to add the current screen to history for back navigation.</param>
        /// <param name="data">Optional data to pass to the screen.</param>
        public void NavigateToScreen(string screenId, bool addToHistory = true, object data = null)
        {
            if (!_screens.ContainsKey(screenId))
            {
                Debug.LogError("Screen not found: " + screenId);
                return;
            }
            
            UIScreen targetScreen = _screens[screenId];
            
            if (_currentScreen != null)
            {
                if (addToHistory)
                {
                    _screenHistory.Push(_currentScreen);
                }
                
                _previousScreen = _currentScreen;
            }
            
            TransitionToScreen(targetScreen, data);
        }
        
        /// <summary>
        /// Navigate back to the previous screen.
        /// </summary>
        /// <returns>True if successfully navigated back, false if there is no previous screen.</returns>
        public bool NavigateBack()
        {
            if (_screenHistory.Count == 0)
            {
                Debug.Log("No screen history available");
                return false;
            }
            
            UIScreen previousScreen = _screenHistory.Pop();
            
            if (previousScreen != null)
            {
                _previousScreen = _currentScreen;
                TransitionToScreen(previousScreen);
                return true;
            }
            
            return false;
        }
        
        /// <summary>
        /// Transition from the current screen to a new screen.
        /// </summary>
        /// <param name="targetScreen">The screen to transition to.</param>
        /// <param name="data">Optional data to pass to the screen.</param>
        private void TransitionToScreen(UIScreen targetScreen, object data = null)
        {
            if (_transitionCoroutine != null)
            {
                StopCoroutine(_transitionCoroutine);
            }
            
            if (_useAnimations)
            {
                _transitionCoroutine = StartCoroutine(TransitionCoroutine(targetScreen, data));
            }
            else
            {
                if (_currentScreen != null)
                {
                    _currentScreen.OnScreenHide();
                    _currentScreen.gameObject.SetActive(false);
                }
                
                _currentScreen = targetScreen;
                _currentScreen.gameObject.SetActive(true);
                _currentScreen.OnScreenShow(data);
            }
        }
        
        /// <summary>
        /// Coroutine to handle animated transitions between screens.
        /// </summary>
        private IEnumerator TransitionCoroutine(UIScreen targetScreen, object data = null)
        {
            // Hide current screen with animation
            if (_currentScreen != null)
            {
                _currentScreen.OnScreenHide();
                
                CanvasGroup currentCanvasGroup = _currentScreen.GetComponent<CanvasGroup>();
                
                if (currentCanvasGroup != null)
                {
                    float startTime = Time.time;
                    float elapsedTime = 0f;
                    
                    while (elapsedTime < _transitionDuration / 2)
                    {
                        elapsedTime = Time.time - startTime;
                        float normalizedTime = elapsedTime / (_transitionDuration / 2);
                        float evaluatedTime = _transitionCurve.Evaluate(normalizedTime);
                        
                        currentCanvasGroup.alpha = 1 - evaluatedTime;
                        
                        yield return null;
                    }
                    
                    currentCanvasGroup.alpha = 0;
                }
                
                _currentScreen.gameObject.SetActive(false);
            }
            
            // Show target screen with animation
            _currentScreen = targetScreen;
            _currentScreen.gameObject.SetActive(true);
            
            CanvasGroup targetCanvasGroup = _currentScreen.GetComponent<CanvasGroup>();
            
            if (targetCanvasGroup != null)
            {
                targetCanvasGroup.alpha = 0;
                
                float startTime = Time.time;
                float elapsedTime = 0f;
                
                while (elapsedTime < _transitionDuration / 2)
                {
                    elapsedTime = Time.time - startTime;
                    float normalizedTime = elapsedTime / (_transitionDuration / 2);
                    float evaluatedTime = _transitionCurve.Evaluate(normalizedTime);
                    
                    targetCanvasGroup.alpha = evaluatedTime;
                    
                    yield return null;
                }
                
                targetCanvasGroup.alpha = 1;
            }
            
            _currentScreen.OnScreenShow(data);
            
            _transitionCoroutine = null;
        }
        
        #endregion
        
        #region Loading Overlay
        
        /// <summary>
        /// Show the loading overlay with custom text.
        /// </summary>
        /// <param name="loadingText">The text to display.</param>
        public void ShowLoading(string loadingText = "Loading...")
        {
            if (_loadingOverlay == null)
            {
                Debug.LogWarning("Loading overlay not assigned");
                return;
            }
            
            _loadingOverlay.SetActive(true);
            
            if (_loadingText != null)
            {
                _loadingText.text = loadingText;
            }
            
            if (_loadingProgressBar != null)
            {
                _loadingProgressBar.fillAmount = 0f;
            }
        }
        
        /// <summary>
        /// Update the loading progress.
        /// </summary>
        /// <param name="progress">Progress value between 0 and 1.</param>
        public void UpdateLoadingProgress(float progress)
        {
            if (_loadingProgressBar != null)
            {
                _loadingProgressBar.fillAmount = Mathf.Clamp01(progress);
            }
        }
        
        /// <summary>
        /// Hide the loading overlay.
        /// </summary>
        public void HideLoading()
        {
            if (_loadingOverlay == null)
            {
                return;
            }
            
            _loadingOverlay.SetActive(false);
        }
        
        #endregion
        
        #region Utility Methods
        
        /// <summary>
        /// Get a registered screen by ID.
        /// </summary>
        /// <param name="screenId">The ID of the screen to get.</param>
        /// <returns>The UI screen, or null if not found.</returns>
        public UIScreen GetScreen(string screenId)
        {
            if (_screens.ContainsKey(screenId))
            {
                return _screens[screenId];
            }
            
            return null;
        }
        
        /// <summary>
        /// Check if a screen with the given ID is registered.
        /// </summary>
        /// <param name="screenId">The ID to check.</param>
        /// <returns>True if the screen is registered, false otherwise.</returns>
        public bool HasScreen(string screenId)
        {
            return _screens.ContainsKey(screenId);
        }
        
        /// <summary>
        /// Get the ID of the current screen.
        /// </summary>
        /// <returns>The ID of the current screen, or null if no screen is active.</returns>
        public string GetCurrentScreenId()
        {
            return _currentScreen != null ? _currentScreen.ScreenId : null;
        }
        
        #endregion
    }
}
