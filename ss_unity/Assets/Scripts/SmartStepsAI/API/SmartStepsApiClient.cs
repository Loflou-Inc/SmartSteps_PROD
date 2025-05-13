using System;
using System.Collections;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.Networking;
using Newtonsoft.Json;

namespace SmartSteps.AI
{
    /// <summary>
    /// Client for the Smart Steps AI API.
    /// Provides methods for interacting with the API endpoints.
    /// </summary>
    public class SmartStepsApiClient
    {
        private readonly string _baseUrl;
        private string _authToken;
        private readonly MonoBehaviour _coroutineRunner;
        
        private const string API_PREFIX = "/api/v1";
        
        /// <summary>
        /// Create a new Smart Steps API client.
        /// </summary>
        /// <param name="baseUrl">Base URL of the API server</param>
        /// <param name="coroutineRunner">MonoBehaviour to run coroutines on</param>
        public SmartStepsApiClient(string baseUrl, MonoBehaviour coroutineRunner)
        {
            _baseUrl = baseUrl.TrimEnd('/');
            _coroutineRunner = coroutineRunner;
        }
        
        /// <summary>
        /// Authenticate with the API and get an access token.
        /// </summary>
        /// <param name="username">Username</param>
        /// <param name="password">Password</param>
        /// <param name="callback">Callback function called when authentication completes</param>
        public void Authenticate(string username, string password, Action<bool, string> callback)
        {
            _coroutineRunner.StartCoroutine(AuthenticateCoroutine(username, password, callback));
        }
        
        private IEnumerator AuthenticateCoroutine(string username, string password, Action<bool, string> callback)
        {
            string url = $"{_baseUrl}{API_PREFIX}/auth/token";
            
            WWWForm form = new WWWForm();
            form.AddField("username", username);
            form.AddField("password", password);
            
            using (UnityWebRequest request = UnityWebRequest.Post(url, form))
            {
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    var response = JsonConvert.DeserializeObject<AuthResponse>(request.downloadHandler.text);
                    _authToken = response.access_token;
                    callback?.Invoke(true, null);
                }
                else
                {
                    callback?.Invoke(false, request.error);
                }
            }
        }
        
        #region Session Management
        
        /// <summary>
        /// Create a new therapy session.
        /// </summary>
        /// <param name="sessionData">Session creation data</param>
        /// <param name="callback">Callback function called when operation completes</param>
        public void CreateSession(SessionCreateRequest sessionData, Action<SessionResponse, string> callback)
        {
            _coroutineRunner.StartCoroutine(CreateSessionCoroutine(sessionData, callback));
        }
        
        private IEnumerator CreateSessionCoroutine(SessionCreateRequest sessionData, Action<SessionResponse, string> callback)
        {
            string url = $"{_baseUrl}{API_PREFIX}/sessions";
            string jsonData = JsonConvert.SerializeObject(sessionData);
            
            using (UnityWebRequest request = CreateJsonRequest(url, "POST", jsonData))
            {
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    var response = JsonConvert.DeserializeObject<SessionResponse>(request.downloadHandler.text);
                    callback?.Invoke(response, null);
                }
                else
                {
                    callback?.Invoke(null, request.error);
                }
            }
        }
        
        /// <summary>
        /// Get a list of therapy sessions.
        /// </summary>
        /// <param name="clientId">Optional client ID filter</param>
        /// <param name="personaId">Optional persona ID filter</param>
        /// <param name="limit">Maximum number of sessions to return</param>
        /// <param name="offset">Number of sessions to skip</param>
        /// <param name="callback">Callback function called when operation completes</param>
        public void ListSessions(string clientId, string personaId, int limit, int offset, Action<SessionListResponse, string> callback)
        {
            _coroutineRunner.StartCoroutine(ListSessionsCoroutine(clientId, personaId, limit, offset, callback));
        }
        
        private IEnumerator ListSessionsCoroutine(string clientId, string personaId, int limit, int offset, Action<SessionListResponse, string> callback)
        {
            StringBuilder urlBuilder = new StringBuilder($"{_baseUrl}{API_PREFIX}/sessions?limit={limit}&offset={offset}");
            
            if (!string.IsNullOrEmpty(clientId))
            {
                urlBuilder.Append($"&client_id={UnityWebRequest.EscapeURL(clientId)}");
            }
            
            if (!string.IsNullOrEmpty(personaId))
            {
                urlBuilder.Append($"&persona_id={UnityWebRequest.EscapeURL(personaId)}");
            }
            
            using (UnityWebRequest request = CreateAuthenticatedRequest(urlBuilder.ToString(), "GET"))
            {
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    var response = JsonConvert.DeserializeObject<SessionListResponse>(request.downloadHandler.text);
                    callback?.Invoke(response, null);
                }
                else
                {
                    callback?.Invoke(null, request.error);
                }
            }
        }
        
        /// <summary>
        /// Get a specific therapy session.
        /// </summary>
        /// <param name="sessionId">Session ID</param>
        /// <param name="callback">Callback function called when operation completes</param>
        public void GetSession(string sessionId, Action<SessionResponse, string> callback)
        {
            _coroutineRunner.StartCoroutine(GetSessionCoroutine(sessionId, callback));
        }
        
        private IEnumerator GetSessionCoroutine(string sessionId, Action<SessionResponse, string> callback)
        {
            string url = $"{_baseUrl}{API_PREFIX}/sessions/{sessionId}";
            
            using (UnityWebRequest request = CreateAuthenticatedRequest(url, "GET"))
            {
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    var response = JsonConvert.DeserializeObject<SessionResponse>(request.downloadHandler.text);
                    callback?.Invoke(response, null);
                }
                else
                {
                    callback?.Invoke(null, request.error);
                }
            }
        }
        
        /// <summary>
        /// Update a therapy session.
        /// </summary>
        /// <param name="sessionId">Session ID</param>
        /// <param name="sessionData">Session update data</param>
        /// <param name="callback">Callback function called when operation completes</param>
        public void UpdateSession(string sessionId, SessionUpdateRequest sessionData, Action<SessionResponse, string> callback)
        {
            _coroutineRunner.StartCoroutine(UpdateSessionCoroutine(sessionId, sessionData, callback));
        }
        
        private IEnumerator UpdateSessionCoroutine(string sessionId, SessionUpdateRequest sessionData, Action<SessionResponse, string> callback)
        {
            string url = $"{_baseUrl}{API_PREFIX}/sessions/{sessionId}";
            string jsonData = JsonConvert.SerializeObject(sessionData);
            
            using (UnityWebRequest request = CreateJsonRequest(url, "PATCH", jsonData))
            {
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    var response = JsonConvert.DeserializeObject<SessionResponse>(request.downloadHandler.text);
                    callback?.Invoke(response, null);
                }
                else
                {
                    callback?.Invoke(null, request.error);
                }
            }
        }
        
        /// <summary>
        /// Delete a therapy session.
        /// </summary>
        /// <param name="sessionId">Session ID</param>
        /// <param name="callback">Callback function called when operation completes</param>
        public void DeleteSession(string sessionId, Action<bool, string> callback)
        {
            _coroutineRunner.StartCoroutine(DeleteSessionCoroutine(sessionId, callback));
        }
        
        private IEnumerator DeleteSessionCoroutine(string sessionId, Action<bool, string> callback)
        {
            string url = $"{_baseUrl}{API_PREFIX}/sessions/{sessionId}";
            
            using (UnityWebRequest request = CreateAuthenticatedRequest(url, "DELETE"))
            {
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    callback?.Invoke(true, null);
                }
                else
                {
                    callback?.Invoke(false, request.error);
                }
            }
        }
        
        #endregion
        
        #region Conversation Management
        
        /// <summary>
        /// Send a message in a therapy session.
        /// </summary>
        /// <param name="sessionId">Session ID</param>
        /// <param name="messageData">Message creation data</param>
        /// <param name="callback">Callback function called when operation completes</param>
        public void SendMessage(string sessionId, MessageCreateRequest messageData, Action<MessageResponse, string> callback)
        {
            _coroutineRunner.StartCoroutine(SendMessageCoroutine(sessionId, messageData, callback));
        }
        
        private IEnumerator SendMessageCoroutine(string sessionId, MessageCreateRequest messageData, Action<MessageResponse, string> callback)
        {
            string url = $"{_baseUrl}{API_PREFIX}/conversations/{sessionId}/messages";
            string jsonData = JsonConvert.SerializeObject(messageData);
            
            using (UnityWebRequest request = CreateJsonRequest(url, "POST", jsonData))
            {
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    var response = JsonConvert.DeserializeObject<MessageResponse>(request.downloadHandler.text);
                    callback?.Invoke(response, null);
                }
                else
                {
                    callback?.Invoke(null, request.error);
                }
            }
        }
        
        /// <summary>
        /// Get conversation history for a therapy session.
        /// </summary>
        /// <param name="sessionId">Session ID</param>
        /// <param name="limit">Maximum number of messages to return</param>
        /// <param name="beforeMessageId">Only return messages before this message ID</param>
        /// <param name="callback">Callback function called when operation completes</param>
        public void GetConversationHistory(string sessionId, int limit, string beforeMessageId, Action<MessageListResponse, string> callback)
        {
            _coroutineRunner.StartCoroutine(GetConversationHistoryCoroutine(sessionId, limit, beforeMessageId, callback));
        }
        
        private IEnumerator GetConversationHistoryCoroutine(string sessionId, int limit, string beforeMessageId, Action<MessageListResponse, string> callback)
        {
            StringBuilder urlBuilder = new StringBuilder($"{_baseUrl}{API_PREFIX}/conversations/{sessionId}/messages?limit={limit}");
            
            if (!string.IsNullOrEmpty(beforeMessageId))
            {
                urlBuilder.Append($"&before={UnityWebRequest.EscapeURL(beforeMessageId)}");
            }
            
            using (UnityWebRequest request = CreateAuthenticatedRequest(urlBuilder.ToString(), "GET"))
            {
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    var response = JsonConvert.DeserializeObject<MessageListResponse>(request.downloadHandler.text);
                    callback?.Invoke(response, null);
                }
                else
                {
                    callback?.Invoke(null, request.error);
                }
            }
        }
        
        /// <summary>
        /// Export conversation for a therapy session.
        /// </summary>
        /// <param name="sessionId">Session ID</param>
        /// <param name="format">Export format (json, markdown, text, html)</param>
        /// <param name="callback">Callback function called when operation completes</param>
        public void ExportConversation(string sessionId, string format, Action<ConversationExportResponse, string> callback)
        {
            _coroutineRunner.StartCoroutine(ExportConversationCoroutine(sessionId, format, callback));
        }
        
        private IEnumerator ExportConversationCoroutine(string sessionId, string format, Action<ConversationExportResponse, string> callback)
        {
            string url = $"{_baseUrl}{API_PREFIX}/conversations/{sessionId}/export?format={format}";
            
            using (UnityWebRequest request = CreateAuthenticatedRequest(url, "GET"))
            {
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    var response = JsonConvert.DeserializeObject<ConversationExportResponse>(request.downloadHandler.text);
                    callback?.Invoke(response, null);
                }
                else
                {
                    callback?.Invoke(null, request.error);
                }
            }
        }
        
        #endregion
        
        #region Analysis
        
        /// <summary>
        /// Analyze a therapy session.
        /// </summary>
        /// <param name="sessionId">Session ID</param>
        /// <param name="depth">Analysis depth (basic, standard, deep)</param>
        /// <param name="callback">Callback function called when operation completes</param>
        public void AnalyzeSession(string sessionId, string depth, Action<SessionAnalysisResponse, string> callback)
        {
            _coroutineRunner.StartCoroutine(AnalyzeSessionCoroutine(sessionId, depth, callback));
        }
        
        private IEnumerator AnalyzeSessionCoroutine(string sessionId, string depth, Action<SessionAnalysisResponse, string> callback)
        {
            string url = $"{_baseUrl}{API_PREFIX}/analysis/sessions/{sessionId}?depth={depth}";
            
            using (UnityWebRequest request = CreateAuthenticatedRequest(url, "GET"))
            {
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    var response = JsonConvert.DeserializeObject<SessionAnalysisResponse>(request.downloadHandler.text);
                    callback?.Invoke(response, null);
                }
                else
                {
                    callback?.Invoke(null, request.error);
                }
            }
        }
        
        /// <summary>
        /// Get insights for a client.
        /// </summary>
        /// <param name="clientId">Client ID</param>
        /// <param name="timeframe">Timeframe for insights (recent, month, year, all)</param>
        /// <param name="limit">Maximum number of insights to return</param>
        /// <param name="callback">Callback function called when operation completes</param>
        public void GetClientInsights(string clientId, string timeframe, int limit, Action<InsightListResponse, string> callback)
        {
            _coroutineRunner.StartCoroutine(GetClientInsightsCoroutine(clientId, timeframe, limit, callback));
        }
        
        private IEnumerator GetClientInsightsCoroutine(string clientId, string timeframe, int limit, Action<InsightListResponse, string> callback)
        {
            string url = $"{_baseUrl}{API_PREFIX}/analysis/insights/client/{clientId}?timeframe={timeframe}&limit={limit}";
            
            using (UnityWebRequest request = CreateAuthenticatedRequest(url, "GET"))
            {
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    var response = JsonConvert.DeserializeObject<InsightListResponse>(request.downloadHandler.text);
                    callback?.Invoke(response, null);
                }
                else
                {
                    callback?.Invoke(null, request.error);
                }
            }
        }
        
        /// <summary>
        /// Generate a client report.
        /// </summary>
        /// <param name="clientId">Client ID</param>
        /// <param name="format">Report format (json, markdown, html, pdf)</param>
        /// <param name="timeframe">Timeframe for report (recent, month, year, all)</param>
        /// <param name="template">Optional report template name</param>
        /// <param name="callback">Callback function called when operation completes</param>
        public void GenerateClientReport(string clientId, string format, string timeframe, string template, Action<ReportResponse, string> callback)
        {
            _coroutineRunner.StartCoroutine(GenerateClientReportCoroutine(clientId, format, timeframe, template, callback));
        }
        
        private IEnumerator GenerateClientReportCoroutine(string clientId, string format, string timeframe, string template, Action<ReportResponse, string> callback)
        {
            StringBuilder urlBuilder = new StringBuilder($"{_baseUrl}{API_PREFIX}/analysis/reports/client/{clientId}?format={format}&timeframe={timeframe}");
            
            if (!string.IsNullOrEmpty(template))
            {
                urlBuilder.Append($"&template={UnityWebRequest.EscapeURL(template)}");
            }
            
            using (UnityWebRequest request = CreateAuthenticatedRequest(urlBuilder.ToString(), "GET"))
            {
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    var response = JsonConvert.DeserializeObject<ReportResponse>(request.downloadHandler.text);
                    callback?.Invoke(response, null);
                }
                else
                {
                    callback?.Invoke(null, request.error);
                }
            }
        }
        
        /// <summary>
        /// Get progress data for a client.
        /// </summary>
        /// <param name="clientId">Client ID</param>
        /// <param name="timeframe">Timeframe for progress data (recent, month, year, all)</param>
        /// <param name="metrics">Specific metrics to include</param>
        /// <param name="callback">Callback function called when operation completes</param>
        public void GetClientProgress(string clientId, string timeframe, string[] metrics, Action<ProgressResponse, string> callback)
        {
            _coroutineRunner.StartCoroutine(GetClientProgressCoroutine(clientId, timeframe, metrics, callback));
        }
        
        private IEnumerator GetClientProgressCoroutine(string clientId, string timeframe, string[] metrics, Action<ProgressResponse, string> callback)
        {
            StringBuilder urlBuilder = new StringBuilder($"{_baseUrl}{API_PREFIX}/analysis/progress/client/{clientId}?timeframe={timeframe}");
            
            if (metrics != null && metrics.Length > 0)
            {
                foreach (var metric in metrics)
                {
                    urlBuilder.Append($"&metrics={UnityWebRequest.EscapeURL(metric)}");
                }
            }
            
            using (UnityWebRequest request = CreateAuthenticatedRequest(urlBuilder.ToString(), "GET"))
            {
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    var response = JsonConvert.DeserializeObject<ProgressResponse>(request.downloadHandler.text);
                    callback?.Invoke(response, null);
                }
                else
                {
                    callback?.Invoke(null, request.error);
                }
            }
        }
        
        #endregion
        
        #region Persona Management
        
        /// <summary>
        /// Get a list of available personas.
        /// </summary>
        /// <param name="role">Optional role filter</param>
        /// <param name="expertise">Optional expertise filter</param>
        /// <param name="limit">Maximum number of personas to return</param>
        /// <param name="offset">Number of personas to skip</param>
        /// <param name="callback">Callback function called when operation completes</param>
        public void ListPersonas(string role, string expertise, int limit, int offset, Action<PersonaListResponse, string> callback)
        {
            _coroutineRunner.StartCoroutine(ListPersonasCoroutine(role, expertise, limit, offset, callback));
        }
        
        private IEnumerator ListPersonasCoroutine(string role, string expertise, int limit, int offset, Action<PersonaListResponse, string> callback)
        {
            StringBuilder urlBuilder = new StringBuilder($"{_baseUrl}{API_PREFIX}/personas?limit={limit}&offset={offset}");
            
            if (!string.IsNullOrEmpty(role))
            {
                urlBuilder.Append($"&role={UnityWebRequest.EscapeURL(role)}");
            }
            
            if (!string.IsNullOrEmpty(expertise))
            {
                urlBuilder.Append($"&expertise={UnityWebRequest.EscapeURL(expertise)}");
            }
            
            using (UnityWebRequest request = CreateAuthenticatedRequest(urlBuilder.ToString(), "GET"))
            {
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    var response = JsonConvert.DeserializeObject<PersonaListResponse>(request.downloadHandler.text);
                    callback?.Invoke(response, null);
                }
                else
                {
                    callback?.Invoke(null, request.error);
                }
            }
        }
        
        /// <summary>
        /// Get a specific persona.
        /// </summary>
        /// <param name="personaId">Persona ID</param>
        /// <param name="callback">Callback function called when operation completes</param>
        public void GetPersona(string personaId, Action<PersonaResponse, string> callback)
        {
            _coroutineRunner.StartCoroutine(GetPersonaCoroutine(personaId, callback));
        }
        
        private IEnumerator GetPersonaCoroutine(string personaId, Action<PersonaResponse, string> callback)
        {
            string url = $"{_baseUrl}{API_PREFIX}/personas/{personaId}";
            
            using (UnityWebRequest request = CreateAuthenticatedRequest(url, "GET"))
            {
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    var response = JsonConvert.DeserializeObject<PersonaResponse>(request.downloadHandler.text);
                    callback?.Invoke(response, null);
                }
                else
                {
                    callback?.Invoke(null, request.error);
                }
            }
        }
        
        #endregion
        
        #region Helper Methods
        
        private UnityWebRequest CreateAuthenticatedRequest(string url, string method)
        {
            UnityWebRequest request = new UnityWebRequest(url, method);
            request.downloadHandler = new DownloadHandlerBuffer();
            
            if (!string.IsNullOrEmpty(_authToken))
            {
                request.SetRequestHeader("Authorization", $"Bearer {_authToken}");
            }
            
            return request;
        }
        
        private UnityWebRequest CreateJsonRequest(string url, string method, string jsonData)
        {
            UnityWebRequest request = new UnityWebRequest(url, method);
            request.downloadHandler = new DownloadHandlerBuffer();
            
            if (!string.IsNullOrEmpty(jsonData))
            {
                byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);
                request.uploadHandler = new UploadHandlerRaw(bodyRaw);
                request.SetRequestHeader("Content-Type", "application/json");
            }
            
            if (!string.IsNullOrEmpty(_authToken))
            {
                request.SetRequestHeader("Authorization", $"Bearer {_authToken}");
            }
            
            return request;
        }
        
        #endregion
    }
}
