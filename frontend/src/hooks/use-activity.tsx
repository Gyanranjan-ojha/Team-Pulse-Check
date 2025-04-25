
import React, { createContext, useContext, useState, useEffect } from 'react';
import { Activity, TeamMetrics, MetricData } from '../types';
import { useTeam } from './use-team';
import { generateMockActivities, generateTeamMetrics } from '../lib/mock-data';

interface ActivityContextType {
  activities: Activity[];
  metrics: TeamMetrics | null;
  loading: boolean;
  refreshActivities: () => Promise<void>;
  addActivity: (activity: Partial<Activity>) => Promise<Activity>;
}

const ActivityContext = createContext<ActivityContextType | undefined>(undefined);

export const ActivityProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { team } = useTeam();
  const [activities, setActivities] = useState<Activity[]>([]);
  const [metrics, setMetrics] = useState<TeamMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  // Load activities when team changes
  useEffect(() => {
    const loadActivities = async () => {
      if (!team) {
        setActivities([]);
        setMetrics(null);
        setLoading(false);
        return;
      }

      setLoading(true);
      try {
        // In a real app, this would be an API call
        // For demo, we generate mock activities
        const mockActivities = generateMockActivities(team);
        setActivities(mockActivities);
        
        // Generate aggregated metrics from activities
        const teamMetrics = generateTeamMetrics(mockActivities, team);
        setMetrics(teamMetrics);
      } catch (error) {
        console.error("Failed to load activities:", error);
      } finally {
        setLoading(false);
      }
    };

    loadActivities();
  }, [team]);

  const refreshActivities = async () => {
    if (!team) return;
    
    setLoading(true);
    try {
      // In a real app, this would refresh from API
      const mockActivities = generateMockActivities(team);
      setActivities(mockActivities);
      
      const teamMetrics = generateTeamMetrics(mockActivities, team);
      setMetrics(teamMetrics);
    } catch (error) {
      console.error("Failed to refresh activities:", error);
    } finally {
      setLoading(false);
    }
  };

  const addActivity = async (activityData: Partial<Activity>): Promise<Activity> => {
    if (!team) throw new Error("Must be in a team to add activities");
    
    try {
      // In a real app, this would be an API call
      const newActivity: Activity = {
        id: `activity-${Date.now()}`,
        teamId: team.id,
        timestamp: new Date(),
        ...activityData
      } as Activity;
      
      setActivities(prev => [newActivity, ...prev]);
      
      // Update metrics (simplified for demo)
      // In real app would recalculate or incrementally update
      
      return newActivity;
    } catch (error) {
      console.error("Failed to add activity:", error);
      throw error;
    }
  };

  return (
    <ActivityContext.Provider
      value={{
        activities,
        metrics,
        loading,
        refreshActivities,
        addActivity
      }}
    >
      {children}
    </ActivityContext.Provider>
  );
};

export const useActivity = () => {
  const context = useContext(ActivityContext);
  if (context === undefined) {
    throw new Error("useActivity must be used within an ActivityProvider");
  }
  return context;
};
