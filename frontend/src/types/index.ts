
// User types
export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  teamId?: string;
  role: 'member' | 'admin';
  createdAt: Date;
}

// Team types
export interface Team {
  id: string;
  name: string;
  inviteCode: string;
  createdById: string;
  createdAt: Date;
  members: TeamMember[];
}

export interface TeamMember {
  id: string;
  userId: string;
  teamId: string;
  name: string;
  role: 'member' | 'admin';
  avatar?: string;
  joinedAt: Date;
}

// Activity types
export type ActivitySource = 'github' | 'slack' | 'manual';
export type ActivityCategory = 'code' | 'chat' | 'review' | 'blocker';

export interface Activity {
  id: string;
  userId: string;
  teamId: string;
  source: ActivitySource;
  category: ActivityCategory;
  title: string;
  description?: string;
  timestamp: Date;
  metadata?: Record<string, any>;
}

export interface GitHubActivity extends Activity {
  source: 'github';
  metadata: {
    repo?: string;
    branch?: string;
    commitId?: string;
    prNumber?: number;
    prTitle?: string;
    prStatus?: 'open' | 'merged' | 'closed';
    commitCount?: number;
  };
}

export interface SlackActivity extends Activity {
  source: 'slack';
  metadata: {
    channel?: string;
    messageType?: 'message' | 'thread' | 'reaction';
    reactionCount?: number;
    threadSize?: number;
  };
}

export interface MetricData {
  date: string;
  value: number;
}

export interface TeamMetrics {
  dailyCommits: MetricData[];
  dailyPRs: MetricData[];
  dailyMessages: MetricData[];
  dailyBlockers: MetricData[];
  memberActivity: {
    memberId: string;
    memberName: string;
    activity: MetricData[];
  }[];
}
