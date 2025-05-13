using System;
using System.Collections.Generic;
using UnityEngine;

namespace SmartSteps.Models
{
    /// <summary>
    /// Represents a client in the Smart Steps system.
    /// Contains all client-related information including demographics, history, and goals.
    /// </summary>
    [Serializable]
    public class ClientData
    {
        /// <summary>
        /// Unique identifier for the client.
        /// </summary>
        public string ClientId;
        
        /// <summary>
        /// First name of the client.
        /// </summary>
        public string FirstName;
        
        /// <summary>
        /// Last name of the client.
        /// </summary>
        public string LastName;
        
        /// <summary>
        /// Date of birth of the client.
        /// </summary>
        public DateTime DateOfBirth;
        
        /// <summary>
        /// The primary facilitator/therapist assigned to this client.
        /// </summary>
        public string PrimaryFacilitatorId;
        
        /// <summary>
        /// The date when the client was first registered in the system.
        /// </summary>
        public DateTime RegistrationDate;
        
        /// <summary>
        /// The date of the client's most recent session.
        /// </summary>
        public DateTime? LastSessionDate;
        
        /// <summary>
        /// The date of the client's next scheduled session, if any.
        /// </summary>
        public DateTime? NextSessionDate;
        
        /// <summary>
        /// The status of the client (e.g., "Active", "Inactive", "Completed", "On Hold").
        /// </summary>
        public string Status;
        
        /// <summary>
        /// The reason for seeking services or presenting issue.
        /// </summary>
        public string PresentingIssue;
        
        /// <summary>
        /// Any diagnoses associated with the client.
        /// </summary>
        public List<string> Diagnoses = new List<string>();
        
        /// <summary>
        /// Goals set for the client.
        /// </summary>
        public List<ClientGoal> Goals = new List<ClientGoal>();
        
        /// <summary>
        /// Notes about the client.
        /// </summary>
        public List<ClientNote> Notes = new List<ClientNote>();
        
        /// <summary>
        /// IDs of sessions conducted with this client.
        /// </summary>
        public List<string> SessionIds = new List<string>();
        
        /// <summary>
        /// Custom tags associated with this client for filtering and organization.
        /// </summary>
        public List<string> Tags = new List<string>();
        
        /// <summary>
        /// Additional demographic information.
        /// </summary>
        public Dictionary<string, object> Demographics = new Dictionary<string, object>();
        
        /// <summary>
        /// Any additional data associated with this client.
        /// </summary>
        public Dictionary<string, object> Metadata = new Dictionary<string, object>();
        
        /// <summary>
        /// When this client data was last modified.
        /// </summary>
        public DateTime LastModified;
        
        /// <summary>
        /// Whether this client data has been synchronized with the backend.
        /// </summary>
        public bool IsSynced;
        
        /// <summary>
        /// Creates a new empty client data object.
        /// </summary>
        public ClientData()
        {
            ClientId = Guid.NewGuid().ToString();
            RegistrationDate = DateTime.Now;
            Status = "Active";
            LastModified = DateTime.Now;
            IsSynced = false;
        }
        
        /// <summary>
        /// Gets the full name of the client.
        /// </summary>
        /// <returns>The full name of the client.</returns>
        public string GetFullName()
        {
            return $"{FirstName} {LastName}";
        }
        
        /// <summary>
        /// Calculates the age of the client based on their date of birth.
        /// </summary>
        /// <returns>The age of the client in years.</returns>
        public int GetAge()
        {
            DateTime today = DateTime.Today;
            int age = today.Year - DateOfBirth.Year;
            
            // Adjust age if birthday hasn't occurred yet this year
            if (DateOfBirth.Date > today.AddYears(-age))
            {
                age--;
            }
            
            return age;
        }
        
        /// <summary>
        /// Adds a new goal for the client.
        /// </summary>
        /// <param name="description">The goal description.</param>
        /// <param name="targetDate">When the goal should be completed.</param>
        /// <returns>The newly created goal.</returns>
        public ClientGoal AddGoal(string description, DateTime targetDate)
        {
            ClientGoal newGoal = new ClientGoal
            {
                GoalId = Guid.NewGuid().ToString(),
                Description = description,
                CreationDate = DateTime.Now,
                TargetDate = targetDate,
                Status = "Active"
            };
            
            Goals.Add(newGoal);
            LastModified = DateTime.Now;
            
            return newGoal;
        }
        
        /// <summary>
        /// Adds a new note about the client.
        /// </summary>
        /// <param name="content">The note content.</param>
        /// <param name="authorId">The ID of the user who wrote the note.</param>
        /// <param name="category">The category of the note.</param>
        /// <returns>The newly created note.</returns>
        public ClientNote AddNote(string content, string authorId, string category = "General")
        {
            ClientNote newNote = new ClientNote
            {
                NoteId = Guid.NewGuid().ToString(),
                Content = content,
                AuthorId = authorId,
                Category = category,
                CreationDate = DateTime.Now
            };
            
            Notes.Add(newNote);
            LastModified = DateTime.Now;
            
            return newNote;
        }
        
        /// <summary>
        /// Records a new session for this client.
        /// </summary>
        /// <param name="sessionId">The ID of the session.</param>
        /// <param name="sessionDate">The date of the session.</param>
        public void RecordSession(string sessionId, DateTime sessionDate)
        {
            SessionIds.Add(sessionId);
            LastSessionDate = sessionDate;
            LastModified = DateTime.Now;
        }
    }
    
    /// <summary>
    /// Represents a goal set for a client.
    /// </summary>
    [Serializable]
    public class ClientGoal
    {
        /// <summary>
        /// Unique identifier for the goal.
        /// </summary>
        public string GoalId;
        
        /// <summary>
        /// The description of the goal.
        /// </summary>
        public string Description;
        
        /// <summary>
        /// When the goal was created.
        /// </summary>
        public DateTime CreationDate;
        
        /// <summary>
        /// The target date for completing the goal.
        /// </summary>
        public DateTime TargetDate;
        
        /// <summary>
        /// When the goal was actually completed, if applicable.
        /// </summary>
        public DateTime? CompletionDate;
        
        /// <summary>
        /// The status of the goal (e.g., "Active", "Completed", "Abandoned").
        /// </summary>
        public string Status;
        
        /// <summary>
        /// The priority level of the goal (e.g., "High", "Medium", "Low").
        /// </summary>
        public string Priority = "Medium";
        
        /// <summary>
        /// Progress towards the goal as a percentage (0-100).
        /// </summary>
        public int ProgressPercentage;
        
        /// <summary>
        /// Notes about the goal.
        /// </summary>
        public string Notes;
        
        /// <summary>
        /// Milestones or steps towards completing the goal.
        /// </summary>
        public List<GoalMilestone> Milestones = new List<GoalMilestone>();
        
        /// <summary>
        /// Any additional data associated with this goal.
        /// </summary>
        public Dictionary<string, object> Metadata = new Dictionary<string, object>();
        
        /// <summary>
        /// Completes the goal and sets the completion date.
        /// </summary>
        public void CompleteGoal()
        {
            Status = "Completed";
            CompletionDate = DateTime.Now;
            ProgressPercentage = 100;
        }
        
        /// <summary>
        /// Adds a milestone to the goal.
        /// </summary>
        /// <param name="description">The milestone description.</param>
        /// <param name="targetDate">When the milestone should be completed.</param>
        /// <returns>The newly created milestone.</returns>
        public GoalMilestone AddMilestone(string description, DateTime targetDate)
        {
            GoalMilestone newMilestone = new GoalMilestone
            {
                MilestoneId = Guid.NewGuid().ToString(),
                Description = description,
                TargetDate = targetDate,
                Status = "Pending"
            };
            
            Milestones.Add(newMilestone);
            
            return newMilestone;
        }
        
        /// <summary>
        /// Updates the progress percentage based on completed milestones.
        /// </summary>
        public void UpdateProgress()
        {
            if (Milestones.Count == 0)
            {
                return;
            }
            
            int completedCount = 0;
            
            foreach (GoalMilestone milestone in Milestones)
            {
                if (milestone.Status == "Completed")
                {
                    completedCount++;
                }
            }
            
            ProgressPercentage = (int)((float)completedCount / Milestones.Count * 100);
        }
    }
    
    /// <summary>
    /// Represents a milestone in a client goal.
    /// </summary>
    [Serializable]
    public class GoalMilestone
    {
        /// <summary>
        /// Unique identifier for the milestone.
        /// </summary>
        public string MilestoneId;
        
        /// <summary>
        /// The description of the milestone.
        /// </summary>
        public string Description;
        
        /// <summary>
        /// The target date for completing the milestone.
        /// </summary>
        public DateTime TargetDate;
        
        /// <summary>
        /// When the milestone was actually completed, if applicable.
        /// </summary>
        public DateTime? CompletionDate;
        
        /// <summary>
        /// The status of the milestone (e.g., "Pending", "In Progress", "Completed").
        /// </summary>
        public string Status;
        
        /// <summary>
        /// Notes about the milestone.
        /// </summary>
        public string Notes;
        
        /// <summary>
        /// Completes the milestone and sets the completion date.
        /// </summary>
        public void CompleteMilestone()
        {
            Status = "Completed";
            CompletionDate = DateTime.Now;
        }
    }
    
    /// <summary>
    /// Represents a note about a client.
    /// </summary>
    [Serializable]
    public class ClientNote
    {
        /// <summary>
        /// Unique identifier for the note.
        /// </summary>
        public string NoteId;
        
        /// <summary>
        /// The content of the note.
        /// </summary>
        public string Content;
        
        /// <summary>
        /// The ID of the user who wrote the note.
        /// </summary>
        public string AuthorId;
        
        /// <summary>
        /// When the note was created.
        /// </summary>
        public DateTime CreationDate;
        
        /// <summary>
        /// When the note was last modified, if applicable.
        /// </summary>
        public DateTime? LastModified;
        
        /// <summary>
        /// The category of the note (e.g., "General", "Session", "Progress", "Goal").
        /// </summary>
        public string Category;
        
        /// <summary>
        /// Whether the note is pinned for easy access.
        /// </summary>
        public bool IsPinned;
        
        /// <summary>
        /// Any additional data associated with this note.
        /// </summary>
        public Dictionary<string, object> Metadata = new Dictionary<string, object>();
        
        /// <summary>
        /// Updates the note content and sets the last modified date.
        /// </summary>
        /// <param name="newContent">The new content for the note.</param>
        public void UpdateContent(string newContent)
        {
            Content = newContent;
            LastModified = DateTime.Now;
        }
    }
}
