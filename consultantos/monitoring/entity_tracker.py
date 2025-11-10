"""
Entity Tracker - Track entity mentions and relationships across monitoring snapshots
"""
import logging
from typing import List, Dict, Any, Set, Tuple, Optional
from datetime import datetime
from collections import defaultdict
from consultantos.models import EntityMention, EntityRelationship

logger = logging.getLogger(__name__)


class EntityChange:
    """Represents a change in entity mentions between snapshots"""

    def __init__(
        self,
        entity_text: str,
        entity_label: str,
        change_type: str,  # 'new', 'increased', 'decreased', 'removed'
        previous_count: int,
        current_count: int,
        context_samples: List[str] = None
    ):
        self.entity_text = entity_text
        self.entity_label = entity_label
        self.change_type = change_type
        self.previous_count = previous_count
        self.current_count = current_count
        self.context_samples = context_samples or []
        self.detected_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "entity_text": self.entity_text,
            "entity_label": self.entity_label,
            "change_type": self.change_type,
            "previous_count": self.previous_count,
            "current_count": self.current_count,
            "context_samples": self.context_samples,
            "detected_at": self.detected_at.isoformat(),
        }

    def __repr__(self) -> str:
        return (
            f"EntityChange(entity='{self.entity_text}', "
            f"type={self.change_type}, "
            f"{self.previous_count}→{self.current_count})"
        )


class RelationshipChange:
    """Represents a change in entity relationships"""

    def __init__(
        self,
        entity1: str,
        entity2: str,
        change_type: str,  # 'new_relationship', 'changed_context', 'removed'
        previous_contexts: List[str],
        current_contexts: List[str]
    ):
        self.entity1 = entity1
        self.entity2 = entity2
        self.change_type = change_type
        self.previous_contexts = previous_contexts
        self.current_contexts = current_contexts
        self.detected_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "entity1": self.entity1,
            "entity2": self.entity2,
            "change_type": self.change_type,
            "previous_contexts": self.previous_contexts,
            "current_contexts": self.current_contexts,
            "detected_at": self.detected_at.isoformat(),
        }

    def __repr__(self) -> str:
        return (
            f"RelationshipChange('{self.entity1}' <-> '{self.entity2}', "
            f"type={self.change_type})"
        )


class EntityTracker:
    """
    Track entity mentions and relationships across monitoring snapshots.

    Enables detection of:
    - New entities (potential competitors, partners)
    - Changed entity mentions (increased/decreased attention)
    - New relationships (partnerships, acquisitions, conflicts)
    - Changed relationship contexts (evolving business relationships)
    """

    def __init__(self, significance_threshold: int = 2):
        """
        Initialize entity tracker.

        Args:
            significance_threshold: Minimum mention count to consider entity significant
        """
        self.significance_threshold = significance_threshold

    def compare_entities(
        self,
        previous_entities: List[EntityMention],
        current_entities: List[EntityMention]
    ) -> List[EntityChange]:
        """
        Compare entity mentions between two snapshots.

        Args:
            previous_entities: Entities from previous snapshot
            current_entities: Entities from current snapshot

        Returns:
            List of EntityChange objects describing changes
        """
        # Count entity mentions by (text, label) tuple
        prev_counts = self._count_entities(previous_entities)
        curr_counts = self._count_entities(current_entities)

        changes = []

        # Find new entities
        for entity_key, count in curr_counts.items():
            if entity_key not in prev_counts:
                if count >= self.significance_threshold:
                    entity_text, entity_label = entity_key
                    changes.append(
                        EntityChange(
                            entity_text=entity_text,
                            entity_label=entity_label,
                            change_type="new",
                            previous_count=0,
                            current_count=count,
                        )
                    )

        # Find removed entities
        for entity_key, count in prev_counts.items():
            if entity_key not in curr_counts:
                if count >= self.significance_threshold:
                    entity_text, entity_label = entity_key
                    changes.append(
                        EntityChange(
                            entity_text=entity_text,
                            entity_label=entity_label,
                            change_type="removed",
                            previous_count=count,
                            current_count=0,
                        )
                    )

        # Find changed mention counts
        for entity_key in set(prev_counts.keys()) & set(curr_counts.keys()):
            prev_count = prev_counts[entity_key]
            curr_count = curr_counts[entity_key]

            # Only track significant changes (>50% change and meets threshold)
            if abs(curr_count - prev_count) / max(prev_count, 1) > 0.5:
                if max(prev_count, curr_count) >= self.significance_threshold:
                    entity_text, entity_label = entity_key
                    change_type = "increased" if curr_count > prev_count else "decreased"

                    changes.append(
                        EntityChange(
                            entity_text=entity_text,
                            entity_label=entity_label,
                            change_type=change_type,
                            previous_count=prev_count,
                            current_count=curr_count,
                        )
                    )

        logger.info(f"Entity comparison: {len(changes)} significant changes detected")
        return changes

    def compare_relationships(
        self,
        previous_relationships: List[EntityRelationship],
        current_relationships: List[EntityRelationship]
    ) -> List[RelationshipChange]:
        """
        Compare entity relationships between two snapshots.

        Args:
            previous_relationships: Relationships from previous snapshot
            current_relationships: Relationships from current snapshot

        Returns:
            List of RelationshipChange objects describing changes
        """
        # Group relationships by entity pair
        prev_rels = self._group_relationships(previous_relationships)
        curr_rels = self._group_relationships(current_relationships)

        changes = []

        # Find new relationships
        for pair_key, contexts in curr_rels.items():
            if pair_key not in prev_rels:
                entity1, entity2 = pair_key
                changes.append(
                    RelationshipChange(
                        entity1=entity1,
                        entity2=entity2,
                        change_type="new_relationship",
                        previous_contexts=[],
                        current_contexts=contexts,
                    )
                )

        # Find removed relationships
        for pair_key, contexts in prev_rels.items():
            if pair_key not in curr_rels:
                entity1, entity2 = pair_key
                changes.append(
                    RelationshipChange(
                        entity1=entity1,
                        entity2=entity2,
                        change_type="removed",
                        previous_contexts=contexts,
                        current_contexts=[],
                    )
                )

        # Find changed relationship contexts
        for pair_key in set(prev_rels.keys()) & set(curr_rels.keys()):
            prev_contexts = prev_rels[pair_key]
            curr_contexts = curr_rels[pair_key]

            # Check if contexts have changed significantly
            if not self._contexts_similar(prev_contexts, curr_contexts):
                entity1, entity2 = pair_key
                changes.append(
                    RelationshipChange(
                        entity1=entity1,
                        entity2=entity2,
                        change_type="changed_context",
                        previous_contexts=prev_contexts,
                        current_contexts=curr_contexts,
                    )
                )

        logger.info(f"Relationship comparison: {len(changes)} changes detected")
        return changes

    def generate_alerts(
        self,
        entity_changes: List[EntityChange],
        relationship_changes: List[RelationshipChange],
        focus_companies: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate alerts based on entity and relationship changes.

        Args:
            entity_changes: Entity changes detected
            relationship_changes: Relationship changes detected
            focus_companies: Optional list of companies to prioritize in alerts

        Returns:
            List of alert dictionaries with priority and message
        """
        alerts = []

        # Generate entity-based alerts
        for change in entity_changes:
            # Prioritize organization (ORG) and person (PERSON) entities
            if change.entity_label in ['ORG', 'PERSON']:
                priority = self._calculate_alert_priority(
                    change, focus_companies
                )

                if priority > 0:  # Only create alert if meaningful
                    alerts.append({
                        "type": "entity_change",
                        "priority": priority,
                        "message": self._format_entity_alert(change),
                        "details": change.to_dict(),
                    })

        # Generate relationship-based alerts
        for change in relationship_changes:
            # Prioritize new relationships involving organizations
            if change.change_type == "new_relationship":
                priority = self._calculate_relationship_priority(
                    change, focus_companies
                )

                if priority > 0:
                    alerts.append({
                        "type": "relationship_change",
                        "priority": priority,
                        "message": self._format_relationship_alert(change),
                        "details": change.to_dict(),
                    })

        # Sort by priority (higher = more important)
        alerts.sort(key=lambda x: x['priority'], reverse=True)

        logger.info(f"Generated {len(alerts)} alerts from entity/relationship changes")
        return alerts

    def _count_entities(
        self, entities: List[EntityMention]
    ) -> Dict[Tuple[str, str], int]:
        """Count entity mentions by (text, label) tuple"""
        counts: Dict[Tuple[str, str], int] = defaultdict(int)

        for entity in entities:
            # Normalize entity text (lowercase, strip whitespace)
            entity_key = (entity.text.lower().strip(), entity.label)
            counts[entity_key] += 1

        return dict(counts)

    def _group_relationships(
        self, relationships: List[EntityRelationship]
    ) -> Dict[Tuple[str, str], List[str]]:
        """Group relationships by entity pair with their contexts"""
        grouped: Dict[Tuple[str, str], List[str]] = defaultdict(list)

        for rel in relationships:
            # Create normalized entity pair (alphabetically sorted for consistency)
            entities = sorted([
                rel.entity1['text'].lower().strip(),
                rel.entity2['text'].lower().strip()
            ])
            pair_key = tuple(entities)

            grouped[pair_key].append(rel.context)

        return dict(grouped)

    def _contexts_similar(
        self, contexts1: List[str], contexts2: List[str], threshold: float = 0.7
    ) -> bool:
        """
        Check if two sets of contexts are similar.

        Simple heuristic: check overlap of context words.
        """
        # Extract words from contexts
        words1 = set(' '.join(contexts1).lower().split())
        words2 = set(' '.join(contexts2).lower().split())

        if not words1 or not words2:
            return False

        # Calculate Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)

        similarity = intersection / union if union > 0 else 0

        return similarity >= threshold

    def _calculate_alert_priority(
        self, change: EntityChange, focus_companies: Optional[List[str]] = None
    ) -> int:
        """
        Calculate alert priority (0-10) based on entity change characteristics.

        Higher priority for:
        - New competitors (ORG entities)
        - Changes involving focus companies
        - Large magnitude changes
        """
        priority = 0

        # Base priority by change type
        if change.change_type == "new":
            priority += 5
        elif change.change_type == "removed":
            priority += 3
        else:  # increased/decreased
            priority += 2

        # Bonus for organization entities (potential competitors)
        if change.entity_label == "ORG":
            priority += 2

        # Bonus for focus companies
        if focus_companies:
            if any(company.lower() in change.entity_text.lower() for company in focus_companies):
                priority += 3

        # Bonus for large magnitude changes
        magnitude = abs(change.current_count - change.previous_count)
        if magnitude >= 5:
            priority += 2
        elif magnitude >= 3:
            priority += 1

        return min(priority, 10)  # Cap at 10

    def _calculate_relationship_priority(
        self, change: RelationshipChange, focus_companies: Optional[List[str]] = None
    ) -> int:
        """Calculate alert priority for relationship changes"""
        priority = 0

        # Base priority by change type
        if change.change_type == "new_relationship":
            priority += 6
        elif change.change_type == "removed":
            priority += 4
        else:  # changed_context
            priority += 3

        # Bonus for focus companies
        if focus_companies:
            for company in focus_companies:
                if (company.lower() in change.entity1.lower() or
                    company.lower() in change.entity2.lower()):
                    priority += 3
                    break

        return min(priority, 10)  # Cap at 10

    def _format_entity_alert(self, change: EntityChange) -> str:
        """Format entity change as human-readable alert message"""
        if change.change_type == "new":
            return (
                f"New {change.entity_label} entity detected: '{change.entity_text}' "
                f"({change.current_count} mentions)"
            )
        elif change.change_type == "removed":
            return (
                f"{change.entity_label} entity no longer mentioned: '{change.entity_text}' "
                f"(previously {change.previous_count} mentions)"
            )
        elif change.change_type == "increased":
            return (
                f"Increased mentions of {change.entity_label} '{change.entity_text}': "
                f"{change.previous_count} → {change.current_count}"
            )
        else:  # decreased
            return (
                f"Decreased mentions of {change.entity_label} '{change.entity_text}': "
                f"{change.previous_count} → {change.current_count}"
            )

    def _format_relationship_alert(self, change: RelationshipChange) -> str:
        """Format relationship change as human-readable alert message"""
        if change.change_type == "new_relationship":
            context_sample = change.current_contexts[0] if change.current_contexts else "related"
            return (
                f"New relationship detected: '{change.entity1}' {context_sample} '{change.entity2}'"
            )
        elif change.change_type == "removed":
            return (
                f"Relationship no longer mentioned: '{change.entity1}' <-> '{change.entity2}'"
            )
        else:  # changed_context
            return (
                f"Relationship context changed: '{change.entity1}' <-> '{change.entity2}'"
            )


# Convenience function for quick entity tracking
def track_entity_changes(
    previous_entities: List[EntityMention],
    current_entities: List[EntityMention],
    previous_relationships: List[EntityRelationship],
    current_relationships: List[EntityRelationship],
    focus_companies: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Track entity and relationship changes between snapshots.

    Args:
        previous_entities: Entities from previous snapshot
        current_entities: Entities from current snapshot
        previous_relationships: Relationships from previous snapshot
        current_relationships: Relationships from current snapshot
        focus_companies: Optional list of companies to prioritize

    Returns:
        Dictionary with entity_changes, relationship_changes, and alerts
    """
    tracker = EntityTracker()

    entity_changes = tracker.compare_entities(previous_entities, current_entities)
    relationship_changes = tracker.compare_relationships(
        previous_relationships, current_relationships
    )

    alerts = tracker.generate_alerts(
        entity_changes, relationship_changes, focus_companies
    )

    return {
        "entity_changes": [change.to_dict() for change in entity_changes],
        "relationship_changes": [change.to_dict() for change in relationship_changes],
        "alerts": alerts,
        "summary": {
            "total_entity_changes": len(entity_changes),
            "total_relationship_changes": len(relationship_changes),
            "high_priority_alerts": sum(1 for alert in alerts if alert['priority'] >= 7),
        }
    }
