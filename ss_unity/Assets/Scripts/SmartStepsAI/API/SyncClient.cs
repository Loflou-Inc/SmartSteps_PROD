using System;
using System.Collections;
using System.Collections.Generic;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;
using Newtonsoft.Json;

namespace SmartSteps.AI
{
    /// <summary>
    /// Client for the Smart Steps AI Synchronization API.
    /// Provides methods for data synchronization between the Unity client and the API server.
    /// </summary>
    public class SyncClient
    {
        private readonly string _baseUrl;
        private string _authToken;
        private readonly MonoBehaviour _coroutineRunner;
        
        private const string API_PREFIX = "/api/v1";
        
        /// <summary>
        /// Create a new Sync Client.
        /// </summary>
        /// <param name="baseUrl">Base URL of the API server</param>
        /// <param name="authToken">Authentication token</param>
        /// <param name="coroutineRunner">MonoBehaviour to run coroutines on</param>
        public SyncClient(string baseUrl, string authToken, MonoBehaviour coroutineRunner)
        {
            _baseUrl = baseUrl.TrimEnd('/');
            _authToken = authToken;
            _coroutineRunner = coroutineRunner;
        }
        
        /// <summary>
        /// Update the authentication token.
        /// </summary>
        /// <param name="token">New authentication token</param>
        public void SetAuthToken(string token)
        {
            _authToken = token;
        }
        
        #region Sync Records
        
        /// <summary>
        /// Create a new sync record.
        /// </summary>
        /// <param name="syncRecord">Sync record data</param>
        /// <param name="callback">Callback function called when operation completes</param>
        public void CreateSyncRecord(SyncRecordCreateRequest syncRecord, Action<SyncRecordResponse, string> callback)
        {
            _coroutineRunner.StartCoroutine(CreateSyncRecordCoroutine(syncRecord, callback));
        }
        
        private IEnumerator CreateSyncRecordCoroutine(SyncRecordCreateRequest syncRecord, Action<SyncRecordResponse, string> callback)
        {
            string url = $"{_baseUrl}{API_PREFIX}/sync/records";
            string jsonData = JsonConvert.SerializeObject(syncRecord);
            
            using (UnityWebRequest request = CreateJsonRequest(url, "POST", jsonData))
            {
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    var response = JsonConvert.DeserializeObject<SyncRecordResponse>(request.downloadHandler.text);
                    callback?.Invoke(response, null);
                }
                else
                {
                    callback?.Invoke(null, request.error);
                }
            }
        }
        
        /// <summary>
        /// Process a batch of sync records.
        /// </summary>
        /// <param name="batch">Batch of sync records</param>
        /// <param name="callback">Callback function called when operation completes</param>
        public void ProcessSyncBatch(SyncBatchRequest batch, Action<List<SyncRecordResponse>, string> callback)
        {
            _coroutineRunner.StartCoroutine(ProcessSyncBatchCoroutine(batch, callback));
        }
        
        private IEnumerator ProcessSyncBatchCoroutine(SyncBatchRequest batch, Action<List<SyncRecordResponse>, string> callback)
        {
            string url = $"{_baseUrl}{API_PREFIX}/sync/batch";
            string jsonData = JsonConvert.SerializeObject(batch);
            
            using (UnityWebRequest request = CreateJsonRequest(url, "POST", jsonData))
            {
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    var response = JsonConvert.DeserializeObject<List<SyncRecordResponse>>(request.downloadHandler.text);
                    callback?.Invoke(response, null);
                }
                else
                {
                    callback?.Invoke(null, request.error);
                }
            }
        }
        
        /// <summary>
        /// Get sync records with optional filtering.
        /// </summary>
        /// <param name="entityType">Optional filter by entity type</param>
        /// <param name="entityId">Optional filter by entity ID</param>
        /// <param name="clientId">Optional filter by client ID</param>
        /// <param name="status">Optional filter by status</param>
        /// <param name="since">Optional filter for records after this timestamp</param>
        /// <param name="callback">Callback function called when operation completes</param>
        public void GetSyncRecords(string entityType, string entityId, string clientId, string status, float? since, Action<List<SyncRecordResponse>, string> callback)
        {
            _coroutineRunner.StartCoroutine(GetSyncRecordsCoroutine(entityType, entityId, clientId, status, since, callback));
        }
        
        private IEnumerator GetSyncRecordsCoroutine(string entityType, string entityId, string clientId, string status, float? since, Action<List<SyncRecordResponse>, string> callback)
        {
            StringBuilder urlBuilder = new StringBuilder($"{_baseUrl}{API_PREFIX}/sync/records?");
            
            if (!string.IsNullOrEmpty(entityType))
            {
                urlBuilder.Append($"entity_type={UnityWebRequest.EscapeURL(entityType)}&");
            }
            
            if (!string.IsNullOrEmpty(entityId))
            {
                urlBuilder.Append($"entity_id={UnityWebRequest.EscapeURL(entityId)}&");
            }
            
            if (!string.IsNullOrEmpty(clientId))
            {
                urlBuilder.Append($"client_id={UnityWebRequest.EscapeURL(clientId)}&");
            }
            
            if (!string.IsNullOrEmpty(status))
            {
                urlBuilder.Append($"status={UnityWebRequest.EscapeURL(status)}&");
            }
            
            if (since.HasValue)
            {
                urlBuilder.Append($"since={since.Value}&");
            }
            
            using (UnityWebRequest request = CreateAuthenticatedRequest(urlBuilder.ToString(), "GET"))
            {
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    var response = JsonConvert.DeserializeObject<List<SyncRecordResponse>>(request.downloadHandler.text);
                    callback?.Invoke(response, null);
                }
                else
                {
                    callback?.Invoke(null, request.error);
                }
            }
        }
        
        /// <summary>
        /// Update the status of a sync record.
        /// </summary>
        /// <param name="recordId">ID of the sync record</param>
        /// <param name="status">New status for the record</param>
        /// <param name="callback">Callback function called when operation completes</param>
        public void UpdateSyncRecordStatus(string recordId, string status, Action<SyncRecordResponse, string> callback)
        {
            _coroutineRunner.StartCoroutine(UpdateSyncRecordStatusCoroutine(recordId, status, callback));
        }
        
        private IEnumerator UpdateSyncRecordStatusCoroutine(string recordId, string status, Action<SyncRecordResponse, string> callback)
        {
            string url = $"{_baseUrl}{API_PREFIX}/sync/records/{recordId}/status?status={status}";
            
            using (UnityWebRequest request = CreateAuthenticatedRequest(url, "PATCH"))
            {
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    var response = JsonConvert.DeserializeObject<SyncRecordResponse>(request.downloadHandler.text);
                    callback?.Invoke(response, null);
                }
                else
                {
                    callback?.Invoke(null, request.error);
                }
            }
        }
        
        /// <summary>
        /// Process all pending sync records.
        /// </summary>
        /// <param name="callback">Callback function called when operation completes</param>
        public void ProcessPendingRecords(Action<Dictionary<string, int>, string> callback)
        {
            _coroutineRunner.StartCoroutine(ProcessPendingRecordsCoroutine(callback));
        }
        
        private IEnumerator ProcessPendingRecordsCoroutine(Action<Dictionary<string, int>, string> callback)
        {
            string url = $"{_baseUrl}{API_PREFIX}/sync/process";
            
            using (UnityWebRequest request = CreateAuthenticatedRequest(url, "POST"))
            {
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    var response = JsonConvert.DeserializeObject<Dictionary<string, int>>(request.downloadHandler.text);
                    callback?.Invoke(response, null);
                }
                else
                {
                    callback?.Invoke(null, request.error);
                }
            }
        }
        
        #endregion
        
        #region Backups
        
        /// <summary>
        /// Create a backup of the current data.
        /// </summary>
        /// <param name="backupId">Optional identifier for the backup</param>
        /// <param name="callback">Callback function called when operation completes</param>
        public void CreateBackup(string backupId, Action<BackupResponse, string> callback)
        {
            _coroutineRunner.StartCoroutine(CreateBackupCoroutine(backupId, callback));
        }
        
        private IEnumerator CreateBackupCoroutine(string backupId, Action<BackupResponse, string> callback)
        {
            string url = $"{_baseUrl}{API_PREFIX}/sync/backups";
            
            if (!string.IsNullOrEmpty(backupId))
            {
                url += $"?backup_id={UnityWebRequest.EscapeURL(backupId)}";
            }
            
            using (UnityWebRequest request = CreateAuthenticatedRequest(url, "POST"))
            {
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    var response = JsonConvert.DeserializeObject<BackupResponse>(request.downloadHandler.text);
                    callback?.Invoke(response, null);
                }
                else
                {
                    callback?.Invoke(null, request.error);
                }
            }
        }
        
        /// <summary>
        /// Get a list of available backups.
        /// </summary>
        /// <param name="callback">Callback function called when operation completes</param>
        public void ListBackups(Action<BackupListResponse, string> callback)
        {
            _coroutineRunner.StartCoroutine(ListBackupsCoroutine(callback));
        }
        
        private IEnumerator ListBackupsCoroutine(Action<BackupListResponse, string> callback)
        {
            string url = $"{_baseUrl}{API_PREFIX}/sync/backups";
            
            using (UnityWebRequest request = CreateAuthenticatedRequest(url, "GET"))
            {
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    var response = JsonConvert.DeserializeObject<BackupListResponse>(request.downloadHandler.text);
                    callback?.Invoke(response, null);
                }
                else
                {
                    callback?.Invoke(null, request.error);
                }
            }
        }
        
        /// <summary>
        /// Restore data from a backup.
        /// </summary>
        /// <param name="backupId">ID of the backup to restore</param>
        /// <param name="callback">Callback function called when operation completes</param>
        public void RestoreBackup(string backupId, Action<BackupResponse, string> callback)
        {
            _coroutineRunner.StartCoroutine(RestoreBackupCoroutine(backupId, callback));
        }
        
        private IEnumerator RestoreBackupCoroutine(string backupId, Action<BackupResponse, string> callback)
        {
            string url = $"{_baseUrl}{API_PREFIX}/sync/backups/{backupId}/restore";
            
            using (UnityWebRequest request = CreateAuthenticatedRequest(url, "POST"))
            {
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    var response = JsonConvert.DeserializeObject<BackupResponse>(request.downloadHandler.text);
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
