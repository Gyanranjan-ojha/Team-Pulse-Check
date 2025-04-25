
import React from "react";
import { NavLink } from "react-router-dom";
import { useTeam } from "../../hooks/use-team";
import { cn } from "@/lib/utils";
import { 
  BarChart2, 
  Users, 
  Calendar, 
  GitPullRequest, 
  MessageSquare, 
  Settings, 
  Activity
} from "lucide-react";

const Sidebar: React.FC = () => {
  const { team } = useTeam();
  
  if (!team) {
    return null;
  }

  const navItems = [
    { name: "Dashboard", path: "/", icon: <BarChart2 className="h-5 w-5" /> },
    { name: "Team", path: "/team", icon: <Users className="h-5 w-5" /> },
    { name: "Activity", path: "/activity", icon: <Activity className="h-5 w-5" /> },
    { name: "Code", path: "/code", icon: <GitPullRequest className="h-5 w-5" /> },
    { name: "Communication", path: "/communication", icon: <MessageSquare className="h-5 w-5" /> },
    { name: "Calendar", path: "/calendar", icon: <Calendar className="h-5 w-5" /> },
    { name: "Settings", path: "/settings", icon: <Settings className="h-5 w-5" /> },
  ];

  return (
    <aside className="bg-sidebar h-screen w-64 border-r flex-shrink-0 hidden md:flex flex-col">
      <div className="p-4 border-b">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-md bg-gradient-to-br from-pulse-primary to-pulse-secondary flex items-center justify-center">
            <span className="text-white font-semibold">PC</span>
          </div>
          <span className="font-bold text-lg">PulseCheck</span>
        </div>
      </div>
      <nav className="flex-1 overflow-y-auto p-2">
        <ul className="space-y-1">
          {navItems.map((item) => (
            <li key={item.name}>
              <NavLink
                to={item.path}
                className={({ isActive }) => cn(
                  "flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors",
                  isActive
                    ? "bg-sidebar-accent text-sidebar-accent-foreground font-medium"
                    : "text-sidebar-foreground hover:bg-sidebar-accent/50"
                )}
              >
                {item.icon}
                {item.name}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
      <div className="p-4 border-t">
        <div className="text-sm text-sidebar-foreground/70">
          <div className="font-medium">{team.name}</div>
          <div className="text-xs">{team.members.length} team members</div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
