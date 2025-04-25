
import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TeamMetrics } from "../../types";
import { getMemberColor } from "../../lib/utils";

interface TeamActivityChartProps {
  metrics: TeamMetrics;
}

const TeamActivityChart: React.FC<TeamActivityChartProps> = ({ metrics }) => {
  // Format date for display
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.getDate();
  };

  // Prepare chart data
  const prepareData = () => {
    const result: any[] = [];
    
    // Only use last 7 days for cleaner chart
    const dates = metrics.dailyCommits.slice(-7).map(item => item.date);
    
    dates.forEach((date, index) => {
      const dataPoint: any = { date };
      
      // Add member data
      metrics.memberActivity.forEach(member => {
        const activityForDate = member.activity.find(a => a.date === date);
        if (activityForDate) {
          dataPoint[member.memberName] = activityForDate.value;
        } else {
          dataPoint[member.memberName] = 0;
        }
      });
      
      result.push(dataPoint);
    });
    
    return result;
  };

  const chartData = prepareData();

  return (
    <Card className="col-span-2 h-[400px]">
      <CardHeader>
        <CardTitle className="text-lg">Team Activity Distribution</CardTitle>
      </CardHeader>
      <CardContent className="h-[324px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{
              top: 5,
              right: 30,
              left: 20,
              bottom: 5,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
            <XAxis
              dataKey="date"
              tickFormatter={formatDate}
              stroke="#888888"
              fontSize={12}
            />
            <YAxis stroke="#888888" fontSize={12} />
            <Tooltip 
              contentStyle={{ background: "#fff", borderRadius: "6px", border: "none" }}
              labelFormatter={(date) => {
                return new Date(date).toLocaleDateString();
              }}
            />
            <Legend />
            {metrics.memberActivity.map((member, index) => (
              <Line
                key={member.memberId}
                type="monotone"
                dataKey={member.memberName}
                stroke={getMemberColor(index)}
                activeDot={{ r: 8 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

export default TeamActivityChart;
