"""
Team service for handling team-related operations.
"""

import secrets
import string
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union, cast

from fastapi import HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.sql import Insert, Select, Update

from ..db.models import Team, TeamInvitation, User, team_members


def create_team(
    db: Session, creator_id: int, name: str, description: Optional[str] = None
) -> Team:
    """
    Create a new team with the provided user as creator.

    Args:
        db: Database session
        creator_id: ID of the user creating the team
        name: Name of the team
        description: Optional description of the team

    Returns:
        Team: The newly created team

    Raises:
        HTTPException: If the creator doesn't exist or other errors occur
    """
    # Check if creator exists
    user = db.query(User).filter(User.id == creator_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Generate a unique invite code
    invite_code = _generate_invite_code()

    # Create new team
    team = Team(
        name=name,
        description=description,
        invite_code=invite_code,
        created_by_id=creator_id,
    )

    db.add(team)
    db.flush()

    # Add creator as a team member with 'admin' role
    stmt = team_members.insert().values(
        user_id=creator_id,
        team_id=team.id,
        role="admin",
        joined_at=func.now(),
        is_active=True,
    )
    db.execute(stmt)

    # Commit the transaction
    db.commit()
    db.refresh(team)

    return team


def join_team_by_invite_code(
    db: Session, user_id: int, invite_code: str
) -> Tuple[Team, str]:
    """
    Add a user to a team using an invite code.

    Args:
        db: Database session
        user_id: ID of the user joining the team
        invite_code: The invite code of the team

    Returns:
        Tuple[Team, str]: The team that was joined and the role assigned

    Raises:
        HTTPException: If user or team doesn't exist, or user is already in the team
    """
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Find team by invite code
    team = db.query(Team).filter(Team.invite_code == invite_code).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid invite code"
        )

    # Check if user is already in the team
    member = (
        db.query(team_members)
        .filter(
            and_(team_members.c.user_id == user_id, team_members.c.team_id == team.id)
        )
        .first()
    )

    if member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this team",
        )

    # Add user to team with 'member' role
    stmt = team_members.insert().values(
        user_id=user_id,
        team_id=team.id,
        role="member",
        joined_at=func.now(),
        is_active=True,
    )
    db.execute(stmt)
    db.commit()

    return team, "member"


def get_team_by_id(db: Session, team_id: int) -> Optional[Team]:
    """
    Get a team by its ID.

    Args:
        db: Database session
        team_id: ID of the team to retrieve

    Returns:
        Optional[Team]: The team if found, None otherwise
    """
    return db.query(Team).filter(Team.id == team_id).first()


class TeamInfo(Dict[str, Any]):
    """Team information dictionary with proper typing."""

    team: Team
    role: str
    joined_at: datetime


def get_user_teams(db: Session, user_id: int) -> List[TeamInfo]:
    """
    Get all teams that a user is a member of with role and join date.

    Args:
        db: Database session
        user_id: ID of the user

    Returns:
        List[TeamInfo]: List of dictionaries containing team information, role, and joined_at date
    """
    results = (
        db.query(Team, team_members.c.role, team_members.c.joined_at)
        .join(team_members, team_members.c.team_id == Team.id)
        .filter(
            and_(team_members.c.user_id == user_id, team_members.c.is_active == True)
        )
        .all()
    )

    teams: List[TeamInfo] = []
    for team_row, role, joined_at in results:
        teams.append(TeamInfo({"team": team_row, "role": role, "joined_at": joined_at}))

    return teams


class MemberInfo(Dict[str, Any]):
    """Member information dictionary with proper typing."""

    user: User
    role: str
    joined_at: datetime
    is_active: bool


def get_team_members(db: Session, team_id: int) -> List[MemberInfo]:
    """
    Get all members of a team with their roles and join dates.

    Args:
        db: Database session
        team_id: ID of the team

    Returns:
        List[MemberInfo]: List of dictionaries containing user information, role, and joined_at date
    """
    results = (
        db.query(
            User,
            team_members.c.role,
            team_members.c.joined_at,
            team_members.c.is_active,
        )
        .join(team_members, team_members.c.user_id == User.id)
        .filter(team_members.c.team_id == team_id)
        .all()
    )

    members: List[MemberInfo] = []
    for user_row, role, joined_at, is_active in results:
        members.append(
            MemberInfo(
                {
                    "user": user_row,
                    "role": role,
                    "joined_at": joined_at,
                    "is_active": is_active,
                }
            )
        )

    return members


def update_team(
    db: Session,
    team_id: int,
    user_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> Team:
    """
    Update a team's information.

    Args:
        db: Database session
        team_id: ID of the team to update
        user_id: ID of the user making the update (must be admin or creator)
        name: New name for the team (optional)
        description: New description for the team (optional)

    Returns:
        Team: The updated team

    Raises:
        HTTPException: If team doesn't exist, or user doesn't have permission
    """
    # Check if team exists
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )

    # Check if user has permission (team creator or admin)
    role = (
        db.query(team_members.c.role)
        .filter(
            and_(
                team_members.c.user_id == user_id,
                team_members.c.team_id == team_id,
                team_members.c.is_active == True,
            )
        )
        .scalar()
    )

    if not role or role not in ["admin", "owner"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this team",
        )

    # Update team information
    if name is not None:
        team.name = name  # type: ignore
    if description is not None:
        team.description = description  # type: ignore

    team.updated_at = datetime.utcnow()  # type: ignore
    db.commit()
    db.refresh(team)

    return team


def remove_team_member(
    db: Session, team_id: int, admin_id: int, member_id: int
) -> bool:
    """
    Remove a member from a team.

    Args:
        db: Database session
        team_id: ID of the team
        admin_id: ID of the admin performing the removal
        member_id: ID of the member to remove

    Returns:
        bool: True if the member was removed successfully

    Raises:
        HTTPException: If team/user doesn't exist, or requester lacks permission
    """
    # Check if team exists
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )

    # Check if admin has permission
    role = (
        db.query(team_members.c.role)
        .filter(
            and_(
                team_members.c.user_id == admin_id,
                team_members.c.team_id == team_id,
                team_members.c.is_active == True,
            )
        )
        .scalar()
    )

    if not role or role not in ["admin", "owner"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to remove members from this team",
        )

    # Cannot remove yourself
    if admin_id == member_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot remove yourself from the team",
        )

    # Check if the member is part of the team
    member_record = (
        db.query(team_members)
        .filter(
            and_(
                team_members.c.user_id == member_id,
                team_members.c.team_id == team_id,
                team_members.c.is_active == True,
            )
        )
        .first()
    )

    if not member_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not a member of this team",
        )

    # Set member as inactive instead of deleting
    db.execute(
        team_members.update()
        .where(
            and_(team_members.c.user_id == member_id, team_members.c.team_id == team_id)
        )
        .values(is_active=False)
    )

    db.commit()

    return True


def regenerate_invite_code(db: Session, team_id: int, user_id: int) -> str:
    """
    Regenerate the invite code for a team.

    Args:
        db: Database session
        team_id: ID of the team
        user_id: ID of the user requesting the code regeneration (must be admin)

    Returns:
        str: The new invite code

    Raises:
        HTTPException: If team doesn't exist, or user doesn't have permission
    """
    # Check if team exists
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )

    # Check if user has permission
    role = (
        db.query(team_members.c.role)
        .filter(
            and_(
                team_members.c.user_id == user_id,
                team_members.c.team_id == team_id,
                team_members.c.is_active == True,
            )
        )
        .scalar()
    )

    if not role or role not in ["admin", "owner"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to regenerate the invite code",
        )

    # Generate new invite code
    new_code = _generate_invite_code()
    team.invite_code = new_code  # type: ignore
    team.updated_at = datetime.utcnow()  # type: ignore

    db.commit()
    db.refresh(team)

    return new_code


def create_team_invitation(
    db: Session,
    team_id: int,
    inviter_id: int,
    invitee_email: str,
    invitee_id: Optional[int] = None,
    expiration_days: int = 7,
) -> TeamInvitation:
    """
    Create an invitation to join a team.

    Args:
        db: Database session
        team_id: ID of the team
        inviter_id: ID of the user sending the invitation
        invitee_email: Email of the invitee
        invitee_id: ID of the invitee if they are a registered user (optional)
        expiration_days: Number of days until the invitation expires

    Returns:
        TeamInvitation: The created invitation

    Raises:
        HTTPException: If team/user doesn't exist, or inviter lacks permission
    """
    # Check if team exists
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )

    # Check if inviter is part of the team and has permission
    role = (
        db.query(team_members.c.role)
        .filter(
            and_(
                team_members.c.user_id == inviter_id,
                team_members.c.team_id == team_id,
                team_members.c.is_active == True,
            )
        )
        .scalar()
    )

    if not role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this team",
        )

    # Check if invitee is already a member of the team
    if invitee_id:
        member = (
            db.query(team_members)
            .filter(
                and_(
                    team_members.c.user_id == invitee_id,
                    team_members.c.team_id == team_id,
                    team_members.c.is_active == True,
                )
            )
            .first()
        )

        if member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this team",
            )

    # Check if there's an active invitation for this user/email
    existing_invitation = (
        db.query(TeamInvitation)
        .filter(
            and_(
                TeamInvitation.team_id == team_id,
                TeamInvitation.status == "pending",
                (
                    TeamInvitation.invitee_id == invitee_id
                    if invitee_id
                    else TeamInvitation.invitee_email == invitee_email
                ),
            )
        )
        .first()
    )

    if existing_invitation:
        # Return the existing invitation
        return existing_invitation

    # Generate invitation token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=expiration_days)

    # Create invitation
    invitation = TeamInvitation(
        team_id=team_id,
        inviter_id=inviter_id,
        invitee_id=invitee_id,
        invitee_email=invitee_email,
        status="pending",
        token=token,
        expires_at=expires_at,
    )

    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    return invitation


def _generate_invite_code(length: int = 8) -> str:
    """
    Generate a random invite code.

    Args:
        length: Length of the invite code to generate

    Returns:
        str: The generated invite code
    """
    chars = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))
