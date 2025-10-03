import { useState } from "react";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { Label } from "./ui/label";
import { Card, CardContent } from "./ui/card";
import { Loader2, Brain } from "lucide-react";

interface InputAnalysisProps {
  onAnalyze: (text: string) => void;
  isAnalyzing: boolean;
}

export function InputAnalysis({ onAnalyze, isAnalyzing }: InputAnalysisProps) {
  const [inputText, setInputText] = useState("");

  const handleAnalyze = () => {
    if (inputText.trim()) {
      onAnalyze(inputText.trim());
      setInputText(""); // Clear input after analysis
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleAnalyze();
    }
  };

  return (
    <Card className="shadow-sm border">
      <CardContent className="p-6">
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-primary" />
            <Label className="text-primary">AI Output Analysis</Label>
          </div>
          
          <div className="space-y-3">
            <Textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Paste AI output here for analysis… (Ctrl+Enter to analyze)"
              className="min-h-32 resize-none border-primary/20 focus:border-primary"
              disabled={isAnalyzing}
            />
            
            <div className="flex justify-between items-center">
              <p className="text-sm text-muted-foreground">
                Enter AI-generated text to analyze confidence levels and generate reference data
              </p>
              
              <Button
                onClick={handleAnalyze}
                disabled={!inputText.trim() || isAnalyzing}
                className="bg-accent hover:bg-accent/90 text-accent-foreground gap-2"
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Brain className="h-4 w-4" />
                    Analyze
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}