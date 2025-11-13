import { Card, CardContent, CardHeader } from "./ui/card";
import { Badge } from "./ui/badge";
import { ConfidenceIndicator } from "./confidence-indicator";
import { ReferenceSection } from "./reference-section";
import { FeedbackWidget } from "./feedback-widget";
import { Separator } from "./ui/separator";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "./ui/collapsible";
import { Button } from "./ui/button";
import { ChevronDown, ChevronUp, Clock } from "lucide-react";
import { useState } from "react";
import type { AIOutput, ViewMode } from "../App";
import React from "react";


interface AIOutputCardProps {
  output: AIOutput;
  viewMode: ViewMode;
  onFeedbackChange: (outputId: string, feedback: "agree" | "disagree" | null) => void;
  onReferenceRating: (outputId: string, referenceId: string, rating: "up" | "down" | null) => void;
}

export function AIOutputCard({
  output,
  viewMode,
  onFeedbackChange,
  onReferenceRating,
}: AIOutputCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const question = output.question ?? "Ask a Question?";
  const answer = output.text ?? output.text;

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getConfidenceExplanation = () => {
    if (output.confidence === "Unknown") {
      return "Unknown — The backend did not provide a numeric confidence score for this response.";
    }
    if (viewMode === "educational") {
      if (output.confidence >= 80) {
        return "High confidence - The AI is very certain about this information based on strong evidence.";
      } else if (output.confidence >= 60) {
        return "Medium confidence - The AI has good evidence but there may be some uncertainty.";
      } else {
        return "Low confidence - The AI has limited evidence or the topic is highly uncertain.";
      }
    } else {
      // Critical mode - more detailed stats
      return `Confidence Score: ${output.confidence}% | References: ${output.references.length} | Category: ${output.category} | Last Updated: ${formatTimestamp(output.timestamp)}`;
    }
  };

  const contentId = React.useId();
  return (
    <Card className="w-full shadow-sm border hover:shadow-md transition-shadow">
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="secondary" className="bg-primary/10 text-primary border-primary/20">
                {output.category}
              </Badge>
              <div className="flex items-center gap-1 text-sm text-muted-foreground">
                <Clock className="h-3 w-3 text-accent" />
                {formatTimestamp(output.timestamp)}
              </div>
            </div>
          </div>
          <ConfidenceIndicator 
            confidence={output.confidence} 
            viewMode={viewMode}
            explanation={getConfidenceExplanation()}
          />
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
  <div className="space-y-3 w-full">
    {/* Question */}
    {question && question !== "Ask a Question?" && (
      <div className="flex justify-end w-full">
        <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm max-w-[80%] ml-auto">
          <p className="leading-relaxed font-medium text-right">{question}</p>
        </div>
      </div>
    )}

    {/* Answer */}
    <div>
      <p className="leading-relaxed">{answer}</p>
    </div>

    <div className="flex items-center justify-between">
      <FeedbackWidget
        feedback={output.userFeedback}
        onFeedbackChange={(feedback) => onFeedbackChange(output.id, feedback)}
      />

      <Collapsible open={isExpanded} onOpenChange={setIsExpanded}>
        <CollapsibleTrigger asChild aria-label="Show details" aria-controls={contentId}>
          <Button variant="ghost" size="sm" className="gap-1 hover:bg-accent/10 hover:text-accent">
            {isExpanded ? (
              <>
                <ChevronUp className="h-4 w-4" />
                Hide Details
              </>
            ) : (
              <>
                <ChevronDown className="h-4 w-4" />
                Show References
              </>
            )}
          </Button>
        </CollapsibleTrigger>

        <CollapsibleContent className="mt-4" id={contentId} role="region">
          <Separator className="mb-4" />
          <ReferenceSection
            references={output.references}
            comparisonSummary={output.comparisonSummary}
            onReferenceRating={(referenceId, rating) => onReferenceRating(output.id, referenceId, rating)}
          />
        </CollapsibleContent>
      </Collapsible>
    </div>
  </div>
</CardContent>
    </Card>
  );
}