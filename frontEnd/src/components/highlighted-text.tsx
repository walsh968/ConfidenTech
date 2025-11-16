import React from "react";

interface HighlightedTextProps {
  text: string;
  alignedIndices?: number[];
  conflictingIndices?: number[];
  sentences?: string[];
  className?: string;
}

export function HighlightedText({
  text,
  alignedIndices = [],
  conflictingIndices = [],
  sentences = [],
  className = "",
}: HighlightedTextProps) {
  // Remove markdown bold markers
  const cleanText = text.replace(/\*\*/g, '');
  
  // Helper function to check if a sentence index should be highlighted
  const getHighlightClass = (index: number) => {
    if (alignedIndices.includes(index)) {
      return "bg-green-100 text-green-900 px-1.5 py-0.5 rounded-md font-medium";
    } else if (conflictingIndices.includes(index)) {
      return "bg-red-100 text-red-900 px-1.5 py-0.5 rounded-md font-medium";
    }
    return "";
  };
  
  // Check if we need to handle numbered lists
  const hasNumberedList = /\d+\.\s+/.test(cleanText);
  
  if (hasNumberedList) {
    // Split the text by numbered list items, keeping the delimiters
    const parts = cleanText.split(/(\d+\.\s+)/g);
    
    // Build a mapping from text position to sentence index for highlighting
    const sentenceToIndexMap = new Map<string, number>();
    if (sentences && sentences.length > 0) {
      const cleanSentences = sentences.map(s => s.replace(/\*\*/g, '').trim());
      cleanSentences.forEach((sent, idx) => {
        sentenceToIndexMap.set(sent.toLowerCase(), idx);
      });
    }
    
    return (
      <div className={`space-y-2 ${className}`}>
        {parts.map((part, index) => {
          // Skip empty parts
          if (!part.trim()) return null;
          
          // If this is a numbered marker (like "1. "), combine it with the next part
          if (/^\d+\.\s+$/.test(part)) {
            const nextPart = parts[index + 1] || "";
            // Combine the marker with its content
            const combined = (part + nextPart).trim();
            // Mark the next part as used
            if (index + 1 < parts.length) {
              parts[index + 1] = "";
            }
            
            // Determine if this item should be highlighted
            // Check if any sentence in the combined text matches our aligned/conflicting indices
            let highlightClass = "";
            if (sentences && sentences.length > 0) {
              const cleanSentences = sentences.map(s => s.replace(/\*\*/g, '').trim());
              // Find which sentences are in this combined text
              for (let i = 0; i < cleanSentences.length; i++) {
                if (combined.toLowerCase().includes(cleanSentences[i].toLowerCase()) || 
                    cleanSentences[i].toLowerCase().includes(combined.toLowerCase().substring(0, 50))) {
                  if (alignedIndices.includes(i)) {
                    highlightClass = "bg-green-100 text-green-900 px-1.5 py-0.5 rounded-md font-medium";
                    break;
                  } else if (conflictingIndices.includes(i)) {
                    highlightClass = "bg-red-100 text-red-900 px-1.5 py-0.5 rounded-md font-medium";
                    break;
                  }
                }
              }
            }
            
            return (
              <div key={index} className={`leading-relaxed ${highlightClass}`}>
                {combined}
              </div>
            );
          }
          
          // Regular text (not immediately after a numbered marker)
          // Check if previous part was not a numbered marker
          const prevPart = parts[index - 1];
          if (!prevPart || !/^\d+\.\s+$/.test(prevPart)) {
            // Determine if this part should be highlighted
            let highlightClass = "";
            if (sentences && sentences.length > 0) {
              const cleanSentences = sentences.map(s => s.replace(/\*\*/g, '').trim());
              for (let i = 0; i < cleanSentences.length; i++) {
                if (part.trim().toLowerCase().includes(cleanSentences[i].toLowerCase()) || 
                    cleanSentences[i].toLowerCase().includes(part.trim().toLowerCase().substring(0, 50))) {
                  if (alignedIndices.includes(i)) {
                    highlightClass = "bg-green-100 text-green-900 px-1.5 py-0.5 rounded-md font-medium";
                    break;
                  } else if (conflictingIndices.includes(i)) {
                    highlightClass = "bg-red-100 text-red-900 px-1.5 py-0.5 rounded-md font-medium";
                    break;
                  }
                }
              }
            }
            
            return (
              <div key={index} className={`leading-relaxed ${highlightClass}`}>
                {part.trim()}
              </div>
            );
          }
          return null;
        }).filter(Boolean)}
      </div>
    );
  }
  
  // If we have pre-split sentences from backend, use them (for non-numbered lists)
  if (sentences && sentences.length > 0) {
    // Clean sentences of markdown
    const cleanSentences = sentences.map(s => s.replace(/\*\*/g, '').trim());
    
    // Regular sentence highlighting without numbered lists
    return (
      <p className={`leading-relaxed ${className}`}>
        {cleanSentences.map((sentence, index) => {
          const highlightClass = getHighlightClass(index);
          
          return (
            <span key={index} className={highlightClass || "inline"}>
              {sentence}
              {index < cleanSentences.length - 1 && " "}
            </span>
          );
        })}
      </p>
    );
  }
  
  // Fallback: split by sentences and highlight
  const sentenceRegex = /([^.!?]+[.!?]+)/g;
  const parts = cleanText.match(sentenceRegex) || [cleanText];
  
  return (
    <p className={`leading-relaxed ${className}`}>
      {parts.map((part, index) => {
        const highlightClass = getHighlightClass(index);
        
        return (
          <span key={index} className={highlightClass || "inline"}>
            {part.trim()}
            {index < parts.length - 1 && " "}
          </span>
        );
      })}
    </p>
  );
}

