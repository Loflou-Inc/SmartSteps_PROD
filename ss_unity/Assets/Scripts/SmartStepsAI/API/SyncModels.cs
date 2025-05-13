using System;
using System.Collections.Generic;
using UnityEngine;
using Newtonsoft.Json;

namespace SmartSteps.AI
{
    #region Sync Record Models
    
    [Serializable]
    public class SyncRecordCreateRequest
    {
        public string entity_type;
        public string entity_id;
        public string operation;
        public Dictionary<string, object> data;
        public string client_id;
        public int version = 1;
    }
    
    [Serializable]
    public class SyncRecordResponse
    {
        public string record_id;
        public string entity_type;
        public string entity_id;
        public string operation;
        public float timestamp;
        public Dictionary<string, object> data;
        public string client_id;
        public int version;
        public string status;
    }
    
    [Serializable]
    public class SyncBatchRequest
    {
        public List<SyncRecordCreateRequest> records;
        public string client_id;
        public bool force_sync;
    }
    
    #endregion
    
    #region Backup Models
    
    [Serializable]
    public class BackupResponse
    {
        public string backup_id;
        public DateTime timestamp;
        public string status;
        public string message;
    }
    
    [Serializable]
    public class BackupListResponse
    {
        public List<BackupResponse> backups;
        public int count;
    }
    
    #endregion
    
    /// <summary>
    /// Synchronization utility for managing local data and syncing with the server.
    /// </summary>
    public class SyncManager
    {
        private readonly SyncClient _syncClient;
        private readonly string _clientId;
        private readonly MonoBehaviour _coroutineRunner;
        
        private List<SyncRecordResponse> _pendingRecords = new List<SyncRecordResponse>();
        private List<SyncRecordResponse> _syncedRecords = new List<SyncRecordResponse>();
        private List<SyncRecordResponse> _conflictRecords = new List<SyncRecordResponse>();
        
        private bool _isSyncing = false;
        private DateTime _lastSyncTime;
        
        /// <summary>
        /// Event fired when synchronization completes.
        /// </summary>
        public event Action<bool, string> OnSyncCompleted;
        
        /// <summary>
        /// Event fired when a conflict is detected.
        /// </summary>
        public event Action<SyncRecordResponse> OnConflictDetected;
        
        /// <summary>
        /// Create a new sync manager.
        /// </summary>
        /// <param name="syncClient">The sync client to use for API communication</param>
        /// <param name="clientId">The client identifier</param>
        /// <param name="coroutineRunner">MonoBehaviour to run coroutines on</param>
        public SyncManager(SyncClient syncClient, string clientId, MonoBehaviour coroutineRunner)
        {
            _syncClient = syncClient;
            _clientId = clientId;
            _coroutineRunner = coroutineRunner;
            _lastSyncTime = DateTime.Now;
            
            // Load local sync state
            LoadLocalSyncState();
        }
        
        #region Public Methods
        
        /// <summary>
        /// Create a local sync record for an entity change.
        /// </summary>
        /// <param name="entityType">Type of entity (session, message, persona, etc.)</param>
        /// <param name="entityId">Identifier of the entity</param>
        /// <param name="operation">Type of operation (create, update, delete)</param>
        /// <param name="data">Data associated with the operation</param>
        /// <param name="callback">Callback function called when operation completes</param>
        public void CreateLocalSyncRecord(string entityType, string entityId, string operation, Dictionary<string, object> data, Action<SyncRecordResponse, string> callback)
        {
            var syncRecord = new SyncRecordCreateRequest
            {
                entity_type = entityType,
                entity_id = entityId,
                operation = operation,
                data = data,
                client_id = _clientId,
                version = 1
            };
            
            // Send to server if online
            if (Application.internetReachability != NetworkReachability.NotReachable)
            {
                _syncClient.CreateSyncRecord(syncRecord, (response, error) =>
                {
                    if (response != null)
                    {
                        // Add to pending records
                        _pendingRecords.Add(response);
                        
                        // Save local sync state
                        SaveLocalSyncState();
                    }
                    
                    callback?.Invoke(response, error);
                });
            }
            else
            {
                // Create a local record if offline
                var localRecord = new SyncRecordResponse
                {
                    record_id = Guid.NewGuid().ToString(),
                    entity_type = entityType,
                    entity_id = entityId,
                    operation = operation,
                    timestamp = DateTimeToUnixTimestamp(DateTime.Now),
                    data = data,
                    client_id = _clientId,
                    version = 1,
                    status = "pending"
                };
                
                // Add to pending records
                _pendingRecords.Add(localRecord);
                
                // Save local sync state
                SaveLocalSyncState();
                
                callback?.Invoke(localRecord, null);
            }
        }
        
        /// <summary>
        /// Synchronize local changes with the server.
        /// </summary>
        /// <param name="callback">Callback function called when synchronization completes</param>
        public void Synchronize(Action<bool, string> callback)
        {
            if (_isSyncing)
            {
                callback?.Invoke(false, "Synchronization already in progress");
                return;
            }
            
            _isSyncing = true;
            
            // Step 1: Get server-side pending records
            _syncClient.GetSyncRecords(null, null, null, "pending", null, (serverRecords, error) =>
            {
                if (serverRecords != null)
                {
                    // Step 2: Create batch from local pending records
                    var batchRecords = new List<SyncRecordCreateRequest>();
                    
                    foreach (var record in _pendingRecords)
                    {
                        if (record.status == "pending")
                        {
                            batchRecords.Add(new SyncRecordCreateRequest
                            {
                                entity_type = record.entity_type,
                                entity_id = record.entity_id,
                                operation = record.operation,
                                data = record.data,
                                client_id = record.client_id,
                                version = record.version
                            });
                        }
                    }
                    
                    if (batchRecords.Count > 0)
                    {
                        // Step 3: Send batch to server
                        var batch = new SyncBatchRequest
                        {
                            records = batchRecords,
                            client_id = _clientId,
                            force_sync = false
                        };
                        
                        _syncClient.ProcessSyncBatch(batch, (responses, batchError) =>
                        {
                            if (responses != null)
                            {
                                // Step 4: Update local records
                                foreach (var response in responses)
                                {
                                    UpdateLocalSyncRecord(response);
                                }
                            }
                            
                            // Step 5: Process server records
                            if (serverRecords.Count > 0)
                            {
                                ProcessServerRecords(serverRecords);
                            }
                            
                            // Step 6: Process pending records on server
                            _syncClient.ProcessPendingRecords((result, processError) =>
                            {
                                _isSyncing = false;
                                _lastSyncTime = DateTime.Now;
                                
                                // Save local sync state
                                SaveLocalSyncState();
                                
                                bool success = (responses != null) && (result != null);
                                string resultError = batchError ?? processError;
                                
                                // Notify listeners
                                OnSyncCompleted?.Invoke(success, resultError);
                                callback?.Invoke(success, resultError);
                            });
                        });
                    }
                    else
                    {
                        // No local records to sync, just process server records
                        if (serverRecords.Count > 0)
                        {
                            ProcessServerRecords(serverRecords);
                        }
                        
                        // Process pending records on server
                        _syncClient.ProcessPendingRecords((result, processError) =>
                        {
                            _isSyncing = false;
                            _lastSyncTime = DateTime.Now;
                            
                            // Save local sync state
                            SaveLocalSyncState();
                            
                            bool success = result != null;
                            
                            // Notify listeners
                            OnSyncCompleted?.Invoke(success, processError);
                            callback?.Invoke(success, processError);
                        });
                    }
                }
                else
                {
                    _isSyncing = false;
                    
                    // Notify listeners
                    OnSyncCompleted?.Invoke(false, error);
                    callback?.Invoke(false, error);
                }
            });
        }
        
        /// <summary>
        /// Create a backup of the current data.
        /// </summary>
        /// <param name="callback">Callback function called when operation completes</param>
        public void CreateBackup(Action<BackupResponse, string> callback)
        {
            _syncClient.CreateBackup(null, callback);
        }
        
        /// <summary>
        /// Get a list of available backups.
        /// </summary>
        /// <param name="callback">Callback function called when operation completes</param>
        public void ListBackups(Action<BackupListResponse, string> callback)
        {
            _syncClient.ListBackups(callback);
        }
        
        /// <summary>
        /// Restore data from a backup.
        /// </summary>
        /// <param name="backupId">ID of the backup to restore</param>
        /// <param name="callback">Callback function called when operation completes</param>
        public void RestoreBackup(string backupId, Action<BackupResponse, string> callback)
        {
            _syncClient.RestoreBackup(backupId, callback);
        }
        
        #endregion
        
        #region Private Methods
        
        private void LoadLocalSyncState()
        {
            // Load from PlayerPrefs or another persistence mechanism
            string pendingRecordsJson = PlayerPrefs.GetString("PendingSyncRecords", "[]");
            string syncedRecordsJson = PlayerPrefs.GetString("SyncedSyncRecords", "[]");
            string conflictRecordsJson = PlayerPrefs.GetString("ConflictSyncRecords", "[]");
            
            _pendingRecords = JsonConvert.DeserializeObject<List<SyncRecordResponse>>(pendingRecordsJson);
            _syncedRecords = JsonConvert.DeserializeObject<List<SyncRecordResponse>>(syncedRecordsJson);
            _conflictRecords = JsonConvert.DeserializeObject<List<SyncRecordResponse>>(conflictRecordsJson);
            
            // Load last sync time
            long lastSyncTicks = Convert.ToInt64(PlayerPrefs.GetString("LastSyncTime", "0"));
            if (lastSyncTicks > 0)
            {
                _lastSyncTime = new DateTime(lastSyncTicks);
            }
        }
        
        private void SaveLocalSyncState()
        {
            // Save to PlayerPrefs or another persistence mechanism
            string pendingRecordsJson = JsonConvert.SerializeObject(_pendingRecords);
            string syncedRecordsJson = JsonConvert.SerializeObject(_syncedRecords);
            string conflictRecordsJson = JsonConvert.SerializeObject(_conflictRecords);
            
            PlayerPrefs.SetString("PendingSyncRecords", pendingRecordsJson);
            PlayerPrefs.SetString("SyncedSyncRecords", syncedRecordsJson);
            PlayerPrefs.SetString("ConflictSyncRecords", conflictRecordsJson);
            
            // Save last sync time
            PlayerPrefs.SetString("LastSyncTime", _lastSyncTime.Ticks.ToString());
            
            PlayerPrefs.Save();
        }
        
        private void UpdateLocalSyncRecord(SyncRecordResponse record)
        {
            // Find and update in pending records
            for (int i = 0; i < _pendingRecords.Count; i++)
            {
                if (_pendingRecords[i].record_id == record.record_id)
                {
                    _pendingRecords[i] = record;
                    
                    // Move to appropriate list based on status
                    if (record.status == "synced")
                    {
                        _syncedRecords.Add(record);
                        _pendingRecords.RemoveAt(i);
                    }
                    else if (record.status == "conflict")
                    {
                        _conflictRecords.Add(record);
                        _pendingRecords.RemoveAt(i);
                        
                        // Notify about conflict
                        OnConflictDetected?.Invoke(record);
                    }
                    
                    return;
                }
            }
            
            // If not found, add to pending records
            _pendingRecords.Add(record);
        }
        
        private void ProcessServerRecords(List<SyncRecordResponse> serverRecords)
        {
            foreach (var record in serverRecords)
            {
                // Apply server-side changes locally
                // Implementation depends on entity types and operations
                
                // Update local sync record
                UpdateLocalSyncRecord(record);
            }
        }
        
        private float DateTimeToUnixTimestamp(DateTime dateTime)
        {
            DateTime epochStart = new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc);
            return (float)(dateTime.ToUniversalTime() - epochStart).TotalSeconds;
        }
        
        #endregion
    }
}
