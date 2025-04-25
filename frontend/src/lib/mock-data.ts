
import { 
  Activity, 
  ActivityCategory, 
  ActivitySource, 
  GitHubActivity, 
  SlackActivity,
  Team,
  TeamMetrics,
  MetricData
} from "../types";

// Generate a random date within the past n days
const getRandomDate = (days: number): Date => {
  const date = new Date();
  date.setDate(date.getDate() - Math.floor(Math.random() * days));
  date.setHours(
    Math.floor(Math.random() * 24),
    Math.floor(Math.random() * 60),
    Math.floor(Math.random() * 60)
  );
  return date;
};

// Generate random GitHub activity
const generateGitHubActivity = (userId: string, teamId: string, timestamp: Date): GitHubActivity => {
  const categories: ActivityCategory[] = ['code', 'review'];
  const repos = ['frontend', 'backend', 'api', 'mobile', 'docs'];
  const branches = ['main', 'develop', 'feature/auth', 'feature/dashboard', 'bugfix/login'];
  const actions = ['opened', 'updated', 'merged', 'resolved', 'fixed'];
  
  const isCommit = Math.random() > 0.4;
  const category = isCommit ? 'code' : 'review';
  const repo = repos[Math.floor(Math.random() * repos.length)];
  const branch = branches[Math.floor(Math.random() * branches.length)];
  const action = actions[Math.floor(Math.random() * actions.length)];
  
  if (isCommit) {
    return {
      id: `gh-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
      userId,
      teamId,
      source: 'github',
      category,
      title: `${action} commit to ${repo}`,
      description: `${action} commit to ${branch} in ${repo}`,
      timestamp,
      metadata: {
        repo,
        branch,
        commitId: Math.random().toString(36).substring(2, 12),
        commitCount: Math.floor(Math.random() * 5) + 1
      }
    };
  } else {
    return {
      id: `gh-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
      userId,
      teamId,
      source: 'github',
      category,
      title: `PR #${Math.floor(Math.random() * 100)} in ${repo}`,
      description: `${action} pull request in ${repo}`,
      timestamp,
      metadata: {
        repo,
        prNumber: Math.floor(Math.random() * 100),
        prTitle: `${action} feature in ${repo}`,
        prStatus: Math.random() > 0.3 ? 'merged' : 'open'
      }
    };
  }
};

// Generate random Slack activity
const generateSlackActivity = (userId: string, teamId: string, timestamp: Date): SlackActivity => {
  const channels = ['general', 'development', 'random', 'bugs', 'feature-requests'];
  const messageTypes = ['message', 'thread', 'reaction'];
  
  const channel = channels[Math.floor(Math.random() * channels.length)];
  const messageType = messageTypes[Math.floor(Math.random() * messageTypes.length)];
  
  const isBlocker = Math.random() > 0.8;
  const category: ActivityCategory = isBlocker ? 'blocker' : 'chat';
  
  return {
    id: `slack-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
    userId,
    teamId,
    source: 'slack',
    category,
    title: isBlocker ? `Blocker reported in #${channel}` : `Message in #${channel}`,
    description: isBlocker ? `Reported a blocker: "${Math.random().toString(36).substring(2, 10)}"` : undefined,
    timestamp,
    metadata: {
      channel,
      messageType,
      reactionCount: Math.floor(Math.random() * 5),
      threadSize: messageType === 'thread' ? Math.floor(Math.random() * 8) + 1 : 0
    }
  };
};

// Generate mock activities for a team
export const generateMockActivities = (team: Team): Activity[] => {
  if (!team || !team.members || team.members.length === 0) {
    return [];
  }
  
  const activities: Activity[] = [];
  const activityCount = Math.floor(Math.random() * 50) + 50; // 50-100 activities
  
  for (let i = 0; i < activityCount; i++) {
    const member = team.members[Math.floor(Math.random() * team.members.length)];
    const isGitHub = Math.random() > 0.4;
    const timestamp = getRandomDate(14); // Past 2 weeks
    
    if (isGitHub) {
      activities.push(generateGitHubActivity(member.userId, team.id, timestamp));
    } else {
      activities.push(generateSlackActivity(member.userId, team.id, timestamp));
    }
  }
  
  // Sort activities by timestamp, newest first
  return activities.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
};

// Format date as YYYY-MM-DD
const formatDate = (date: Date): string => {
  return date.toISOString().split('T')[0];
};

// Get dates for the last n days
const getDatesForLastDays = (days: number): string[] => {
  const dates: string[] = [];
  const today = new Date();
  
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date();
    date.setDate(today.getDate() - i);
    dates.push(formatDate(date));
  }
  
  return dates;
};

// Generate aggregated metrics from activities
export const generateTeamMetrics = (activities: Activity[], team: Team): TeamMetrics => {
  const days = 14; // Show metrics for past 14 days
  const dates = getDatesForLastDays(days);
  
  // Initialize metric arrays with zeros for all dates
  const emptyMetrics = dates.map(date => ({ date, value: 0 }));
  
  const dailyCommits: MetricData[] = [...emptyMetrics];
  const dailyPRs: MetricData[] = [...emptyMetrics];
  const dailyMessages: MetricData[] = [...emptyMetrics];
  const dailyBlockers: MetricData[] = [...emptyMetrics];
  
  // Initialize per-member activity tracking
  const memberActivity: Record<string, MetricData[]> = {};
  team.members.forEach(member => {
    memberActivity[member.userId] = [...emptyMetrics];
  });
  
  // Process activities
  activities.forEach(activity => {
    const date = formatDate(new Date(activity.timestamp));
    const dateIndex = dates.indexOf(date);
    
    if (dateIndex !== -1) {
      // Update overall metrics
      if (activity.source === 'github' && activity.category === 'code') {
        dailyCommits[dateIndex].value += 1;
      } else if (activity.source === 'github' && activity.category === 'review') {
        dailyPRs[dateIndex].value += 1;
      } else if (activity.source === 'slack' && activity.category === 'chat') {
        dailyMessages[dateIndex].value += 1;
      } else if (activity.category === 'blocker') {
        dailyBlockers[dateIndex].value += 1;
      }
      
      // Update individual metrics
      if (memberActivity[activity.userId]?.[dateIndex]) {
        memberActivity[activity.userId][dateIndex].value += 1;
      }
    }
  });
  
  // Format member activity for the return value
  const memberMetrics = team.members.map(member => ({
    memberId: member.userId,
    memberName: member.name,
    activity: memberActivity[member.userId] || [...emptyMetrics]
  }));
  
  return {
    dailyCommits,
    dailyPRs,
    dailyMessages,
    dailyBlockers,
    memberActivity: memberMetrics
  };
};
