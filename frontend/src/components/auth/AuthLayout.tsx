
import React from "react";
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../../hooks/use-auth";

const AuthLayout: React.FC = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse text-xl text-pulse-primary">Loading...</div>
      </div>
    );
  }

  if (user) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="min-h-screen bg-background flex">
      <div className="flex-1 flex flex-col justify-center px-4 sm:px-6 lg:flex-none lg:px-20 xl:px-24">
        <div className="mx-auto w-full max-w-sm lg:w-96">
          <Outlet />
        </div>
      </div>
      <div className="hidden lg:block relative flex-1 bg-gradient-to-br from-pulse-primary to-pulse-tertiary">
        <div className="absolute inset-0 flex flex-col items-center justify-center text-white">
          <div className="text-5xl font-bold mb-4">PulseCheck</div>
          <p className="text-xl max-w-md text-center">
            Monitor your team's collaborative energy and spot early signals of burnout or disengagement.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;
