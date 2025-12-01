import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Separator } from "./ui/separator";
import { ThumbsUp, ThumbsDown, ExternalLink } from "lucide-react";
import { cn } from "./ui/utils";
import { HighlightedText } from "./highlighted-text";
import React from "react";
import { Explanation } from "../App";


interface Reference {
  id: string;
  title: string;
  url: string;
  description: string;
  userRating: "up" | "down" | null;
}

interface ReferenceSectionProps {
  references: Reference[];
  explanation: Explanation | null | undefined;
  comparisonSummary: string;
  onReferenceRating: (referenceId: string, rating: "up" | "down" | null) => void;
  answerText?: string; // The AI answer text to display in Evidence Analysis
  sentenceAlignment?: {
    aligned: number[];
    conflicting: number[];
    sentences?: string[];
  };
}

export function ReferenceSection({ 
  references, 
  explanation,
  comparisonSummary, 
  onReferenceRating,
  answerText,
  sentenceAlignment
}: ReferenceSectionProps) {
  const handleRatingClick = (referenceId: string, rating: "up" | "down") => {
    // Toggle rating if same rating is clicked, otherwise set new rating
    const currentRef = references.find(ref => ref.id === referenceId);
    const newRating = currentRef?.userRating === rating ? null : rating;
    onReferenceRating(referenceId, newRating);
  };

  return (
    <div className="space-y-4">
      <h4>References & Sources</h4>
      
      {/* Reference Links */}
      <div className="grid gap-3">
        {references.map((reference) => (
          <Card key={reference.id} className="bg-muted/50 border-border/50">
            <CardContent className="p-4">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 space-y-2">
                  <div className="flex items-center gap-2">
                    <a 
                      href={reference.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-medium text-primary hover:text-accent hover:underline flex items-center gap-1 transition-colors"
                    >
                      {reference.title}
                      <ExternalLink className="h-3 w-3 text-accent" />
                    </a>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {reference.description}
                  </p>
                </div>
                
                {/* Reference Rating Buttons */}
                <div className="flex gap-1" aria-label="Rate this reference">
                  <Button
                    type="button"
                    aria-label="Upvote reference"
                    variant="ghost"
                    size="sm"
                    className={cn(
                      "h-8 w-8 p-0 hover:bg-accent/10 hover:text-accent",
                      reference.userRating === "up" && "bg-green-100 text-green-700 hover:bg-green-200 hover:text-green-800"
                    )}
                    onClick={() => handleRatingClick(reference.id, "up")}
                  >
                    <ThumbsUp className="h-3 w-3" aria-hidden="true"/>
                  </Button>
                  <Button
                    type="button"
                    aria-label="Downvote reference"
                    variant="ghost"
                    size="sm"
                    className={cn(
                      "h-8 w-8 p-0 hover:bg-accent/10 hover:text-accent",
                      reference.userRating === "down" && "bg-red-100 text-red-700 hover:bg-red-200 hover:text-red-800"
                    )}
                    onClick={() => handleRatingClick(reference.id, "down")}
                  >
                    <ThumbsDown className="h-3 w-3" aria-hidden="true"/>
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Separator />

      {/* Evidence Analysis - Show AI answer with highlighting */}
      <div>
        <h5 className="mb-2 text-primary">Evidence Analysis</h5>
        <Card className="bg-primary/5 border-primary/20">
          <CardContent className="p-4">
            {answerText && sentenceAlignment ? (
              <HighlightedText
                text={answerText}
                alignedIndices={sentenceAlignment.aligned}
                conflictingIndices={sentenceAlignment.conflicting}
                sentences={sentenceAlignment.sentences}
                className="text-sm text-foreground"
              />
            ) : (
              <p className="text-sm leading-relaxed text-foreground">
                {comparisonSummary}
              </p>
            )}
            <div className="mt-3 pt-3 border-t border-primary/10">
              <p className="text-xs font-medium text-muted-foreground mb-2">Color Coding:</p>
              <div className="flex flex-col gap-1.5 text-xs">
                <div className="flex items-center gap-2">
                  <span className="bg-green-100 text-green-900 px-2 py-0.5 rounded inline-block">Aligned</span>
                  <span className="text-muted-foreground">Sentences supported by sources</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="bg-red-100 text-red-900 px-2 py-0.5 rounded inline-block">Conflicting</span>
                  <span className="text-muted-foreground">Sentences that contradict sources</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-primary/5 border-primary/20 mt-4">
          <CardContent className="p-4">                        
            <div className="mt-3 pt-3 border-primary/10">
              <p className="text-sm border-b font-medium text-muted-foreground mb-2">Explanation:</p>
              <div className="text-sm leading-relaxed text-foreground">
                <p>{explanation?.reason || "No explanation available."}</p>            
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}