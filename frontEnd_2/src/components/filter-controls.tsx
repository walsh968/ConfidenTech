import { Label } from "./ui/label";
import { Slider } from "./ui/slider";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import React from "react";


interface FilterControlsProps {
  confidenceThreshold: number;
  onThresholdChange: (threshold: number) => void;
  sortOrder: "high-to-low" | "low-to-high";
  onSortOrderChange: (order: "high-to-low" | "low-to-high") => void;
}

export function FilterControls({ 
  confidenceThreshold, 
  onThresholdChange, 
  sortOrder, 
  onSortOrderChange 
}: FilterControlsProps) {
  return (
    <div className="flex flex-col sm:flex-row gap-6 items-start sm:items-end">
      {/* Confidence Threshold Filter */}
      <div className="space-y-2 min-w-48">
        <Label className="text-sm text-primary">
          Minimum Confidence: <span className="text-accent font-medium">{confidenceThreshold}%</span>
        </Label>
        <Slider
          value={[confidenceThreshold]}
          onValueChange={(value) => onThresholdChange(value[0])}
          max={100}
          min={0}
          step={5}
          className="w-full"
        />
      </div>

      {/* Sort Order */}
      <div className="space-y-2 min-w-40">
        <Label className="text-sm text-primary">Sort by Confidence</Label>
        <Select value={sortOrder} onValueChange={onSortOrderChange}>
          <SelectTrigger className="border-primary/20 focus:border-primary">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="high-to-low">High to Low</SelectItem>
            <SelectItem value="low-to-high">Low to High</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}