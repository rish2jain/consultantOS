"""
Database index management for Firestore.

This module defines composite indexes and provides utilities for index creation.
"""
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


# Firestore composite index configurations
FIRESTORE_INDEXES = [
    {
        "collection": "analyses",
        "fields": [
            {"field": "company", "mode": "ASCENDING"},
            {"field": "created_at", "mode": "DESCENDING"}
        ],
        "description": "Query analyses by company, ordered by creation time"
    },
    {
        "collection": "analyses",
        "fields": [
            {"field": "user_id", "mode": "ASCENDING"},
            {"field": "created_at", "mode": "DESCENDING"}
        ],
        "description": "Query user's analyses ordered by creation time"
    },
    {
        "collection": "analyses",
        "fields": [
            {"field": "status", "mode": "ASCENDING"},
            {"field": "updated_at", "mode": "DESCENDING"}
        ],
        "description": "Query analyses by status, ordered by update time"
    },
    {
        "collection": "conversations",
        "fields": [
            {"field": "user_id", "mode": "ASCENDING"},
            {"field": "updated_at", "mode": "DESCENDING"}
        ],
        "description": "Query user's conversations ordered by update time"
    },
    {
        "collection": "conversations",
        "fields": [
            {"field": "context_type", "mode": "ASCENDING"},
            {"field": "created_at", "mode": "DESCENDING"}
        ],
        "description": "Query conversations by context type, ordered by creation time"
    },
    {
        "collection": "forecasts",
        "fields": [
            {"field": "company", "mode": "ASCENDING"},
            {"field": "created_at", "mode": "DESCENDING"}
        ],
        "description": "Query forecasts by company, ordered by creation time"
    },
    {
        "collection": "forecasts",
        "fields": [
            {"field": "user_id", "mode": "ASCENDING"},
            {"field": "created_at", "mode": "DESCENDING"}
        ],
        "description": "Query user's forecasts ordered by creation time"
    },
    {
        "collection": "monitors",
        "fields": [
            {"field": "user_id", "mode": "ASCENDING"},
            {"field": "active", "mode": "ASCENDING"},
            {"field": "next_check", "mode": "ASCENDING"}
        ],
        "description": "Query active monitors by user, ordered by next check time"
    },
    {
        "collection": "monitors",
        "fields": [
            {"field": "company", "mode": "ASCENDING"},
            {"field": "created_at", "mode": "DESCENDING"}
        ],
        "description": "Query monitors by company, ordered by creation time"
    },
    {
        "collection": "alerts",
        "fields": [
            {"field": "monitor_id", "mode": "ASCENDING"},
            {"field": "created_at", "mode": "DESCENDING"}
        ],
        "description": "Query alerts for a monitor, ordered by creation time"
    },
    {
        "collection": "alerts",
        "fields": [
            {"field": "user_id", "mode": "ASCENDING"},
            {"field": "dismissed", "mode": "ASCENDING"},
            {"field": "created_at", "mode": "DESCENDING"}
        ],
        "description": "Query user's undismissed alerts ordered by creation time"
    },
    {
        "collection": "reports",
        "fields": [
            {"field": "user_id", "mode": "ASCENDING"},
            {"field": "format", "mode": "ASCENDING"},
            {"field": "created_at", "mode": "DESCENDING"}
        ],
        "description": "Query user's reports by format, ordered by creation time"
    },
    {
        "collection": "snapshots",
        "fields": [
            {"field": "monitor_id", "mode": "ASCENDING"},
            {"field": "timestamp", "mode": "DESCENDING"}
        ],
        "description": "Query snapshots for a monitor, ordered by timestamp"
    },
    {
        "collection": "jobs",
        "fields": [
            {"field": "status", "mode": "ASCENDING"},
            {"field": "created_at", "mode": "ASCENDING"}
        ],
        "description": "Query jobs by status, ordered by creation time (for job queue)"
    }
]


# Single-field indexes (automatically created by Firestore for most use cases)
SINGLE_FIELD_INDEXES = [
    {"collection": "analyses", "field": "report_id"},
    {"collection": "analyses", "field": "company"},
    {"collection": "analyses", "field": "user_id"},
    {"collection": "conversations", "field": "conversation_id"},
    {"collection": "forecasts", "field": "company"},
    {"collection": "monitors", "field": "monitor_id"},
    {"collection": "monitors", "field": "company"},
    {"collection": "alerts", "field": "alert_id"},
    {"collection": "reports", "field": "report_id"},
]


def generate_index_json() -> Dict[str, Any]:
    """
    Generate firestore.indexes.json file content.

    Returns:
        Dict suitable for firestore.indexes.json
    """
    indexes = []

    for index_config in FIRESTORE_INDEXES:
        fields = []
        for field in index_config["fields"]:
            fields.append({
                "fieldPath": field["field"],
                "order": field["mode"]
            })

        indexes.append({
            "collectionGroup": index_config["collection"],
            "queryScope": "COLLECTION",
            "fields": fields
        })

    return {
        "indexes": indexes,
        "fieldOverrides": []
    }


def get_index_creation_commands() -> List[str]:
    """
    Generate gcloud commands to create indexes.

    Returns:
        List of gcloud firestore index commands
    """
    commands = []

    for index_config in FIRESTORE_INDEXES:
        field_specs = []
        for field in index_config["fields"]:
            field_specs.append(
                f"{field['field']}:{field['mode'].lower()}"
            )

        field_spec_str = ",".join(field_specs)

        command = (
            f"gcloud firestore indexes composite create "
            f"--collection-group={index_config['collection']} "
            f"--field-config={field_spec_str} "
            f"--query-scope=COLLECTION"
        )

        commands.append(command)

    return commands


def print_index_info():
    """Print index configuration information."""
    print("=" * 80)
    print("Firestore Index Configuration")
    print("=" * 80)
    print(f"\nTotal Composite Indexes: {len(FIRESTORE_INDEXES)}")
    print(f"Total Single-Field Indexes: {len(SINGLE_FIELD_INDEXES)}")

    print("\nComposite Indexes:")
    print("-" * 80)

    for i, index in enumerate(FIRESTORE_INDEXES, 1):
        print(f"\n{i}. {index['collection']}")
        print(f"   Description: {index['description']}")
        print("   Fields:")
        for field in index["fields"]:
            print(f"     - {field['field']} ({field['mode']})")

    print("\n" + "=" * 80)


def generate_index_file():
    """Generate and save firestore.indexes.json file."""
    import json
    from pathlib import Path

    index_data = generate_index_json()

    # Save to project root
    project_root = Path(__file__).parent.parent.parent
    index_file = project_root / "firestore.indexes.json"

    with open(index_file, "w") as f:
        json.dump(index_data, f, indent=2)

    logger.info(f"Generated index file: {index_file}")
    print(f"\nIndex file generated: {index_file}")


def generate_deployment_script():
    """Generate deployment script for indexes."""
    from pathlib import Path

    commands = get_index_creation_commands()

    script_content = """#!/bin/bash
# Firestore Index Deployment Script
# Generated by ConsultantOS performance optimization

set -e

echo "Deploying Firestore indexes..."

"""

    for i, command in enumerate(commands, 1):
        script_content += f"\necho 'Creating index {i}/{len(commands)}...'\n"
        script_content += f"{command}\n"

    script_content += """
echo "Index deployment complete!"
echo "Note: Indexes may take several minutes to build."
"""

    # Save to scripts directory
    project_root = Path(__file__).parent.parent.parent
    scripts_dir = project_root / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    script_file = scripts_dir / "deploy_indexes.sh"

    with open(script_file, "w") as f:
        f.write(script_content)

    # Make executable
    script_file.chmod(0o755)

    logger.info(f"Generated deployment script: {script_file}")
    print(f"\nDeployment script generated: {script_file}")
    print("Run with: ./scripts/deploy_indexes.sh")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "info":
            print_index_info()
        elif command == "generate":
            generate_index_file()
            generate_deployment_script()
        else:
            print(f"Unknown command: {command}")
            print("Usage: python indexes.py [info|generate]")
    else:
        print("Usage: python indexes.py [info|generate]")
        print("\nCommands:")
        print("  info     - Display index configuration")
        print("  generate - Generate index files and deployment script")
