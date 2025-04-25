
import React, { useState, useMemo } from "react";
import { useActivity } from "../../hooks/use-activity";
import { groupActivitiesByDate, formatRelativeTime, getActivityColor } from "../../lib/utils";
import { Activity } from "../../types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { GitPullRequest, MessageSquare, GitCommit, AlertTriangle, Search, RefreshCw } from "lucide-react";

const ActivityPage: React.FC = () => {
  const { activities, loading, refreshActivities } = useActivity();
  const [searchQuery, setSearchQuery] = useState("");
  const [activeTab, setActiveTab] = useState("all");

  const filteredActivities = useMemo(() => {
    if (!activities) return [];

    let filtered = activities;

    // Filter by tab
    if (activeTab !== "all") {
      filtered = filtered.filter(activity => activity.category === activeTab);
    }

    // Filter by search
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        activity => 
          activity.title.toLowerCase().includes(query) || 
          (activity.description && activity.description.toLowerCase().includes(query))
      );
    }

    return filtered;
  }, [activities, activeTab, searchQuery]);

  const groupedActivities = useMemo(() => {
    return groupActivitiesByDate(filteredActivities);
  }, [filteredActivities]);

  const getActivityIcon = (activity: Activity) => {
    if (activity.category === "code") return <GitCommit className="h-4 w-4" />;
    if (activity.category === "review") return <GitPullRequest className="h-4 w-4" />;
    if (activity.category === "chat") return <MessageSquare className="h-4 w-4" />;
    if (activity.category === "blocker") return <AlertTriangle className="h-4 w-4" />;
    return null;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-pulse text-xl text-pulse-primary">Loading activity...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Team Activity</h1>
          <p className="text-muted-foreground">
            Track your team's collaborative efforts over time
          </p>
        </div>

        <div className="flex gap-2">
          <div className="relative w-full md:w-64">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search activities..."
              className="pl-8"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <Button 
            variant="outline" 
            size="icon" 
            onClick={refreshActivities}
            disabled={loading}
          >
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid grid-cols-5 max-w-md">
          <TabsTrigger value="all">All</TabsTrigger>
          <TabsTrigger value="code" className="text-green-500">Code</TabsTrigger>
          <TabsTrigger value="review" className="text-blue-500">PRs</TabsTrigger>
          <TabsTrigger value="chat" className="text-pulse-primary">Messages</TabsTrigger>
          <TabsTrigger value="blocker" className="text-red-500">Blockers</TabsTrigger>
        </TabsList>
      </Tabs>

      <div className="space-y-8">
        {Object.keys(groupedActivities).length === 0 ? (
          <div className="flex items-center justify-center h-40 border rounded-md">
            <p className="text-muted-foreground">No activities found</p>
          </div>
        ) : (
          Object.keys(groupedActivities).map((date) => (
            <div key={date}>
              <h3 className="text-sm font-medium text-muted-foreground mb-4">{date}</h3>
              <div className="space-y-2">
                {groupedActivities[date].map((activity) => (
                  <div
                    key={activity.id}
                    className="flex items-start gap-3 p-3 rounded-md hover:bg-muted/50 transition-colors"
                  >
                    <div className={`mt-1 ${getActivityColor(activity.category, activity.source)}`}>
                      {getActivityIcon(activity)}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <p className="font-medium">{activity.title}</p>
                        <span className="text-xs text-muted-foreground">
                          {formatRelativeTime(new Date(activity.timestamp))}
                        </span>
                      </div>
                      {activity.description && (
                        <p className="text-sm text-muted-foreground mt-1">
                          {activity.description}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ActivityPage;
