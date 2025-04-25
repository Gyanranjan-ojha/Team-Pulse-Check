
import React from "react";
import { Activity } from "../../types";
import { formatRelativeTime, getActivityColor } from "../../lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { GitPullRequest, MessageSquare, GitCommit, AlertTriangle } from "lucide-react";

interface ActivityCardProps {
  activities: Activity[];
  title: string;
}

const ActivityCard: React.FC<ActivityCardProps> = ({ activities, title }) => {
  if (!activities || activities.length === 0) {
    return (
      <Card className="h-[300px]">
        <CardHeader>
          <CardTitle className="text-lg">{title}</CardTitle>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-[224px]">
          <p className="text-muted-foreground">No recent activity</p>
        </CardContent>
      </Card>
    );
  }

  const getActivityIcon = (activity: Activity) => {
    if (activity.category === "code") return <GitCommit className="h-4 w-4" />;
    if (activity.category === "review") return <GitPullRequest className="h-4 w-4" />;
    if (activity.category === "chat") return <MessageSquare className="h-4 w-4" />;
    if (activity.category === "blocker") return <AlertTriangle className="h-4 w-4" />;
    return null;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4 max-h-[224px] overflow-y-auto">
        {activities.slice(0, 5).map((activity) => (
          <div key={activity.id} className="activity-item">
            <span className={getActivityColor(activity.category, activity.source)}>
              {getActivityIcon(activity)}
            </span>
            <div className="flex-1">
              <p className="text-sm font-medium">{activity.title}</p>
              {activity.description && (
                <p className="text-xs text-muted-foreground">
                  {activity.description}
                </p>
              )}
            </div>
            <div className="text-xs text-muted-foreground">
              {formatRelativeTime(new Date(activity.timestamp))}
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
};

export default ActivityCard;
