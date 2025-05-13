using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace SmartSteps.UI
{
    /// <summary>
    /// Base class for all UI screens in the Smart Steps application.
    /// </summary>
    public abstract class UIScreen : MonoBehaviour
    {
        [Header("Screen Configuration")]
        [SerializeField] private string _screenId;
        [SerializeField] private string _screenTitle;
        [SerializeField] private bool _canGoBack = true;
        
        [Header("Common UI Elements")]
        [SerializeField] protected CanvasGroup _canvasGroup;
        [SerializeField] protected Button _backButton;
        
        // Reference to the UI manager
        protected UIManager _uiManager;
        
        // Data passed to this screen
        protected object _screenData;
        
        /// <summary>
        /// Gets the unique identifier for this screen.
        /// </summary>
        public string ScreenId => _screenId;
        
        /// <summary>
        /// Gets the title of this screen.
        /// </summary>
        public string ScreenTitle => _screenTitle;
        
        /// <summary>
        /// Gets whether the user can navigate back from this screen.
        /// </summary>
        public bool CanGoBack => _canGoBack;
        
        /// <summary>
        /// Initialize the screen.
        /// </summary>
        /// <param name="uiManager">The UI manager.</param>
        public virtual void Initialize(UIManager uiManager)
        {
            _uiManager = uiManager;
            
            // Make sure we have a canvas group
            if (_canvasGroup == null)
            {
                _canvasGroup = GetComponent<CanvasGroup>();
                
                if (_canvasGroup == null)
                {
                    _canvasGroup = gameObject.AddComponent<CanvasGroup>();
                }
            }
            
            // Hook up back button if available
            if (_backButton != null)
            {
                _backButton.onClick.AddListener(OnBackButtonClicked);
            }
            
            OnInitialize();
        }
        
        /// <summary>
        /// Called when the screen is initialized.
        /// Override this to perform screen-specific initialization.
        /// </summary>
        protected virtual void OnInitialize()
        {
            // Override in derived classes
        }
        
        /// <summary>
        /// Called when the screen is shown.
        /// </summary>
        /// <param name="data">Optional data passed to the screen.</param>
        public virtual void OnScreenShow(object data = null)
        {
            _screenData = data;
            _canvasGroup.interactable = true;
            _canvasGroup.blocksRaycasts = true;
            
            // Update back button visibility
            if (_backButton != null)
            {
                _backButton.gameObject.SetActive(_canGoBack);
            }
        }
        
        /// <summary>
        /// Called when the screen is hidden.
        /// </summary>
        public virtual void OnScreenHide()
        {
            _canvasGroup.interactable = false;
            _canvasGroup.blocksRaycasts = false;
        }
        
        /// <summary>
        /// Called when the back button is clicked.
        /// </summary>
        protected virtual void OnBackButtonClicked()
        {
            if (_uiManager != null && _canGoBack)
            {
                _uiManager.NavigateBack();
            }
        }
        
        /// <summary>
        /// Navigate to another screen.
        /// </summary>
        /// <param name="screenId">The ID of the target screen.</param>
        /// <param name="data">Optional data to pass to the screen.</param>
        protected void NavigateTo(string screenId, object data = null)
        {
            if (_uiManager != null)
            {
                _uiManager.NavigateToScreen(screenId, true, data);
            }
        }
    }
}
