
import React from "react";
import { useTeam } from "../../hooks/use-team";
import MembersList from "../../components/team/MembersList";
import InviteMembers from "../../components/team/InviteMembers";

const TeamPage: React.FC = () => {
  const { team, loading } = useTeam();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-pulse text-xl text-pulse-primary">Loading team details...</div>
      </div>
    );
  }

  if (!team) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <p className="text-lg mb-2">You're not part of any team yet.</p>
          <a href="/onboarding" className="text-pulse-primary hover:underline">Set up your team</a>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">{team.name}</h1>
        <p className="text-muted-foreground">
          Team management and collaboration
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <MembersList />
        </div>
        <div>
          <InviteMembers />
        </div>
      </div>
    </div>
  );
};

export default TeamPage;
