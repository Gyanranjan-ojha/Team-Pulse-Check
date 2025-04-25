
import React from "react";
import { useTeam } from "../../hooks/use-team";
import { useActivity } from "../../hooks/use-activity";
import MetricCard from "../../components/dashboard/MetricCard";
import ActivityCard from "../../components/dashboard/ActivityCard";
import ActivityChart from "../../components/dashboard/ActivityChart";
import TeamActivityChart from "../../components/dashboard/TeamActivityChart";
import { Button } from "@/components/ui/button";
import { RefreshCw, GitPullRequest, MessageSquare, GitCommit, AlertTriangle } from "lucide-react";

const Dashboard: React.FC = () => {
  const { team } = useTeam();
  const { activities, metrics, loading, refreshActivities } = useActivity();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-pulse text-xl text-pulse-primary">Loading dashboard...</div>
      </div>
    );
  }

  if (!team) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <p className="text-lg mb-2">You're not part of any team yet.</p>
          <Button asChild>
            <a href="/onboarding">Set up your team</a>
          </Button>
        </div>
      </div>
    );
  }

  // Calculate metrics for this week
  const getTotalCommits = () => {
    if (!metrics?.dailyCommits) return 0;
    return metrics.dailyCommits.slice(-7).reduce((sum, day) => sum + day.value, 0);
  };

  const getTotalPRs = () => {
    if (!metrics?.dailyPRs) return 0;
    return metrics.dailyPRs.slice(-7).reduce((sum, day) => sum + day.value, 0);
  };

  const getTotalMessages = () => {
    if (!metrics?.dailyMessages) return 0;
    return metrics.dailyMessages.slice(-7).reduce((sum, day) => sum + day.value, 0);
  };

  const getTotalBlockers = () => {
    if (!metrics?.dailyBlockers) return 0;
    return metrics.dailyBlockers.slice(-7).reduce((sum, day) => sum + day.value, 0);
  };

  // Calculate this week's change compared to last week
  const getWeeklyChange = (data: any[] | undefined) => {
    if (!data || data.length < 14) return 0;
    
    const thisWeek = data.slice(-7).reduce((sum, day) => sum + day.value, 0);
    const lastWeek = data.slice(-14, -7).reduce((sum, day) => sum + day.value, 0);
    
    if (lastWeek === 0) return thisWeek > 0 ? 100 : 0;
    return Math.round(((thisWeek - lastWeek) / lastWeek) * 100);
  };

  const getRecentActivities = (category: string) => {
    return activities.filter(a => a.category === category);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Team Dashboard</h1>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={refreshActivities}
          disabled={loading}
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh Data
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard 
          title="Total Commits" 
          value={getTotalCommits()}
          change={getWeeklyChange(metrics?.dailyCommits)}
          icon={<GitCommit className="h-4 w-4 text-green-500" />}
        />
        <MetricCard 
          title="Pull Requests" 
          value={getTotalPRs()}
          change={getWeeklyChange(metrics?.dailyPRs)}
          icon={<GitPullRequest className="h-4 w-4 text-blue-500" />}
        />
        <MetricCard 
          title="Messages" 
          value={getTotalMessages()}
          change={getWeeklyChange(metrics?.dailyMessages)}
          icon={<MessageSquare className="h-4 w-4 text-pulse-primary" />}
        />
        <MetricCard 
          title="Blockers" 
          value={getTotalBlockers()}
          change={getWeeklyChange(metrics?.dailyBlockers)}
          icon={<AlertTriangle className="h-4 w-4 text-red-500" />}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ActivityChart 
          title="Code Commits (Last 14 Days)"
          data={metrics?.dailyCommits || []}
          color="#10b981" // Green
        />
        <ActivityChart 
          title="Pull Requests (Last 14 Days)"
          data={metrics?.dailyPRs || []}
          color="#3b82f6" // Blue
        />
      </div>
      
      {metrics && (
        <TeamActivityChart metrics={metrics} />
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ActivityCard 
          title="Recent Code Activity"
          activities={getRecentActivities("code")}
        />
        <ActivityCard 
          title="Recent Blockers"
          activities={getRecentActivities("blocker")}
        />
      </div>
    </div>
  );
};

export default Dashboard;
