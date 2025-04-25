"""
Database models for the PulseCheck team activity tracker.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


# Association table for user-team many-to-many relationship
team_members = Table(
    "team_members",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("team_id", Integer, ForeignKey("teams.id"), primary_key=True),
    Column("role", String(20), default="member"),
    Column("joined_at", DateTime, default=func.now()),
    Column("is_active", Boolean, default=True),
)


class User(Base):
    """
    Represents a user in the system.

    Attributes:
        id (Integer): Primary key for the user
        email (String): User's email address, unique
        username (String): User's username, unique
        hashed_password (String): Hashed password for the user
        full_name (String): User's full name
        is_active (Boolean): Whether the user account is active
        is_superuser (Boolean): Whether the user has superuser privileges
        created_at (DateTime): Timestamp of user creation
        updated_at (DateTime): Timestamp of last update
        last_login (DateTime): Timestamp of user's last login

    Relationships:
        teams (List[Team]): Many-to-many relationship with Team model via team_members table
        activities (List[Activity]): One-to-many relationship with Activity model
        sent_invitations (List[TeamInvitation]): One-to-many relationship for sent invitations
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )
    last_login = Column(DateTime, nullable=True)

    # Relationships
    teams: Mapped[List["Team"]] = relationship(
        "Team", secondary=team_members, back_populates="members"
    )
    activities: Mapped[List["Activity"]] = relationship(
        "Activity", back_populates="user"
    )
    sent_invitations: Mapped[List["TeamInvitation"]] = relationship(
        "TeamInvitation",
        foreign_keys="[TeamInvitation.inviter_id]",
        back_populates="inviter",
    )
    received_invitations: Mapped[List["TeamInvitation"]] = relationship(
        "TeamInvitation",
        foreign_keys="[TeamInvitation.invitee_id]",
        back_populates="invitee",
    )
    sessions: Mapped[List["UserSession"]] = relationship(
        "UserSession", back_populates="user", cascade="all, delete-orphan"
    )


class UserSession(Base):
    """
    Represents a user login session.

    Attributes:
        id (Integer): Primary key for the session
        user_id (Integer): Foreign key to User model
        token (String): Unique session token
        expires_at (DateTime): Session expiration timestamp
        created_at (DateTime): Timestamp when session was created
        last_active_at (DateTime): Timestamp of last activity
        ip_address (String): IP address used for login
        user_agent (String): User agent information
        is_active (Boolean): Whether the session is currently active

    Relationships:
        user (User): Relationship to User model
    """

    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    last_active_at = Column(DateTime, nullable=False, default=func.now())
    ip_address = Column(String(45), nullable=True)  # IPv6 can be up to 45 chars
    user_agent = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="sessions")


class Team(Base):
    """
    Represents a team in the system.

    Attributes:
        id (Integer): Primary key for the team
        name (String): Team name
        description (Text): Team description
        invite_code (String): Unique code for inviting users to the team
        is_active (Boolean): Whether the team is active
        created_at (DateTime): Timestamp of team creation
        updated_at (DateTime): Timestamp of last update
        created_by_id (Integer): Foreign key to User model for team creator

    Relationships:
        members (List[User]): Many-to-many relationship with User model via team_members table
        activities (List[Activity]): One-to-many relationship with Activity model
        metrics (List[TeamMetric]): One-to-many relationship with TeamMetric model
        invitations (List[TeamInvitation]): One-to-many relationship with TeamInvitation model
    """

    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    invite_code = Column(String(20), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    members: Mapped[List["User"]] = relationship(
        "User", secondary=team_members, back_populates="teams"
    )
    activities: Mapped[List["Activity"]] = relationship(
        "Activity", back_populates="team"
    )
    metrics: Mapped[List["TeamMetric"]] = relationship(
        "TeamMetric", back_populates="team"
    )
    invitations: Mapped[List["TeamInvitation"]] = relationship(
        "TeamInvitation", back_populates="team"
    )


class ActivityType(Base):
    """
    Represents different types of activities that can be tracked.

    Attributes:
        id (Integer): Primary key for the activity type
        name (String): Name of the activity type (e.g., "commit", "message", "meeting")
        description (Text): Description of the activity type
        icon (String): Icon identifier for UI display
        color (String): Color code for UI display
        weight (Float): Weight factor for scoring/metrics calculation
        is_active (Boolean): Whether the activity type is active
        created_at (DateTime): Timestamp of creation
        updated_at (DateTime): Timestamp of last update

    Relationships:
        activities (List[Activity]): One-to-many relationship with Activity model
    """

    __tablename__ = "activity_types"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)
    color = Column(String(20), nullable=True)
    weight = Column(Float, default=1.0, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    # Relationships
    activities: Mapped[List["Activity"]] = relationship(
        "Activity", back_populates="activity_type"
    )


class Activity(Base):
    """
    Represents an activity or event in the system.

    Attributes:
        id (Integer): Primary key for the activity
        user_id (Integer): Foreign key to User model
        team_id (Integer): Foreign key to Team model
        activity_type_id (Integer): Foreign key to ActivityType model
        title (String): Title or summary of the activity
        description (Text): Detailed description of the activity
        timestamp (DateTime): When the activity occurred
        duration_minutes (Integer): Duration of the activity in minutes (if applicable)
        impact_score (Float): Calculated impact score for the activity
        is_simulated (Boolean): Whether this is real or simulated data
        created_at (DateTime): Timestamp of creation in the system
        updated_at (DateTime): Timestamp of last update

    Relationships:
        user (User): Relationship to User model
        team (Team): Relationship to Team model
        activity_type (ActivityType): Relationship to ActivityType model
    """

    __tablename__ = "activities"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)
    activity_type_id = Column(
        Integer, ForeignKey("activity_types.id"), nullable=False, index=True
    )
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer, nullable=True)
    impact_score = Column(Float, default=0.0, nullable=False)
    is_simulated = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="activities")
    team: Mapped["Team"] = relationship("Team", back_populates="activities")
    activity_type: Mapped["ActivityType"] = relationship(
        "ActivityType", back_populates="activities"
    )


class TeamMetric(Base):
    """
    Represents aggregated team metrics for a specific time period.

    Attributes:
        id (Integer): Primary key for the team metric
        team_id (Integer): Foreign key to Team model
        metric_type (String): Type of metric (e.g., "activity_count", "collaboration_score")
        value (Float): Numerical value of the metric
        period_start (DateTime): Start of the period for this metric
        period_end (DateTime): End of the period for this metric
        created_at (DateTime): Timestamp of creation
        updated_at (DateTime): Timestamp of last update

    Relationships:
        team (Team): Relationship to Team model
    """

    __tablename__ = "team_metrics"

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)
    metric_type = Column(String(50), nullable=False)
    value = Column(Float, nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    # Relationships
    team: Mapped["Team"] = relationship("Team", back_populates="metrics")

    # Constraints
    __table_args__ = (
        UniqueConstraint(
            "team_id",
            "metric_type",
            "period_start",
            "period_end",
            name="uq_team_metric_period",
        ),
    )


class TeamInvitation(Base):
    """
    Represents an invitation to join a team.

    Attributes:
        id (Integer): Primary key for the invitation
        team_id (Integer): Foreign key to Team model
        inviter_id (Integer): Foreign key to User model for the user who sent the invitation
        invitee_id (Integer): Foreign key to User model for the user who received the invitation,
                             can be null if invitation is by email
        invitee_email (String): Email of the invitee if not a registered user
        status (String): Status of the invitation (pending, accepted, rejected, expired)
        token (String): Unique token for invitation verification
        expires_at (DateTime): Expiration timestamp for the invitation
        created_at (DateTime): Timestamp of creation
        updated_at (DateTime): Timestamp of last update

    Relationships:
        team (Team): Relationship to Team model
        inviter (User): Relationship to User model for the inviter
        invitee (User): Relationship to User model for the invitee
    """

    __tablename__ = "team_invitations"

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)
    inviter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    invitee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    invitee_email = Column(String(255), nullable=True)
    status = Column(
        Enum("pending", "accepted", "rejected", "expired", name="invitation_status"),
        default="pending",
        nullable=False,
    )
    token = Column(String(100), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    # Relationships
    team: Mapped["Team"] = relationship("Team", back_populates="invitations")
    inviter: Mapped["User"] = relationship(
        "User", foreign_keys=[inviter_id], back_populates="sent_invitations"
    )
    invitee: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[invitee_id], back_populates="received_invitations"
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint(
            "team_id", "invitee_id", "status", name="uq_team_invitee_pending"
        ),
        UniqueConstraint(
            "team_id", "invitee_email", "status", name="uq_team_invitee_email_pending"
        ),
    )


class UserMetric(Base):
    """
    Represents aggregated metrics for a specific user in a team.

    Attributes:
        id (Integer): Primary key for the user metric
        user_id (Integer): Foreign key to User model
        team_id (Integer): Foreign key to Team model
        metric_type (String): Type of metric (e.g., "activity_score", "engagement_level")
        value (Float): Numerical value of the metric
        period_start (DateTime): Start of the period for this metric
        period_end (DateTime): End of the period for this metric
        created_at (DateTime): Timestamp of creation
        updated_at (DateTime): Timestamp of last update

    Relationships:
        user (User): Relationship to User model
        team (Team): Relationship to Team model
    """

    __tablename__ = "user_metrics"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)
    metric_type = Column(String(50), nullable=False)
    value = Column(Float, nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship("User")
    team: Mapped["Team"] = relationship("Team")

    # Constraints
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "team_id",
            "metric_type",
            "period_start",
            "period_end",
            name="uq_user_team_metric_period",
        ),
    )
