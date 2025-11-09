# Team Collaboration Guide

## Overview

ConsultantOS team features enable collaborative strategic analysis with built-in switching costs through shared workspaces, team knowledge, and collaborative workflows.

## Key Features

### 1. Team Workspaces

Create dedicated spaces for teams to collaborate on analyses:

```bash
POST /teams
{
  "name": "Strategy Team",
  "description": "Internal strategy consulting team",
  "plan": "pro"  # free, pro, enterprise
}
```

**Plan Limits**:
- **Free**: 5 members, 50 analyses/month
- **Pro**: 20 members, 500 analyses/month
- **Enterprise**: Unlimited members & analyses

### 2. Team Member Management

Invite and manage team members:

```bash
# Invite member
POST /teams/{team_id}/members
{
  "email": "analyst@company.com",
  "role": "member"  # owner, admin, member, viewer
}

# List members
GET /teams/{team_id}/members

# Remove member
DELETE /teams/{team_id}/members/{user_id}
```

**Roles**:
- **Owner**: Full control, can delete team
- **Admin**: Can invite/remove members, manage team settings
- **Member**: Can create analyses, comment, share within team
- **Viewer**: Read-only access to team analyses

### 3. Shared Analyses

All team members can access analyses shared with the team:

```bash
# List team analyses
GET /teams/{team_id}/analyses

# Results include:
# - All analyses created by team members
# - Shared analyses with team permissions
# - Full history and versions
```

### 4. Collaborative Comments

Add threaded comments to analyses:

```bash
# Add comment
POST /teams/{team_id}/analyses/{analysis_id}/comments
{
  "text": "Great insights on the competitive landscape!",
  "parent_id": null  # For threaded replies
}

# List comments
GET /teams/{team_id}/analyses/{analysis_id}/comments
```

**Features**:
- Threaded discussions
- Reactions (👍, ❤️, etc.)
- Edit history tracking
- Email notifications

## Switching Cost Features

### Shared Knowledge Accumulation

As teams collaborate, they build:
1. **Shared Analysis History**: Complete timeline of team insights
2. **Collective Patterns**: Cross-analyst trend identification
3. **Team Conventions**: Shared frameworks and custom approaches
4. **Institutional Memory**: Knowledge that exists only within team context

### Team-Specific Value

The more a team uses ConsultantOS together:
- **More valuable internal references**: Previous analyses become research assets
- **Shared vocabulary**: Custom frameworks and terminology
- **Workflow integration**: Team processes built around platform
- **Member onboarding**: New members inherit team's accumulated knowledge

### Migration Barriers

Switching platforms requires:
1. **Recreating team structure** elsewhere
2. **Losing collaboration history** and threaded discussions
3. **Breaking workflow integrations** team has established
4. **Abandoning shared custom frameworks** and conventions
5. **Retraining team members** on new platform

## Usage Examples

### Creating a Consulting Team

```python
import requests

# Create team
response = requests.post(
    "https://api.consultantos.app/teams",
    json={
        "name": "Acme Consulting",
        "description": "Strategic consulting division",
        "plan": "pro"
    },
    headers={"X-API-Key": "your-api-key"}
)

team_id = response.json()["id"]

# Invite team members
members = [
    {"email": "senior@acme.com", "role": "admin"},
    {"email": "analyst1@acme.com", "role": "member"},
    {"email": "analyst2@acme.com", "role": "member"},
]

for member in members:
    requests.post(
        f"https://api.consultantos.app/teams/{team_id}/members",
        json=member,
        headers={"X-API-Key": "your-api-key"}
    )
```

### Collaborative Analysis Workflow

```python
# Senior analyst creates analysis
response = requests.post(
    "https://api.consultantos.app/analyze",
    json={
        "company": "Tesla",
        "industry": "Electric Vehicles",
        "frameworks": ["porter", "swot", "blue_ocean"],
        "depth": "comprehensive"
    },
    headers={"X-API-Key": "senior-api-key"}
)

analysis_id = response.json()["report_id"]

# Junior analyst adds insights via comments
requests.post(
    f"https://api.consultantos.app/teams/{team_id}/analyses/{analysis_id}/comments",
    json={
        "text": "I noticed their battery technology creates significant supplier power. Should we expand the Porter analysis?"
    },
    headers={"X-API-Key": "analyst-api-key"}
)

# Senior responds with threaded reply
requests.post(
    f"https://api.consultantos.app/teams/{team_id}/analyses/{analysis_id}/comments",
    json={
        "text": "Great catch! Let's create a custom framework focusing on battery supply chain.",
        "parent_id": comment_id
    },
    headers={"X-API-Key": "senior-api-key"}
)
```

## Best Practices

### Team Structure

1. **Small Core Teams**: 3-5 active analysts per team for optimal collaboration
2. **Clear Roles**: Assign admin roles to decision-makers, members to analysts
3. **Topic-Based Teams**: Create separate teams for different client sectors or practice areas

### Collaboration Patterns

1. **Analysis Review**: Have senior analysts review and comment on junior work
2. **Peer Validation**: Require multiple team members to validate key findings
3. **Knowledge Sharing**: Use comments to explain reasoning and share insights
4. **Version Tracking**: Compare team analyses over time to track market changes

### Retention Optimization

1. **Encourage Commenting**: Active discussions increase team investment
2. **Build Custom Frameworks**: Team-specific frameworks create unique value
3. **Share Broadly**: Cross-team sharing increases organizational dependency
4. **Document Processes**: Use platform for team knowledge management

## Metrics to Track

### Team Health
- Active members per team
- Comments per analysis
- Cross-member collaboration frequency
- Custom framework creation rate

### Switching Cost Indicators
- Shared analysis count
- Team tenure (time since first analysis)
- Custom framework usage
- Comment thread depth

### Growth Signals
- Teams creating new teams (organizational expansion)
- Member invitation rate
- Upgrade from free to pro/enterprise
- Integration with team workflows

## API Reference

**Base URL**: `https://api.consultantos.app`

### Teams
- `POST /teams` - Create team
- `GET /teams` - List user's teams
- `GET /teams/{id}` - Get team details
- `DELETE /teams/{id}` - Delete team (owner only)

### Members
- `POST /teams/{id}/members` - Invite member
- `GET /teams/{id}/members` - List members
- `DELETE /teams/{id}/members/{user_id}` - Remove member

### Collaboration
- `GET /teams/{id}/analyses` - List team analyses
- `POST /teams/{id}/analyses/{analysis_id}/comments` - Add comment
- `GET /teams/{id}/analyses/{analysis_id}/comments` - List comments

## Support

For team setup assistance or enterprise inquiries:
- Email: teams@consultantos.app
- Documentation: https://docs.consultantos.app/teams
- Enterprise sales: https://consultantos.app/enterprise
