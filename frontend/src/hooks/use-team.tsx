
import React, { createContext, useContext, useState, useEffect } from 'react';
import { Team, TeamMember } from '../types';
import { useAuth } from './use-auth';
import { generateTeamInviteCode } from '../lib/utils';

interface TeamContextType {
  team: Team | null;
  loading: boolean;
  createTeam: (name: string) => Promise<Team>;
  joinTeam: (inviteCode: string) => Promise<Team>;
  addMember: (userId: string, name: string) => void;
  removeMember: (userId: string) => void;
}

// Mock teams for demo purposes
const mockTeams: Team[] = [];

const TeamContext = createContext<TeamContextType | undefined>(undefined);

export const TeamProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, updateUserTeam } = useAuth();
  const [team, setTeam] = useState<Team | null>(null);
  const [loading, setLoading] = useState(true);

  // Load team data when user changes
  useEffect(() => {
    const loadTeam = async () => {
      if (!user) {
        setTeam(null);
        setLoading(false);
        return;
      }

      if (user.teamId) {
        try {
          // In a real app, this would be an API call
          const foundTeam = mockTeams.find(t => t.id === user.teamId);
          if (foundTeam) {
            setTeam(foundTeam);
          }
        } catch (error) {
          console.error("Failed to load team:", error);
        }
      }
      setLoading(false);
    };

    loadTeam();
  }, [user]);

  const createTeam = async (name: string): Promise<Team> => {
    if (!user) throw new Error("Must be logged in to create a team");
    
    setLoading(true);
    try {
      // In a real app, this would be an API call
      const newTeam: Team = {
        id: `team-${Date.now()}`,
        name,
        inviteCode: generateTeamInviteCode(),
        createdById: user.id,
        createdAt: new Date(),
        members: [
          {
            id: `member-${Date.now()}`,
            userId: user.id,
            teamId: `team-${Date.now()}`,
            name: user.name,
            role: 'admin',
            joinedAt: new Date(),
          }
        ]
      };
      
      mockTeams.push(newTeam);
      setTeam(newTeam);
      updateUserTeam(newTeam.id);
      return newTeam;
    } catch (error) {
      console.error("Failed to create team:", error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const joinTeam = async (inviteCode: string): Promise<Team> => {
    if (!user) throw new Error("Must be logged in to join a team");
    
    setLoading(true);
    try {
      // In a real app, this would be an API call
      const foundTeam = mockTeams.find(t => t.inviteCode === inviteCode);
      if (!foundTeam) {
        throw new Error("Invalid team invite code");
      }

      // Check if user is already a member
      const isMember = foundTeam.members.some(m => m.userId === user.id);
      if (!isMember) {
        const newMember: TeamMember = {
          id: `member-${Date.now()}`,
          userId: user.id,
          teamId: foundTeam.id,
          name: user.name,
          role: 'member',
          joinedAt: new Date(),
        };
        foundTeam.members.push(newMember);
      }
      
      setTeam(foundTeam);
      updateUserTeam(foundTeam.id);
      return foundTeam;
    } catch (error) {
      console.error("Failed to join team:", error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const addMember = (userId: string, name: string) => {
    if (!team) return;
    
    const newMember: TeamMember = {
      id: `member-${Date.now()}`,
      userId,
      teamId: team.id,
      name,
      role: 'member',
      joinedAt: new Date(),
    };
    
    const updatedTeam = { 
      ...team, 
      members: [...team.members, newMember] 
    };
    
    setTeam(updatedTeam);
    // In a real app, this would update via an API call
  };

  const removeMember = (userId: string) => {
    if (!team || !user) return;
    
    // Only allow admins to remove members
    if (team.createdById !== user.id) {
      console.error("Only team admin can remove members");
      return;
    }
    
    const updatedTeam = {
      ...team,
      members: team.members.filter(m => m.userId !== userId)
    };
    
    setTeam(updatedTeam);
    // In a real app, this would update via an API call
  };

  return (
    <TeamContext.Provider
      value={{
        team,
        loading,
        createTeam,
        joinTeam,
        addMember,
        removeMember
      }}
    >
      {children}
    </TeamContext.Provider>
  );
};

export const useTeam = () => {
  const context = useContext(TeamContext);
  if (context === undefined) {
    throw new Error("useTeam must be used within a TeamProvider");
  }
  return context;
};
