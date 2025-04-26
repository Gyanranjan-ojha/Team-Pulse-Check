"""
Team routes for the PulseCheck API.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, cast

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field

from ..db.database import get_db
from ..db.models import Team, TeamInvitation, User
from ..services import team_service
from ..services.auth_service import get_current_user

router = APIRouter(tags=["teams"])


class TeamCreate(BaseModel):
    """Schema for creating a new team."""

    name: str = Field(..., min_length=1, max_length=255, description="Name of the team")
    description: Optional[str] = Field(
        None, description="Optional description of the team"
    )


class TeamResponse(BaseModel):
    """Schema for team response data."""

    id: int
    name: str
    description: Optional[str] = None
    invite_code: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TeamMemberResponse(BaseModel):
    """Schema for team member response data."""

    user_id: int
    username: str
    email: str
    full_name: Optional[str] = None
    role: str
    joined_at: datetime
    is_active: bool


class TeamInvitationCreate(BaseModel):
    """Schema for creating a team invitation."""

    invitee_email: EmailStr = Field(..., description="Email of the person to invite")


class TeamInvitationResponse(BaseModel):
    """Schema for team invitation response data."""

    id: int
    team_id: int
    team_name: str
    inviter_email: str
    invitee_email: str
    status: str
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class TeamUpdateRequest(BaseModel):
    """Schema for updating team information."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class JoinTeamRequest(BaseModel):
    """Schema for joining a team by invite code."""

    invite_code: str = Field(..., description="The team's invite code")


class UserTeamResponse(BaseModel):
    """Schema for user's team list response."""

    team: TeamResponse
    role: str
    joined_at: datetime


@router.post("/teams", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_data: TeamCreate, db=Depends(get_db), current_user=Depends(get_current_user)
) -> Team:
    """
    Create a new team.

    The authenticated user will be assigned as the team creator and admin.

    Authentication:
        - Requires Bearer token in the Authorization header
        - Example: Authorization: Bearer <your_token>

    Request Body:
        - name: String (required) - Name of the team
        - description: String (optional) - Description of the team

    Returns:
        - 201 Created: Team object with id, name, description, invite_code, and timestamps
        - 401 Unauthorized: If the token is missing or invalid
        - 422 Unprocessable Entity: If the request body is invalid
    """
    team = team_service.create_team(
        db=db,
        creator_id=current_user.id,
        name=team_data.name,
        description=team_data.description,
    )
    return team


@router.post("/teams/join", response_model=TeamResponse)
async def join_team(
    join_data: JoinTeamRequest,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
) -> Team:
    """
    Join a team using an invite code.

    Authentication:
        - Requires Bearer token in the Authorization header
        - Example: Authorization: Bearer <your_token>

    Request Body:
        - invite_code: String (required) - The invite code of the team to join

    Returns:
        - 200 OK: Team object with details of the joined team
        - 400 Bad Request: If the user is already a member of the team
        - 401 Unauthorized: If the token is missing or invalid
        - 404 Not Found: If the invite code is invalid
    """
    team, _ = team_service.join_team_by_invite_code(
        db=db, user_id=current_user.id, invite_code=join_data.invite_code
    )
    return team


@router.get("/teams/my", response_model=List[UserTeamResponse])
async def get_my_teams(
    db=Depends(get_db), current_user=Depends(get_current_user)
) -> List[Dict]:
    """
    Get all teams that the current user is a member of.

    Authentication:
        - Requires Bearer token in the Authorization header
        - Example: Authorization: Bearer <your_token>

    Returns:
        - 200 OK: List of team objects that the user is a member of, including:
            - team: Team object with id, name, description, invite_code, etc.
            - role: User's role in the team (admin, member, etc.)
            - joined_at: When the user joined the team
        - 401 Unauthorized: If the token is missing or invalid
    """
    teams = team_service.get_user_teams(db=db, user_id=current_user.id)
    return teams


@router.get("/teams/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: int, db=Depends(get_db), current_user=Depends(get_current_user)
) -> Team:
    """
    Get information about a specific team.

    User must be a member of the team to access this endpoint.

    Authentication:
        - Requires Bearer token in the Authorization header
        - Example: Authorization: Bearer <your_token>

    Path Parameters:
        - team_id: Integer (required) - ID of the team to retrieve

    Returns:
        - 200 OK: Team object with details
        - 401 Unauthorized: If the token is missing or invalid
        - 403 Forbidden: If the user is not a member of the team
        - 404 Not Found: If the team doesn't exist
    """
    # First check if user is a member of this team
    teams = team_service.get_user_teams(db=db, user_id=current_user.id)
    is_member = any(team_info["team"].id == team_id for team_info in teams)

    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this team",
        )

    team = team_service.get_team_by_id(db=db, team_id=team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )

    return team


@router.get("/teams/{team_id}/members", response_model=List[TeamMemberResponse])
async def get_team_members(
    team_id: int,
    include_inactive: bool = Query(False, description="Include inactive members"),
    db=Depends(get_db),
    current_user=Depends(get_current_user),
) -> List[TeamMemberResponse]:
    """
    Get all members of a specific team.

    User must be a member of the team to access this endpoint.

    Authentication:
        - Requires Bearer token in the Authorization header
        - Example: Authorization: Bearer <your_token>

    Path Parameters:
        - team_id: Integer (required) - ID of the team

    Query Parameters:
        - include_inactive: Boolean (optional, default=false) - Whether to include inactive members

    Returns:
        - 200 OK: List of team members with user details, roles, and join dates
        - 401 Unauthorized: If the token is missing or invalid
        - 403 Forbidden: If the user is not a member of the team
    """
    # First check if user is a member of this team
    teams = team_service.get_user_teams(db=db, user_id=current_user.id)
    is_member = any(team_info["team"].id == team_id for team_info in teams)

    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this team",
        )

    members = team_service.get_team_members(db=db, team_id=team_id)

    # Filter out inactive members if requested
    if not include_inactive:
        members = [m for m in members if m["is_active"]]

    # Transform to response model
    result: List[TeamMemberResponse] = []
    for member in members:
        user = cast(User, member["user"])
        result.append(
            TeamMemberResponse(
                user_id=user.id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                role=cast(str, member["role"]),
                joined_at=cast(datetime, member["joined_at"]),
                is_active=cast(bool, member["is_active"]),
            )
        )

    return result


@router.patch("/teams/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: int,
    team_data: TeamUpdateRequest,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
) -> Team:
    """
    Update team information.

    User must be an admin or creator of the team to use this endpoint.

    Authentication:
        - Requires Bearer token in the Authorization header
        - Example: Authorization: Bearer <your_token>

    Path Parameters:
        - team_id: Integer (required) - ID of the team to update

    Request Body:
        - name: String (optional) - New name for the team
        - description: String (optional) - New description for the team

    Returns:
        - 200 OK: Updated team object
        - 401 Unauthorized: If the token is missing or invalid
        - 403 Forbidden: If the user doesn't have permission to update the team
        - 404 Not Found: If the team doesn't exist
        - 422 Unprocessable Entity: If the request body is invalid
    """
    team = team_service.update_team(
        db=db,
        team_id=team_id,
        user_id=current_user.id,
        name=team_data.name,
        description=team_data.description,
    )
    return team


@router.post("/teams/{team_id}/regenerate-invite", response_model=Dict[str, str])
async def regenerate_invite_code(
    team_id: int, db=Depends(get_db), current_user=Depends(get_current_user)
) -> Dict[str, str]:
    """
    Regenerate the invite code for a team.

    User must be an admin or creator of the team to use this endpoint.

    Authentication:
        - Requires Bearer token in the Authorization header
        - Example: Authorization: Bearer <your_token>

    Path Parameters:
        - team_id: Integer (required) - ID of the team

    Returns:
        - 200 OK: Object containing the new invite code {"invite_code": "NEW_CODE"}
        - 401 Unauthorized: If the token is missing or invalid
        - 403 Forbidden: If the user doesn't have permission to regenerate the invite code
        - 404 Not Found: If the team doesn't exist
    """
    new_code = team_service.regenerate_invite_code(
        db=db, team_id=team_id, user_id=current_user.id
    )
    return {"invite_code": new_code}


@router.delete("/teams/{team_id}/members/{member_id}", response_model=Dict[str, bool])
async def remove_member(
    team_id: int,
    member_id: int,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
) -> Dict[str, bool]:
    """
    Remove a member from a team.

    User must be an admin or creator of the team to use this endpoint.

    Authentication:
        - Requires Bearer token in the Authorization header
        - Example: Authorization: Bearer <your_token>

    Path Parameters:
        - team_id: Integer (required) - ID of the team
        - member_id: Integer (required) - ID of the member to remove

    Returns:
        - 200 OK: Object containing success status {"success": true}
        - 400 Bad Request: If the user tries to remove themselves
        - 401 Unauthorized: If the token is missing or invalid
        - 403 Forbidden: If the user doesn't have permission to remove members
        - 404 Not Found: If the team or member doesn't exist
    """
    success = team_service.remove_team_member(
        db=db, team_id=team_id, admin_id=current_user.id, member_id=member_id
    )
    return {"success": success}


@router.post(
    "/teams/{team_id}/invitations",
    response_model=TeamInvitationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def invite_to_team(
    team_id: int,
    invitation_data: TeamInvitationCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
) -> Dict:
    """
    Invite a user to join a team.

    User must be a member of the team to use this endpoint.

    Authentication:
        - Requires Bearer token in the Authorization header
        - Example: Authorization: Bearer <your_token>

    Path Parameters:
        - team_id: Integer (required) - ID of the team

    Request Body:
        - invitee_email: String (required) - Email of the person to invite

    Returns:
        - 201 Created: Invitation object with details including token and expiration
        - 400 Bad Request: If the user is already a member of the team
        - 401 Unauthorized: If the token is missing or invalid
        - 403 Forbidden: If the user is not a member of the team
        - 404 Not Found: If the team doesn't exist
        - 422 Unprocessable Entity: If the request body is invalid
    """
    invitation = team_service.create_team_invitation(
        db=db,
        team_id=team_id,
        inviter_id=current_user.id,
        invitee_email=invitation_data.invitee_email,
    )

    # Get the team name for the response
    team = team_service.get_team_by_id(db=db, team_id=team_id)

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )

    return {
        "id": invitation.id,
        "team_id": team_id,
        "team_name": team.name,
        "inviter_email": current_user.email,
        "invitee_email": invitation.invitee_email,
        "status": invitation.status,
        "expires_at": invitation.expires_at,
        "created_at": invitation.created_at,
    }
