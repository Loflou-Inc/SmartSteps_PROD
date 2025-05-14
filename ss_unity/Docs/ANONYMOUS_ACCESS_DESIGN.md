# Anonymous Client Access System: Design & Implementation Plan

**Last Updated:** May 14, 2025  
**Status:** Planned - Medium Priority

## Overview

The Anonymous Client Access System addresses a key requirement in the SmartSteps patent application: enabling clients to use the system without requiring personally identifiable information. This document outlines the design and implementation plan for creating a secure, privacy-preserving access system that aligns with patent claims while maintaining system functionality.

## Patent Alignment

The Anonymous Client Access System directly implements these aspects of the patent application:

> "To prioritize user privacy and encourage open engagement, the system will feature anonymous login capabilities and anonymous data collection protocols. No personally identifiable information will be required for user access, and all interaction data will be securely stored and anonymized for analysis and research purposes."

## Core Components

### 1. Anonymous Client Data Model (Unity-Side)

```csharp
[System.Serializable]
public enum TokenStatus
{
    Active,
    Expired,
    Revoked
}

[System.Serializable]
public class SessionPreferences
{
    public string PreferredPersona;
    public string NotificationLevel = "standard";
    public Dictionary<string, object> AccessibilitySettings = new Dictionary<string, object>();
    public string Language = "en-us";
    public string Theme = "default";
}

[System.Serializable]
public class AnonymousToken
{
    public string TokenId;
    public string DisplayAlias;  // Human-readable alias for the client
    public System.DateTime CreationTime;
    public System.DateTime? ExpirationTime;
    public System.DateTime? LastUsed;
    public TokenStatus Status = TokenStatus.Active;
    public Dictionary<string, object> Metadata = new Dictionary<string, object>();
    
    // Reference to facilitator who created the token
    public string FacilitatorId;
    
    // Session preferences
    public SessionPreferences Preferences = new SessionPreferences();
    
    // Client notes (visible only to facilitator)
    public string FacilitatorNotes;
    
    public bool IsValid()
    {
        if (Status != TokenStatus.Active)
            return false;
        if (ExpirationTime.HasValue && System.DateTime.Now > ExpirationTime.Value)
            return false;
        return true;
    }
}

[System.Serializable]
public class AnonymousClientReference
{
    public string ClientId;
    public string ActiveToken;
    public List<string> SessionRefs = new List<string>();
    public System.DateTime LastSession;
    public int SessionCount;
}
```

### 2. Anonymous Access Services (Unity-Side)

```csharp
public interface IAnonymousAccessService
{
    // Token management
    Task<AnonymousToken> GenerateTokenAsync(string facilitatorId, string aliasPrefix = null, int? expirationDays = 30);
    Task<bool> ValidateTokenAsync(string tokenId);
    Task<bool> RevokeTokenAsync(string tokenId, string facilitatorId);
    
    // Token listing and retrieval
    Task<List<AnonymousToken>> ListTokensAsync(string facilitatorId, bool includeExpired = false, bool includeRevoked = false);
    Task<AnonymousToken> GetTokenAsync(string tokenId);
    
    // Session creation
    Task<string> CreateSessionWithTokenAsync(string tokenId, string personaId = null);
    
    // QR code generation
    Task<Texture2D> GenerateTokenQRCodeAsync(string tokenId, int size = 256);
}
```

### 3. Anonymous Access UI Components

#### Facilitator Token Management

```csharp
public class TokenManagementPanel : MonoBehaviour
{
    [SerializeField] private GameObject tokenListItemPrefab;
    [SerializeField] private Transform tokenListContainer;
    [SerializeField] private Button createTokenButton;
    [SerializeField] private TMP_InputField aliasPrefixInput;
    [SerializeField] private TMP_Dropdown expirationDropdown;
    [SerializeField] private RawImage qrCodeImage;
    
    private IAnonymousAccessService anonymousAccessService;
    private List<AnonymousToken> currentTokens = new List<AnonymousToken>();
    
    // Initialization
    private void Start()
    {
        anonymousAccessService = ServiceLocator.Get<IAnonymousAccessService>();
        createTokenButton.onClick.AddListener(CreateNewToken);
        RefreshTokenList();
    }
    
    // Create new token
    private async void CreateNewToken()
    {
        string aliasPrefix = aliasPrefixInput.text;
        int expirationDays = GetExpirationDaysFromDropdown();
        
        string facilitatorId = UserManager.Instance.CurrentUserId;
        var token = await anonymousAccessService.GenerateTokenAsync(facilitatorId, aliasPrefix, expirationDays);
        
        if (token != null)
        {
            DisplayNewToken(token);
            RefreshTokenList();
        }
    }
    
    // Display token including QR code
    private async void DisplayNewToken(AnonymousToken token)
    {
        // Show token info in UI
        tokenInfoText.text = $"Token: {token.TokenId}\nAlias: {token.DisplayAlias}";
        
        // Generate and display QR code
        var qrTexture = await anonymousAccessService.GenerateTokenQRCodeAsync(token.TokenId);
        if (qrTexture != null)
        {
            qrCodeImage.texture = qrTexture;
            qrCodeImage.gameObject.SetActive(true);
        }
        
        // Show share options
        sharePanel.SetActive(true);
    }
    
    // Refresh token list
    private async void RefreshTokenList()
    {
        // Clear current list
        foreach (Transform child in tokenListContainer)
        {
            Destroy(child.gameObject);
        }
        
        // Get updated token list
        string facilitatorId = UserManager.Instance.CurrentUserId;
        currentTokens = await anonymousAccessService.ListTokensAsync(facilitatorId);
        
        // Populate list
        foreach (var token in currentTokens)
        {
            var listItem = Instantiate(tokenListItemPrefab, tokenListContainer);
            var tokenListItemComponent = listItem.GetComponent<TokenListItem>();
            tokenListItemComponent.Initialize(token, OnRevokeToken);
        }
    }
    
    // Revoke token callback
    private async void OnRevokeToken(string tokenId)
    {
        string facilitatorId = UserManager.Instance.CurrentUserId;
        bool success = await anonymousAccessService.RevokeTokenAsync(tokenId, facilitatorId);
        
        if (success)
        {
            RefreshTokenList();
        }
    }
}
```

#### Anonymous Client Login

```csharp
public class AnonymousLoginPanel : MonoBehaviour
{
    [SerializeField] private TMP_InputField tokenInput;
    [SerializeField] private Button loginButton;
    [SerializeField] private GameObject invalidTokenMessage;
    
    private IAnonymousAccessService anonymousAccessService;
    
    private void Start()
    {
        anonymousAccessService = ServiceLocator.Get<IAnonymousAccessService>();
        loginButton.onClick.AddListener(AttemptLogin);
        invalidTokenMessage.SetActive(false);
    }
    
    private async void AttemptLogin()
    {
        string tokenId = tokenInput.text.Trim();
        
        if (string.IsNullOrEmpty(tokenId))
            return;
        
        bool isValid = await anonymousAccessService.ValidateTokenAsync(tokenId);
        
        if (isValid)
        {
            var token = await anonymousAccessService.GetTokenAsync(tokenId);
            LoginSuccessful(token);
        }
        else
        {
            ShowInvalidTokenMessage();
        }
    }
    
    private async void LoginSuccessful(AnonymousToken token)
    {
        // Store token for session
        SessionManager.Instance.SetAnonymousToken(token);
        
        // Create session
        string personaId = token.Preferences.PreferredPersona;
        string sessionId = await anonymousAccessService.CreateSessionWithTokenAsync(token.TokenId, personaId);
        
        if (!string.IsNullOrEmpty(sessionId))
        {
            // Navigate to client dashboard
            ClientDashboardManager.Instance.LoadDashboard(token.DisplayAlias);
        }
    }
    
    private void ShowInvalidTokenMessage()
    {
        invalidTokenMessage.SetActive(true);
        Invoke("HideInvalidTokenMessage", 3f);
    }
    
    private void HideInvalidTokenMessage()
    {
        invalidTokenMessage.SetActive(false);
    }
}
```

### 4. Integration with Existing Systems

#### Session Management

```csharp
// Extension to existing SessionManager to support anonymous sessions
public partial class SessionManager
{
    private AnonymousToken currentAnonymousToken;
    
    public bool IsAnonymousSession => currentAnonymousToken != null;
    
    public void SetAnonymousToken(AnonymousToken token)
    {
        currentAnonymousToken = token;
    }
    
    public string GetClientIdentifier()
    {
        if (IsAnonymousSession)
            return currentAnonymousToken.DisplayAlias;
        else
            return currentUser?.FullName;
    }
    
    // Modified session creation to support anonymous mode
    public async Task<string> CreateSessionAsync(string personaId)
    {
        if (IsAnonymousSession)
        {
            // Use anonymous token to create session
            var sessionId = await anonymousAccessService.CreateSessionWithTokenAsync(
                currentAnonymousToken.TokenId, personaId);
            
            if (!string.IsNullOrEmpty(sessionId))
            {
                OnSessionCreated(sessionId);
                return sessionId;
            }
            return null;
        }
        else
        {
            // Use regular user session creation
            return await CreateUserSessionAsync(currentUser.Id, personaId);
        }
    }
}
```

#### UI Adaptations

```csharp
// Extension to UI managers to support anonymous mode
public partial class UIManager
{
    public void UpdateUIForAnonymousMode(bool isAnonymous)
    {
        // Hide/show elements based on anonymous status
        userProfileButton.gameObject.SetActive(!isAnonymous);
        userSettingsButton.gameObject.SetActive(!isAnonymous);
        anonymousIndicator.gameObject.SetActive(isAnonymous);
        
        // Update header text
        if (isAnonymous)
        {
            string alias = SessionManager.Instance.GetClientIdentifier();
            headerText.text = $"Session: {alias}";
        }
        else
        {
            headerText.text = $"Welcome, {currentUser.FirstName}";
        }
    }
}
```

## Implementation Phases

### Phase 1: Token System and API (2 weeks)
- Implement token data models
- Create API endpoints for token management
- Develop token validation service
- Build QR code generation utility
- Implement session creation with tokens

### Phase 2: Facilitator Interface (2 weeks)
- Create token management UI
- Implement token list and management
- Build token creation workflow
- Develop token sharing features
- Create token status visualization

### Phase 3: Anonymous Login (2 weeks)
- Create anonymous login screen
- Implement token validation flow
- Build session initialization for anonymous users
- Adapt UI for anonymous users
- Create token error handling

### Phase 4: Integration and Testing (2 weeks)
- Integrate with session management
- Adapt dashboard for anonymous users
- Test anonymous session workflows
- Implement analytics for anonymous sessions
- Create comprehensive error handling

## Conclusion

The Anonymous Client Access System provides a critical feature described in the patent application, enabling privacy-preserving use of the SmartSteps platform. This document outlines the Unity client implementation that will support this functionality, working in conjunction with the backend services.

By implementing this system, we will eliminate a significant gap between the current implementation and the patent claims, while enhancing the platform's appeal to privacy-conscious users and organizations.
