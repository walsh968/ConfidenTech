import React from "react";
import { useParams, Navigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { Card, CardHeader, CardContent } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Separator } from "./ui/separator";
import { CalendarDays, Mail, User as UserIcon, ShieldCheck } from "lucide-react";
import { useNavigate } from "react-router-dom";


export const UserProfilePage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user, isLoading, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto" />
          <p className="mt-2 text-muted-foreground">Loading profile...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  if (id && id !== String(user.id)) {

    return <Navigate to={`/user/${user.id}`} replace />;
  }

  const formatDate = (value: string | null | undefined) => {
    if (!value) return "N/A";
    const d = new Date(value);
    if (Number.isNaN(d.getTime())) return "N/A";
    return d.toLocaleString("en-US", {
      year: "numeric",
      month: "short",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const demoStats = {
    totalQueries: 24,
    highConfidenceCount: 15,
    lowConfidenceCount: 3,
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <Card className="shadow-sm border">
          <CardHeader className="flex flex-row items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <UserIcon className="h-5 w-5 text-primary" />
                <h1 className="text-2xl font-semibold">
                  {user.full_name || `${user.first_name} ${user.last_name}` || "User Profile"}
                </h1>
              </div>
              <p className="text-sm text-muted-foreground">
                Personalized profile page for{" "}
                <span className="font-medium">{user.email}</span>
              </p>
            </div>

            <div className="flex flex-col items-end gap-2">
              <Badge variant="outline" className="flex items-center gap-1">
                <ShieldCheck className="h-4 w-4 text-green-500" />
                <span>Account Verified: {user.is_verified ? "Yes" : "No"}</span>
              </Badge>
              <Badge variant="secondary">
                User ID: {user.id}
              </Badge>
            </div>
          </CardHeader>

          <CardContent className="space-y-6">
            <section>
              <h2 className="text-sm font-medium text-muted-foreground mb-3">
                Basic Information
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">Full Name</p>
                  <p className="font-medium">
                    {user.full_name ||
                      [user.first_name, user.last_name].filter(Boolean).join(" ") ||
                      "N/A"}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">Email</p>
                  <div className="flex items-center gap-2">
                    <Mail className="h-4 w-4 text-muted-foreground" />
                    <p className="font-medium">{user.email}</p>
                  </div>
                </div>
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">Account Status</p>
                  <p className="font-medium">
                    {user.is_active ? "Active" : "Inactive"}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">Created At</p>
                  <div className="flex items-center gap-2">
                    <CalendarDays className="h-4 w-4 text-muted-foreground" />
                    <p className="font-medium">{formatDate(user.created_at)}</p>
                  </div>
                </div>
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">Last Login</p>
                  <p className="font-medium">{formatDate(user.last_login)}</p>
                </div>
              </div>
            </section>

            <Separator />

            <section>
              <h2 className="text-sm font-medium text-muted-foreground mb-3">
                Your ConfidenTech Usage
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="rounded-lg border bg-card px-3 py-2">
                  <p className="text-xs text-muted-foreground">Total Queries</p>
                  <p className="text-xl font-semibold">{demoStats.totalQueries}</p>
                </div>
              </div>
            </section>

            <Separator />
            <section className="flex flex-wrap gap-3 justify-between items-center">
              <p className="text-xs text-muted-foreground">
               
              </p>
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate("/")}
              >
                Back
              </Button>
            </section>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
