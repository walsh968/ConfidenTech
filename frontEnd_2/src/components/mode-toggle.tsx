import { Button } from "./ui/button";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "./ui/dropdown-menu";
import { Settings, GraduationCap, AlertTriangle } from "lucide-react";
import type { ViewMode } from "../App";
import React from "react";


interface ModeToggleProps {
  viewMode: ViewMode;
  onModeChange: (mode: ViewMode) => void;
}

export function ModeToggle({ viewMode, onModeChange }: ModeToggleProps) {
  const getModeIcon = () => {
    return viewMode === "educational" ? <GraduationCap className="h-4 w-4" /> : <AlertTriangle className="h-4 w-4" />;
  };

  const getModeLabel = () => {
    return viewMode === "educational" ? "Educational" : "Critical";
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button 
          variant="outline" 
          className="gap-2 border-primary text-primary hover:bg-primary hover:text-primary-foreground"
        >
          {getModeIcon()}
          {getModeLabel()} Mode
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem 
          onClick={() => onModeChange("educational")}
          className="gap-2"
        >
          <GraduationCap className="h-4 w-4" />
          <div className="flex flex-col items-start">
            <span>Educational Mode</span>
            <span className="text-xs text-muted-foreground">
              Simplified view for learning
            </span>
          </div>
        </DropdownMenuItem>
        <DropdownMenuItem 
          onClick={() => onModeChange("critical")}
          className="gap-2"
        >
          <AlertTriangle className="h-4 w-4" />
          <div className="flex flex-col items-start">
            <span>Critical Mode</span>
            <span className="text-xs text-muted-foreground">
              Detailed metrics for experts
            </span>
          </div>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}