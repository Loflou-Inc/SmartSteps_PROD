using System;
using System.Collections.Generic;
using UnityEngine;
using Newtonsoft.Json;

namespace SmartSteps.AI
{
    #region Authentication
    
    [Serializable]
    public class AuthResponse
    {
        public string access_token;
        public string token_type;
    }
    
    #endregion
    
    #region Session Models
    
    [Serializable]
    public class SessionCreateRequest
    {
        public string title;
        public string client_id;
        public string persona_id;
        public string provider_id;
        public Dictionary<string, object> metadata;
    }
    
    [Serializable]
    public class SessionUpdateRequest
    {
        public string title;
        public string status;
        public Dictionary<string, object> metadata;
    }
    
    [Serializable]
    public class SessionResponse
    {
        public string id;
        public string title;
        public string client_id;
        public string persona_id;
        public string provider_id;
        public string status;
        public DateTime created_at;
        public DateTime updated_at;
        public int message_count;
        public int? duration;
        public Dictionary<string, object> metadata;
    }
    
    [Serializable]
    public class SessionListResponse
    {
        public List<SessionResponse> sessions;
        public int total_count;
        public int limit;
        public int offset;
    }
    
    #endregion
    
    #region Conversation Models
    
    [Serializable]
    public class MessageCreateRequest
    {
        public string content;
        public string client_id;
        public Dictionary<string, object> metadata;
    }
    
    [Serializable]
    public class MessageResponse
    {
        public string id;
        public string session_id;
        public string sender_type;
        public string content;
        public DateTime timestamp;
        public Dictionary<string, object> metadata;
    }
    
    [Serializable]
    public class MessageListResponse
    {
        public List<MessageResponse> messages;
        public int total_count;
        public int limit;
    }
    
    [Serializable]
    public class ConversationExportResponse
    {
        public string session_id;
        public string title;
        public string format;
        public string content;
        public int message_count;
        public string client_id;
        public string persona_id;
        public DateTime created_at;
        public List<MessageResponse> messages;
    }
    
    #endregion
    
    #region Analysis Models
    
    [Serializable]
    public class SessionAnalysisResponse
    {
        public string session_id;
        public string client_id;
        public string title;
        public string summary;
        public List<string> key_points;
        public List<string> themes;
        public List<string> concerns;
        public List<string> strengths;
        public List<string> recommendations;
        public Dictionary<string, object> sentiment_analysis;
        public DateTime analysis_date;
    }
    
    [Serializable]
    public class InsightResponse
    {
        public string id;
        public string client_id;
        public string session_id;
        public string type;
        public string content;
        public float confidence;
        public DateTime timestamp;
        public List<string> supporting_evidence;
        public List<string> related_insights;
        public List<string> actions;
    }
    
    [Serializable]
    public class InsightListResponse
    {
        public List<InsightResponse> insights;
        public int total_count;
        public int limit;
        public string client_id;
        public string timeframe;
    }
    
    [Serializable]
    public class ReportSection
    {
        public string title;
        public string content;
        public string type;
        public int order;
    }
    
    [Serializable]
    public class ReportResponse
    {
        public string id;
        public string client_id;
        public string title;
        public string format;
        public string content;
        public List<ReportSection> sections;
        public Dictionary<string, object> metadata;
        public DateTime created_at;
        public int session_count;
        public string timeframe;
    }
    
    [Serializable]
    public class ProgressMetric
    {
        public string name;
        public float value;
        public float baseline;
        public float? target;
        public float change;
        public float change_percentage;
        public List<Dictionary<string, object>> history;
    }
    
    [Serializable]
    public class Milestone
    {
        public string id;
        public string title;
        public string description;
        public bool achieved;
        public DateTime? achieved_date;
        public DateTime? target_date;
        public List<string> metrics;
    }
    
    [Serializable]
    public class ProgressResponse
    {
        public string client_id;
        public string timeframe;
        public Dictionary<string, ProgressMetric> metrics;
        public Dictionary<string, object> trends;
        public List<Milestone> milestones;
        public string summary;
        public string recommendation;
        public int session_count;
        public DateTime first_session_date;
        public DateTime latest_session_date;
    }
    
    #endregion
    
    #region Persona Models
    
    [Serializable]
    public class PersonaResponse
    {
        public string id;
        public string name;
        public string role;
        public string description;
        public List<string> expertise;
        public List<string> traits;
        public string voice_style;
        public List<string> therapeutic_approach;
        public DateTime created_at;
        public DateTime updated_at;
        public float? effectiveness;
        public int session_count;
        public bool is_enhanced;
        public Dictionary<string, object> metadata;
    }
    
    [Serializable]
    public class PersonaListResponse
    {
        public List<PersonaResponse> personas;
        public int total_count;
        public int limit;
        public int offset;
    }
    
    [Serializable]
    public class PersonaValidationResponse
    {
        public string persona_id;
        public bool is_valid;
        public List<string> issues;
        public List<string> warnings;
        public List<string> suggestions;
        public DateTime validation_date;
    }
    
    #endregion
}
