
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTeam } from "../../hooks/use-team";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import { useToast } from "@/hooks/use-toast";

const TeamSetup: React.FC = () => {
  const [teamName, setTeamName] = useState("");
  const [inviteCode, setInviteCode] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { createTeam, joinTeam } = useTeam();
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleCreateTeam = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await createTeam(teamName);
      toast({
        title: "Team created!",
        description: "Your new team has been created successfully.",
      });
      navigate("/");
    } catch (error) {
      console.error("Failed to create team:", error);
      toast({
        title: "Failed to create team",
        description: "Please try again later.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleJoinTeam = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await joinTeam(inviteCode);
      toast({
        title: "Team joined!",
        description: "You have successfully joined the team.",
      });
      navigate("/");
    } catch (error) {
      console.error("Failed to join team:", error);
      toast({
        title: "Failed to join team",
        description: "Please check the invite code and try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="w-full max-w-md">
        <div className="text-center space-y-2 mb-6">
          <h1 className="text-3xl font-bold">Set up your team</h1>
          <p className="text-muted-foreground">
            Create a new team or join an existing one
          </p>
        </div>

        <Card className="animate-fade-in">
          <Tabs defaultValue="create">
            <TabsList className="grid grid-cols-2 w-full">
              <TabsTrigger value="create">Create Team</TabsTrigger>
              <TabsTrigger value="join">Join Team</TabsTrigger>
            </TabsList>

            <TabsContent value="create">
              <form onSubmit={handleCreateTeam}>
                <CardHeader>
                  <CardTitle>Create a new team</CardTitle>
                  <CardDescription>
                    Start fresh with a new team for your organization
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="team-name">Team Name</Label>
                    <Input
                      id="team-name"
                      placeholder="Acme Engineering Team"
                      required
                      value={teamName}
                      onChange={(e) => setTeamName(e.target.value)}
                    />
                  </div>
                </CardContent>
                <CardFooter>
                  <Button type="submit" className="w-full" disabled={isLoading}>
                    {isLoading ? "Creating..." : "Create Team"}
                  </Button>
                </CardFooter>
              </form>
            </TabsContent>

            <TabsContent value="join">
              <form onSubmit={handleJoinTeam}>
                <CardHeader>
                  <CardTitle>Join an existing team</CardTitle>
                  <CardDescription>
                    Enter an invite code to join your team
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="invite-code">Invite Code</Label>
                    <Input
                      id="invite-code"
                      placeholder="e.g., ABC123"
                      required
                      value={inviteCode}
                      onChange={(e) => setInviteCode(e.target.value.toUpperCase())}
                    />
                  </div>
                </CardContent>
                <CardFooter>
                  <Button type="submit" className="w-full" disabled={isLoading}>
                    {isLoading ? "Joining..." : "Join Team"}
                  </Button>
                </CardFooter>
              </form>
            </TabsContent>
          </Tabs>
        </Card>
      </div>
    </div>
  );
};

export default TeamSetup;
