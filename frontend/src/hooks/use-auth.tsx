
import React, { createContext, useContext, useState, useEffect } from "react";
import { User } from "../types";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, name: string, password: string) => Promise<void>;
  signOut: () => void;
  updateUserTeam: (teamId: string) => void;
}

// Mock user data for demo purposes
const mockUsers: User[] = [
  {
    id: "user-1",
    email: "demo@example.com",
    name: "Demo User",
    role: "admin",
    createdAt: new Date(),
  }
];

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Check for existing session on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const storedUser = localStorage.getItem("pulsecheck_user");
        if (storedUser) {
          setUser(JSON.parse(storedUser));
        }
      } catch (error) {
        console.error("Auth check failed:", error);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const signIn = async (email: string, password: string) => {
    setLoading(true);
    try {
      // In a real app, this would be an API call
      const foundUser = mockUsers.find(u => u.email === email);
      if (!foundUser) {
        throw new Error("Invalid credentials");
      }
      
      // Simulate successful login
      setUser(foundUser);
      localStorage.setItem("pulsecheck_user", JSON.stringify(foundUser));
    } catch (error) {
      console.error("Sign in failed:", error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const signUp = async (email: string, name: string, password: string) => {
    setLoading(true);
    try {
      // In a real app, this would be an API call
      const newUser: User = {
        id: `user-${Date.now()}`,
        email,
        name,
        role: "member",
        createdAt: new Date(),
      };
      
      // Simulate successful registration
      setUser(newUser);
      mockUsers.push(newUser);
      localStorage.setItem("pulsecheck_user", JSON.stringify(newUser));
    } catch (error) {
      console.error("Sign up failed:", error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const signOut = () => {
    setUser(null);
    localStorage.removeItem("pulsecheck_user");
  };

  const updateUserTeam = (teamId: string) => {
    if (user) {
      const updatedUser = { ...user, teamId };
      setUser(updatedUser);
      localStorage.setItem("pulsecheck_user", JSON.stringify(updatedUser));
    }
  };

  return (
    <AuthContext.Provider 
      value={{ 
        user, 
        loading, 
        signIn, 
        signUp, 
        signOut,
        updateUserTeam
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
