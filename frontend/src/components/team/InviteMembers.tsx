
import React from "react";
import { useTeam } from "../../hooks/use-team";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { Copy } from "lucide-react";

const InviteMembers: React.FC = () => {
  const { team } = useTeam();
  const { toast } = useToast();
  
  if (!team) return null;
  
  const handleCopyInviteCode = () => {
    navigator.clipboard.writeText(team.inviteCode);
    toast({
      title: "Copied!",
      description: "Invite code copied to clipboard",
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Invite Team Members</CardTitle>
        <CardDescription>
          Share the invite code with your team members
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="space-y-2">
            <p className="text-sm font-medium">Your team invite code:</p>
            <div className="flex items-center gap-2">
              <Input value={team.inviteCode} readOnly />
              <Button 
                variant="outline" 
                size="icon"
                onClick={handleCopyInviteCode}
              >
                <Copy className="h-4 w-4" />
              </Button>
            </div>
          </div>

          <div className="text-sm text-muted-foreground">
            <p>
              Team members will need to:
            </p>
            <ol className="list-decimal list-inside mt-2 space-y-1">
              <li>Sign up for a PulseCheck account</li>
              <li>Select "Join Team" during onboarding</li>
              <li>Enter the invite code above</li>
            </ol>
          </div>
        </div>
      </CardContent>
      <CardFooter>
        <Button className="w-full" onClick={handleCopyInviteCode}>
          Copy Invite Code
        </Button>
      </CardFooter>
    </Card>
  );
};

export default InviteMembers;
