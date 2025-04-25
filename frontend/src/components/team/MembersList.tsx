
import React from "react";
import { useTeam } from "../../hooks/use-team";
import { useAuth } from "../../hooks/use-auth";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { User, MoreHorizontal, Crown, UserMinus } from "lucide-react";
import { formatRelativeTime } from "@/lib/utils";
import { useToast } from "@/hooks/use-toast";

const MembersList: React.FC = () => {
  const { team, removeMember } = useTeam();
  const { user } = useAuth();
  const { toast } = useToast();
  
  if (!team) return null;
  
  const isAdmin = team.createdById === user?.id;

  const handleRemoveMember = (userId: string, name: string) => {
    if (!isAdmin) {
      toast({
        title: "Permission denied",
        description: "Only team admins can remove members.",
        variant: "destructive",
      });
      return;
    }

    if (userId === user?.id) {
      toast({
        title: "Cannot remove yourself",
        description: "You cannot remove yourself from the team.",
        variant: "destructive",
      });
      return;
    }

    removeMember(userId);
    toast({
      title: "Member removed",
      description: `${name} has been removed from the team.`,
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Team Members</CardTitle>
        <CardDescription>
          {team.members.length} members in {team.name}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          {team.members.map((member) => (
            <div
              key={member.id}
              className="flex items-center justify-between p-2 rounded-md hover:bg-muted/50"
            >
              <div className="flex items-center gap-3">
                <div className="bg-muted h-10 w-10 rounded-full flex items-center justify-center">
                  <User className="h-5 w-5 text-muted-foreground" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <p className="font-medium">{member.name}</p>
                    {team.createdById === member.userId && (
                      <Crown className="h-4 w-4 text-yellow-500" />
                    )}
                    {member.userId === user?.id && (
                      <span className="text-xs bg-muted px-2 py-0.5 rounded">You</span>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Joined {formatRelativeTime(new Date(member.joinedAt))}
                  </p>
                </div>
              </div>

              {isAdmin && member.userId !== user?.id && (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="icon">
                      <MoreHorizontal className="h-4 w-4" />
                      <span className="sr-only">Actions</span>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem
                      className="text-red-500 focus:text-red-500"
                      onClick={() => handleRemoveMember(member.userId, member.name)}
                    >
                      <UserMinus className="h-4 w-4 mr-2" />
                      Remove member
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default MembersList;
