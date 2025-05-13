using UnityEngine;
using UnityEditor;
using System.IO;
using System.Collections.Generic;

namespace SmartSteps.Editor
{
    /// <summary>
    /// Custom editor tools for the Smart Steps project.
    /// </summary>
    public static class SmartStepsEditorTools
    {
        [MenuItem("Smart Steps/Create Default Folders")]
        public static void CreateDefaultFolders()
        {
            List<string> folders = new List<string>
            {
                "Animations",
                "Audio/Music",
                "Audio/SFX",
                "Materials",
                "Models",
                "Prefabs/UI",
                "Prefabs/Modules",
                "Resources",
                "Scenes",
                "Scripts/Core",
                "Scripts/UI",
                "Scripts/Modules",
                "Scripts/Utils",
                "Shaders",
                "Textures",
                "ThirdParty"
            };

            foreach (string folder in folders)
            {
                if (!AssetDatabase.IsValidFolder("Assets/" + folder))
                {
                    string[] folderLevels = folder.Split('/');
                    string currentFolderPath = "Assets";
                    
                    foreach (string level in folderLevels)
                    {
                        string newFolderPath = Path.Combine(currentFolderPath, level);
                        
                        if (!AssetDatabase.IsValidFolder(newFolderPath))
                        {
                            AssetDatabase.CreateFolder(currentFolderPath, level);
                        }
                        
                        currentFolderPath = newFolderPath;
                    }
                }
            }
            
            AssetDatabase.Refresh();
            Debug.Log("Created default folders for Smart Steps project");
        }
        
        [MenuItem("Smart Steps/Create Module Template")]
        public static void CreateModuleTemplate()
        {
            string moduleName = EditorInputDialog.Show("Create Module", "Enter module name:", "NewModule");
            
            if (string.IsNullOrEmpty(moduleName))
            {
                return;
            }
            
            // Create module folders
            if (!AssetDatabase.IsValidFolder($"Assets/Scripts/Modules/{moduleName}"))
            {
                AssetDatabase.CreateFolder("Assets/Scripts/Modules", moduleName);
            }
            
            if (!AssetDatabase.IsValidFolder($"Assets/Prefabs/Modules/{moduleName}"))
            {
                if (!AssetDatabase.IsValidFolder("Assets/Prefabs/Modules"))
                {
                    AssetDatabase.CreateFolder("Assets/Prefabs", "Modules");
                }
                
                AssetDatabase.CreateFolder("Assets/Prefabs/Modules", moduleName);
            }
            
            // Create module manager script
            string managerScriptPath = $"Assets/Scripts/Modules/{moduleName}/{moduleName}Manager.cs";
            string managerScriptContent = 
$@"using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using SmartSteps.Models;

namespace SmartSteps.Modules.{moduleName}
{{
    /// <summary>
    /// Manager class for the {moduleName} module.
    /// </summary>
    public class {moduleName}Manager : MonoBehaviour
    {{
        [Header("Configuration")]
        [SerializeField] private bool _isDebugMode = false;
        
        // Singleton pattern
        private static {moduleName}Manager _instance;
        
        /// <summary>
        /// Gets the singleton instance of the {moduleName}Manager.
        /// </summary>
        public static {moduleName}Manager Instance
        {{
            get {{ return _instance; }}
        }}
        
        private void Awake()
        {{
            if (_instance != null && _instance != this)
            {{
                Destroy(gameObject);
                return;
            }}
            
            _instance = this;
            DontDestroyOnLoad(gameObject);
            
            Initialize();
        }}
        
        /// <summary>
        /// Initialize the module.
        /// </summary>
        private void Initialize()
        {{
            Debug.Log(""{moduleName} module initialized"");
            
            // TODO: Module-specific initialization
        }}
        
        /// <summary>
        /// Activate the module for a specific client.
        /// </summary>
        /// <param name=""clientId"">The ID of the client.</param>
        public void ActivateForClient(string clientId)
        {{
            // TODO: Activate module functionality for this client
            Debug.Log($""{moduleName} module activated for client {{clientId}}"");
        }}
        
        /// <summary>
        /// Handle a session event.
        /// </summary>
        /// <param name=""sessionData"">The current session data.</param>
        /// <param name=""eventType"">The type of event.</param>
        /// <param name=""eventData"">Additional event data.</param>
        public void HandleSessionEvent(SessionData sessionData, string eventType, Dictionary<string, object> eventData)
        {{
            // TODO: Process session events
            Debug.Log($""{moduleName} module handling event: {{eventType}}"");
        }}
        
        /// <summary>
        /// Save module-specific data.
        /// </summary>
        public void SaveModuleData()
        {{
            // TODO: Save module data
            Debug.Log(""{moduleName} module data saved"");
        }}
    }}
}}";
            
            // Create module data script
            string dataScriptPath = $"Assets/Scripts/Modules/{moduleName}/{moduleName}Data.cs";
            string dataScriptContent = 
$@"using UnityEngine;
using System;
using System.Collections.Generic;

namespace SmartSteps.Modules.{moduleName}
{{
    /// <summary>
    /// Data class for the {moduleName} module.
    /// </summary>
    [Serializable]
    public class {moduleName}Data
    {{
        /// <summary>
        /// Unique identifier for this module data.
        /// </summary>
        public string Id;
        
        /// <summary>
        /// The client ID associated with this data.
        /// </summary>
        public string ClientId;
        
        /// <summary>
        /// When this data was created.
        /// </summary>
        public DateTime CreationDate;
        
        /// <summary>
        /// When this data was last modified.
        /// </summary>
        public DateTime LastModified;
        
        /// <summary>
        /// Any additional data for this module.
        /// </summary>
        public Dictionary<string, object> Metadata = new Dictionary<string, object>();
        
        /// <summary>
        /// Creates a new {moduleName} data instance.
        /// </summary>
        public {moduleName}Data()
        {{
            Id = Guid.NewGuid().ToString();
            CreationDate = DateTime.Now;
            LastModified = DateTime.Now;
        }}
    }}
}}";
            
            // Create module UI script
            string uiScriptPath = $"Assets/Scripts/Modules/{moduleName}/{moduleName}UI.cs";
            string uiScriptContent = 
$@"using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections;

namespace SmartSteps.Modules.{moduleName}
{{
    /// <summary>
    /// UI controller for the {moduleName} module.
    /// </summary>
    public class {moduleName}UI : MonoBehaviour
    {{
        [Header("UI References")]
        [SerializeField] private GameObject _mainPanel;
        [SerializeField] private TextMeshProUGUI _titleText;
        [SerializeField] private Button _closeButton;
        
        // Reference to the module manager
        private {moduleName}Manager _manager;
        
        private void Awake()
        {{
            // Find the manager
            _manager = {moduleName}Manager.Instance;
            
            // Setup UI
            if (_closeButton != null)
            {{
                _closeButton.onClick.AddListener(OnCloseButtonClicked);
            }}
        }}
        
        private void OnEnable()
        {{
            // Initialize UI state
            RefreshUI();
        }}
        
        /// <summary>
        /// Refreshes the UI with current data.
        /// </summary>
        public void RefreshUI()
        {{
            // TODO: Update UI elements with current data
            if (_titleText != null)
            {{
                _titleText.text = ""{moduleName} Module"";
            }}
        }}
        
        /// <summary>
        /// Handles the close button click.
        /// </summary>
        private void OnCloseButtonClicked()
        {{
            // TODO: Handle closing the module UI
            Debug.Log(""{moduleName} module UI closed"");
            
            if (_mainPanel != null)
            {{
                _mainPanel.SetActive(false);
            }}
        }}
    }}
}}";
            
            // Write the files
            File.WriteAllText(managerScriptPath, managerScriptContent);
            File.WriteAllText(dataScriptPath, dataScriptContent);
            File.WriteAllText(uiScriptPath, uiScriptContent);
            
            AssetDatabase.Refresh();
            Debug.Log($"Created module template for {moduleName}");
        }
        
        [MenuItem("Smart Steps/Generate Documentation")]
        public static void GenerateDocumentation()
        {
            // TODO: Implement documentation generation
            EditorUtility.DisplayDialog("Documentation Generation", 
                "This feature is not yet implemented.\n\n" +
                "It will automatically generate documentation from code comments.", 
                "OK");
        }
    }
    
    /// <summary>
    /// A simple input dialog for the Unity Editor.
    /// </summary>
    public class EditorInputDialog : EditorWindow
    {
        private string _windowTitle = "";
        private string _labelText = "";
        private string _inputText = "";
        private string _result = "";
        private bool _isDone = false;
        private bool _isCanceled = false;
        
        public static string Show(string windowTitle, string labelText, string defaultText = "")
        {
            EditorInputDialog window = ScriptableObject.CreateInstance<EditorInputDialog>();
            window._windowTitle = windowTitle;
            window._labelText = labelText;
            window._inputText = defaultText;
            window._isDone = false;
            window._isCanceled = false;
            
            window.position = new Rect(Screen.width / 2, Screen.height / 2, 250, 100);
            window.ShowModalUtility();
            
            if (window._isCanceled)
            {
                return "";
            }
            
            return window._result;
        }
        
        private void OnGUI()
        {
            titleContent = new GUIContent(_windowTitle);
            
            GUILayout.Space(10);
            GUILayout.Label(_labelText);
            GUI.SetNextControlName("InputField");
            _inputText = GUILayout.TextField(_inputText);
            
            GUI.FocusControl("InputField");
            
            GUILayout.Space(10);
            
            GUILayout.BeginHorizontal();
            GUILayout.FlexibleSpace();
            
            if (GUILayout.Button("Cancel", GUILayout.Width(100)))
            {
                _isCanceled = true;
                _isDone = true;
                Close();
            }
            
            if (GUILayout.Button("OK", GUILayout.Width(100)))
            {
                _result = _inputText;
                _isDone = true;
                Close();
            }
            
            GUILayout.EndHorizontal();
            
            if (Event.current.isKey && Event.current.keyCode == KeyCode.Return)
            {
                _result = _inputText;
                _isDone = true;
                Close();
            }
            
            if (Event.current.isKey && Event.current.keyCode == KeyCode.Escape)
            {
                _isCanceled = true;
                _isDone = true;
                Close();
            }
        }
    }
}
