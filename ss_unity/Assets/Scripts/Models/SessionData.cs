using System;
using System.Collections.Generic;
using UnityEngine;

namespace SmartSteps.Models
{
    /// <summary>
    /// Represents a therapeutic or intervention session with a client.
    /// Contains all data related to a single session including events, 
    /// measurements, and outcomes.
    /// </summary>
    [Serializable]
    public class SessionData
    {
        /// <summary>
        /// Unique identifier for the session.
        /// </summary>
        public string SessionId;
        
        /// <summary>
        /// The unique identifier for the client.
        /// </summary>
        public string ClientId;
        
        /// <summary>
        /// The unique identifier for the therapist or facilitator.
        /// </summary>
        public string FacilitatorId;
        
        /// <summary>
        /// The type of session conducted.
        /// </summary>
        public string SessionType;
        
        /// <summary>
        /// When the session started.
        /// </summary>
        public DateTime StartTime;
        
        /// <summary>
        /// When the session ended. Null if the session is ongoing.
        /// </summary>
        public DateTime? EndTime;
        
        /// <summary>
        /// Notes about the session written by the facilitator.
        /// </summary>
        public string SessionNotes;
        
        /// <summary>
        /// The status of the session (e.g., "Scheduled", "In Progress", "Completed", "Cancelled").
        /// </summary>
        public string Status;
        
        /// <summary>
        /// The location where the session took place.
        /// </summary>
        public string Location;
        
        /// <summary>
        /// A list of goals that were addressed in this session.
        /// </summary>
        public List<string> GoalsAddressed = new List<string>();
        
        /// <summary>
        /// A list of interventions that were used in this session.
        /// </summary>
        public List<string> InterventionsUsed = new List<string>();
        
        /// <summary>
        /// A list of assessments that were conducted in this session.
        /// </summary>
        public List<string> AssessmentsCompleted = new List<string>();
        
        /// <summary>
        /// A list of events that occurred during the session.
        /// </summary>
        public List<SessionEvent> Events = new List<SessionEvent>();
        
        /// <summary>
        /// Any additional data associated with this session.
        /// </summary>
        public Dictionary<string, object> Metadata = new Dictionary<string, object>();
        
        /// <summary>
        /// Rating of the session effectiveness (1-10).
        /// </summary>
        public int EffectivenessRating;
        
        /// <summary>
        /// Client engagement level during the session (1-10).
        /// </summary>
        public int EngagementLevel;
        
        /// <summary>
        /// Progress made during this session (1-10).
        /// </summary>
        public int ProgressRating;
        
        /// <summary>
        /// Planned follow-up actions after this session.
        /// </summary>
        public string FollowUpPlan;
        
        /// <summary>
        /// Date and time of the next scheduled session, if any.
        /// </summary>
        public DateTime? NextSessionDate;
        
        /// <summary>
        /// Whether this session data has been synchronized with the backend.
        /// </summary>
        public bool IsSynced;
        
        /// <summary>
        /// When this session data was last modified.
        /// </summary>
        public DateTime LastModified;
        
        /// <summary>
        /// Creates a new empty session data object.
        /// </summary>
        public SessionData()
        {
            SessionId = Guid.NewGuid().ToString();
            StartTime = DateTime.Now;
            Status = "In Progress";
            LastModified = DateTime.Now;
            IsSynced = false;
        }
        
        /// <summary>
        /// Adds an event to the session timeline.
        /// </summary>
        /// <param name="eventType">The type of event.</param>
        /// <param name="description">Description of the event.</param>
        /// <param name="metadata">Additional data about the event.</param>
        public void AddEvent(string eventType, string description, Dictionary<string, object> metadata = null)
        {
            SessionEvent newEvent = new SessionEvent
            {
                EventType = eventType,
                Description = description,
                Timestamp = DateTime.Now
            };
            
            if (metadata != null)
            {
                newEvent.Metadata = new Dictionary<string, object>(metadata);
            }
            
            Events.Add(newEvent);
            LastModified = DateTime.Now;
        }
        
        /// <summary>
        /// Ends the current session and sets the end time.
        /// </summary>
        public void EndSession()
        {
            EndTime = DateTime.Now;
            Status = "Completed";
            LastModified = DateTime.Now;
            
            // Add session end event
            AddEvent("SessionEnd", "Session was completed");
        }
        
        /// <summary>
        /// Calculates the duration of the session.
        /// </summary>
        /// <returns>The duration of the session as a TimeSpan, or null if the session is ongoing.</returns>
        public TimeSpan? GetDuration()
        {
            if (EndTime.HasValue)
            {
                return EndTime.Value - StartTime;
            }
            
            return null;
        }
    }
    
    /// <summary>
    /// Represents a specific event that occurred during a session.
    /// </summary>
    [Serializable]
    public class SessionEvent
    {
        /// <summary>
        /// The type of event (e.g., "Assessment", "Intervention", "Break", "ClientResponse").
        /// </summary>
        public string EventType;
        
        /// <summary>
        /// A description of the event.
        /// </summary>
        public string Description;
        
        /// <summary>
        /// When the event occurred.
        /// </summary>
        public DateTime Timestamp;
        
        /// <summary>
        /// Additional data associated with this event.
        /// </summary>
        public Dictionary<string, object> Metadata = new Dictionary<string, object>();
    }
}
