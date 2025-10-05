import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "./ui/tooltip";
import { Badge } from "./ui/badge";
import { CircleDot } from "lucide-react";
import type { ViewMode } from "../App";
import React from "react";

type Confidence = number | "Unknown";

interface ConfidenceIndicatorProps {
  confidence: Confidence;
  viewMode: ViewMode;
  explanation?: string;
}

type Level = "high" | "medium" | "low" | "unknown";

function normalize(confidence: Confidence): {
  level: Level;
  numeric?: number;       
  label: string;          
  dotClass: string;       
  bgClass: string;        
  barClass: string;       
} {
  if (confidence === "Unknown" || confidence === null || confidence === undefined) {
    return {
      level: "unknown",
      label: "Unknown",
      dotClass: "text-gray-500",
      bgClass: "bg-gray-100 border-gray-200",
      barClass: "bg-gray-400",
    };
  }

  const n = Math.min(100, Math.max(0, Number(confidence)));
  const level: Level = n >= 75 ? "high" : n >= 50 ? "medium" : "low";

  const palette =
    level === "high"
      ? { dot: "text-green-500", bg: "bg-green-100 border-green-200", bar: "bg-green-500" }
      : level === "medium"
      ? { dot: "text-yellow-500", bg: "bg-yellow-100 border-yellow-200", bar: "bg-yellow-500" }
      : { dot: "text-red-500", bg: "bg-red-100 border-red-200", bar: "bg-red-500" };

  return {
    level,
    numeric: n,
    label: `${n}%`,
    dotClass: palette.dot,
    bgClass: palette.bg,
    barClass: palette.bar,
  };
}

export function ConfidenceIndicator({ confidence, viewMode, explanation }: ConfidenceIndicatorProps) {
  const info = normalize(confidence);

  if (viewMode === "educational") {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <div className="flex items-center gap-3">
              {/* Traffic Light Icon */}
              <div className={`p-2 rounded-full border ${info.bgClass}`}>
                <CircleDot className={`h-5 w-5 ${info.dotClass}`} />
              </div>

              {/* Confidence Badge */}
              <Badge variant="outline" className="gap-1">
                {info.level === "unknown"
                  ? "Unknown"
                  : info.level === "high"
                  ? "High"
                  : info.level === "medium"
                  ? "Medium"
                  : "Low"}
              </Badge>
            </div>
          </TooltipTrigger>
          <TooltipContent side="left" className="max-w-xs">
            <p>
              {explanation ||
                (info.level === "unknown"
                  ? "Unknown means the backend didn't provide a numeric confidence."
                  : info.level === "high"
                  ? "High confidence: strong supporting signals."
                  : info.level === "medium"
                  ? "Medium confidence: mixed or partial support."
                  : "Low confidence: limited or conflicting support.")}
            </p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  // Critical mode
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div className="flex items-center gap-3 min-w-fit">
            {/* Traffic Light Icon */}
            <div className={`p-1.5 rounded-full border ${info.bgClass}`}>
              <CircleDot className={`h-4 w-4 ${info.dotClass}`} />
            </div>

            {/* Progress + Percentage */}
            <div className="flex items-center gap-2 min-w-24">
              <div className="relative w-16">
                <div className="bg-primary/20 relative h-2 w-full overflow-hidden rounded-full">
                  {info.numeric !== undefined && (
                    <div
                      className={`h-full transition-all ${info.barClass}`}
                      style={{ width: `${info.numeric}%` }}
                    />
                  )}
                </div>
              </div>
              <span className="text-sm font-medium min-w-fit">
                {info.level === "unknown" ? "Unknown" : info.label}
              </span>
            </div>
          </div>
        </TooltipTrigger>
        <TooltipContent side="left" className="max-w-sm">
          <p>
            {explanation ||
              (info.level === "unknown"
                ? "Unknown means the backend didn't provide a numeric confidence."
                : `Confidence: ${info.label}`)}
          </p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
