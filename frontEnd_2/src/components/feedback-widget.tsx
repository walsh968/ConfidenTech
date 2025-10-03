import { Button } from "./ui/button";
import { ThumbsUp, ThumbsDown } from "lucide-react";
import { cn } from "./ui/utils";
import React from "react";


interface FeedbackWidgetProps {
  feedback: "agree" | "disagree" | null;
  onFeedbackChange: (feedback: "agree" | "disagree" | null) => void;
}

export function FeedbackWidget({ feedback, onFeedbackChange }: FeedbackWidgetProps) {
  const handleFeedbackClick = (newFeedback: "agree" | "disagree") => {
    // Toggle feedback if same feedback is clicked, otherwise set new feedback
    const updatedFeedback = feedback === newFeedback ? null : newFeedback;
    onFeedbackChange(updatedFeedback);
  };

  return (
    <div className="flex items-center gap-2">
      <span className="text-sm text-muted-foreground">Rate confidence:</span>
      <div className="flex gap-1">
        <Button
          variant="ghost"
          size="sm"
          className={cn(
            "gap-1 hover:bg-accent/10 hover:text-accent",
            feedback === "agree" && "bg-green-100 text-green-700 hover:bg-green-200 hover:text-green-800"
          )}
          onClick={() => handleFeedbackClick("agree")}
        >
          <ThumbsUp className="h-4 w-4" />
          Agree
        </Button>
        <Button
          variant="ghost"
          size="sm"
          className={cn(
            "gap-1 hover:bg-accent/10 hover:text-accent",
            feedback === "disagree" && "bg-red-100 text-red-700 hover:bg-red-200 hover:text-red-800"
          )}
          onClick={() => handleFeedbackClick("disagree")}
        >
          <ThumbsDown className="h-4 w-4" />
          Disagree
        </Button>
      </div>
    </div>
  );
}