
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Generate a random team invite code
export function generateTeamInviteCode(): string {
  const characters = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  let result = '';
  for (let i = 0; i < 6; i++) {
    result += characters.charAt(Math.floor(Math.random() * characters.length));
  }
  return result;
}

// Format date relative to current time
export function formatRelativeTime(date: Date): string {
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  
  if (diffInSeconds < 60) {
    return `${diffInSeconds} seconds ago`;
  }
  
  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) {
    return `${diffInMinutes} minute${diffInMinutes === 1 ? '' : 's'} ago`;
  }
  
  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) {
    return `${diffInHours} hour${diffInHours === 1 ? '' : 's'} ago`;
  }
  
  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 30) {
    return `${diffInDays} day${diffInDays === 1 ? '' : 's'} ago`;
  }
  
  const diffInMonths = Math.floor(diffInDays / 30);
  return `${diffInMonths} month${diffInMonths === 1 ? '' : 's'} ago`;
}

// Format number with abbreviations (1K, 1M, etc.)
export function formatNumber(num: number): string {
  if (num < 1000) {
    return num.toString();
  }
  if (num < 1000000) {
    return (num / 1000).toFixed(1) + 'K';
  }
  return (num / 1000000).toFixed(1) + 'M';
}

// Group activities by date
export function groupActivitiesByDate(activities: any[]): Record<string, any[]> {
  return activities.reduce((groups, activity) => {
    const date = new Date(activity.timestamp).toLocaleDateString();
    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(activity);
    return groups;
  }, {} as Record<string, any[]>);
}

// Get activity icon based on category and source
export function getActivityColor(category: string, source: string): string {
  if (category === 'code') return 'text-green-500';
  if (category === 'review') return 'text-blue-500';
  if (category === 'chat') return 'text-purple-500';
  if (category === 'blocker') return 'text-red-500';
  return 'text-gray-500';
}

// Generate colors for team members (for charts)
export function getMemberColor(index: number): string {
  const colors = [
    '#9b87f5', '#7E69AB', '#6E59A5', '#5149ab', '#4338ca', 
    '#4f46e5', '#6366f1', '#818cf8', '#a5b4fc', '#c7d2fe'
  ];
  return colors[index % colors.length];
}
