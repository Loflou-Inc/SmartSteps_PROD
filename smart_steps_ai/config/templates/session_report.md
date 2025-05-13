# Session Report: {{session_id}}

**Client**: {{client_name}} (ID: {{client_id}})  
**Date**: {{session_date}}  
**Duration**: {{session_duration}}  
**Session Type**: {{session_type}}  
**Facilitator**: {{facilitator_name}}

## Summary

{{session_summary}}

## Key Points

{% for point in key_points %}
- {{point}}
{% endfor %}

## Progress Assessment

{% if progress_items %}
{% for item in progress_items %}
- **{{item.area}}**: {{item.assessment}}
{% endfor %}
{% else %}
No specific progress areas were assessed in this session.
{% endif %}

## Behavioral Observations

{{behavioral_observations}}

## Cognitive Patterns

{{cognitive_patterns}}

## Emotional Content

{{emotional_content}}

## Intervention Effectiveness

{% if interventions %}
{% for intervention in interventions %}
- **{{intervention.name}}**: {{intervention.effectiveness}}
{% endfor %}
{% else %}
No specific interventions were used in this session.
{% endif %}

## Therapeutic Alliance

{{therapeutic_alliance}}

## Action Items

{% for item in action_items %}
- {{item}}
{% endfor %}

## Recommendations

{{recommendations}}

## Notes

{{notes}}

---

*Report generated on {{generation_date}} by Smart Steps AI*
