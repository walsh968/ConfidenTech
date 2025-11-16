import React from "react";
import { LogOut, Settings, HelpCircle, Sparkles } from "lucide-react";
import { HoverCard, HoverCardContent, HoverCardTrigger } from "./ui/hover-card";
import { Avatar, AvatarFallback } from "./ui/avatar";
import { Button } from "./ui/button";
import { Separator } from "./ui/separator";
import { User } from "../services/api";

interface ProfileMenuProps {
  user: User | null;
  onLogout: () => void;
}

export function ProfileMenu({ user, onLogout }: ProfileMenuProps) {
  const getInitials = () => {
    if (!user) return "U";
    const first = user.first_name?.[0] || "";
    const last = user.last_name?.[0] || "";
    if (first && last) return `${first}${last}`.toUpperCase();
    if (first) return first.toUpperCase();
    if (user.email) return user.email[0].toUpperCase();
    return "U";
  };

  const getUserName = () => {
    if (!user) return "User";
    if (user.first_name && user.last_name) {
      return `${user.first_name} ${user.last_name}`;
    }
    if (user.first_name) return user.first_name;
    return user.email || "User";
  };

  return (
    <HoverCard>
      <HoverCardTrigger asChild>
        <button
          className="flex items-center justify-center w-10 h-10 transition-colors cursor-pointer shadow-sm p-0 border-0 bg-transparent hover:bg-transparent"
          aria-label="Profile menu"
        >
          <Avatar className="w-10 h-10 hover:opacity-90 transition-opacity" style={{ border: '2px solid #9ca3af', borderRadius: '50%', aspectRatio: '1/1' }}>
            <AvatarFallback className="bg-blue-100/70 hover:bg-blue-200/80 text-blue-600 text-sm font-medium transition-colors" style={{ borderRadius: '50%', width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {getInitials()}
            </AvatarFallback>
          </Avatar>
        </button>
      </HoverCardTrigger>
      <HoverCardContent className="w-64 p-0" align="end">
        <div className="p-4 border-b">
          <div className="flex items-center gap-3">
            <Avatar className="w-12 h-12">
              <AvatarFallback className="bg-primary/10 text-primary text-lg font-medium">
                {getInitials()}
              </AvatarFallback>
            </Avatar>
            <div className="flex flex-col">
              <p className="text-sm font-medium">{getUserName()}</p>
              <p className="text-xs text-muted-foreground">{user?.email}</p>
            </div>
          </div>
        </div>
        <div className="p-2 space-y-1">
          <Button
            variant="ghost"
            className="w-full justify-start gap-2 text-sm"
            onClick={() => {
              // TODO: Implement upgrade plan functionality
              console.log("Upgrade Plan clicked");
            }}
          >
            <Sparkles className="h-4 w-4" />
            Upgrade Plan
          </Button>
          <Button
            variant="ghost"
            className="w-full justify-start gap-2 text-sm"
            onClick={() => {
              // TODO: Implement settings functionality
              console.log("Settings clicked");
            }}
          >
            <Settings className="h-4 w-4" />
            Settings
          </Button>
          <Button
            variant="ghost"
            className="w-full justify-start gap-2 text-sm"
            onClick={() => {
              // TODO: Implement help functionality
              console.log("Help clicked");
            }}
          >
            <HelpCircle className="h-4 w-4" />
            Help
          </Button>
          <Separator className="my-1" />
          <Button
            variant="ghost"
            className="w-full justify-start gap-2 text-sm text-destructive hover:text-destructive"
            onClick={onLogout}
          >
            <LogOut className="h-4 w-4" />
            Logout
          </Button>
        </div>
      </HoverCardContent>
    </HoverCard>
  );
}

