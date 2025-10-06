import { useState } from "react";
import { Button } from "./ui/button";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "./ui/dropdown-menu";
import { Download, FileText, FileSpreadsheet } from "lucide-react";
import type { AIOutput } from "../App";
import React from "react";


interface ExportButtonProps {
  outputs: AIOutput[];
}

export function ExportButton({ outputs }: ExportButtonProps) {
  const [isExporting, setIsExporting] = useState(false);

  const downloadFile = (content: string, filename: string, mimeType: string) => {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const exportToCSV = async () => {
    setIsExporting(true);
    
    try {
      const headers = [
        'ID',
        'Category', 
        'Confidence',
        'Text',
        'Timestamp',
        'User Feedback',
        'Reference Count',
        'Comparison Summary'
      ];

      const rows = outputs.map(output => [
        output.id,
        output.category,
        output.confidence.toString(),
        `"${output.text.replace(/"/g, '""')}"`, // Escape quotes in CSV
        output.timestamp,
        output.userFeedback || '',
        output.references.length.toString(),
        `"${output.comparisonSummary.replace(/"/g, '""')}"`
      ]);

      const csvContent = [
        headers.join(','),
        ...rows.map(row => row.join(','))
      ].join('\n');

      const timestamp = new Date().toISOString().split('T')[0];
      downloadFile(csvContent, `ai-confidence-data-${timestamp}.csv`, 'text/csv');
    } finally {
      setIsExporting(false);
    }
  };

  const exportToJSON = async () => {
    setIsExporting(true);
    
    try {
      const exportData = {
        exportDate: new Date().toISOString(),
        totalOutputs: outputs.length,
        outputs: outputs.map(output => ({
          id: output.id,
          category: output.category,
          confidence: output.confidence,
          text: output.text,
          timestamp: output.timestamp,
          userFeedback: output.userFeedback,
          references: output.references.map(ref => ({
            id: ref.id,
            title: ref.title,
            url: ref.url,
            description: ref.description,
            userRating: ref.userRating
          })),
          comparisonSummary: output.comparisonSummary
        }))
      };

      const jsonContent = JSON.stringify(exportData, null, 2);
      const timestamp = new Date().toISOString().split('T')[0];
      downloadFile(jsonContent, `ai-confidence-data-${timestamp}.json`, 'application/json');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button 
          type="button"
          aria-label="Export data"
          variant="outline" 
          className="gap-2 border-accent text-accent hover:bg-accent hover:text-accent-foreground" 
          disabled={isExporting || outputs.length === 0}
        >
          <Download className="h-4 w-4" aria-hidden="true"/>
          Export Data
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={exportToCSV} disabled={isExporting}>
          <FileSpreadsheet className="h-4 w-4 mr-2" />
          Export as CSV
        </DropdownMenuItem>
        <DropdownMenuItem onClick={exportToJSON} disabled={isExporting}>
          <FileText className="h-4 w-4 mr-2" />
          Export as JSON
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}