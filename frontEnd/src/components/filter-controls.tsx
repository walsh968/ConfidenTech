import { Label } from "./ui/label";
import { Slider } from "./ui/slider";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import React from "react";

type SortOrder = "oldest-to-recent" | "high-to-low" | "low-to-high";

interface FilterControlsProps {
  confidenceThreshold: number;
  onThresholdChange: (threshold: number) => void;
  sortOrder: SortOrder;
  onSortOrderChange: (order: SortOrder) => void;
}

export function FilterControls({ 
  confidenceThreshold, 
  onThresholdChange, 
  sortOrder, 
  onSortOrderChange 
}: FilterControlsProps) {

  const sliderId = "confidence-threshold";
  return (
    <div className="flex flex-col sm:flex-row gap-6 items-start sm:items-end">
      {/* Minimum Confidence */}
      <div className="space-y-2 min-w-48">
        <Label className="text-sm text-primary" htmlFor={sliderId}>
          Minimum Confidence: <span className="text-accent font-medium">{confidenceThreshold}%</span>
        </Label>
        <Slider
          id={sliderId}
          aria-label="Confidence threshold"
          aria-valuemin={0}
          aria-valuemax={100}
          value={[confidenceThreshold]}
          onValueChange={(value: number[]) => onThresholdChange(value[0])}
          max={100}
          min={0}
          step={5}
          className="w-full"
        />
      </div>

      {/* Sort */}
      <div className="space-y-2 min-w-40">
        <Label className="text-sm text-primary">Sort</Label>
        <Select value={sortOrder} onValueChange={(v) => onSortOrderChange(v as SortOrder)}>
          <SelectTrigger className="border-primary/20 focus:border-primary" aria-label="Sort order">
            <SelectValue placeholder="Sort by"/>
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="oldest-to-recent">Oldest to Recent</SelectItem>
            <SelectItem value="high-to-low">High to Low</SelectItem>
            <SelectItem value="low-to-high">Low to High</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}
