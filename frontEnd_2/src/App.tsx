import { useState, useMemo } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AIOutputCard } from "./components/ai-output-card";
import { FilterControls } from "./components/filter-controls";
import { ExportButton } from "./components/export-button";
import { ModeToggle } from "./components/mode-toggle";
import { InputAnalysis } from "./components/input-analysis";
import { Separator } from "./components/ui/separator";
import { LoginPage } from "./components/LoginPage";
import { RegisterPage } from "./components/RegisterPage";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import React from "react";


// Mock data for AI outputs
const mockAIOutputs: AIOutput[] = [
  {
    id: "1",
    text: "Climate change is primarily caused by human activities, particularly the emission of greenhouse gases from burning fossil fuels. The scientific consensus is overwhelming, with over 97% of climate scientists agreeing on this fact.",
    confidence: 94,
    timestamp: "2024-01-15T10:30:00Z",
    category: "Climate Science",
    references: [
      {
        id: "ref-1",
        title: "IPCC Sixth Assessment Report",
        url: "https://ipcc.ch/assessment-report/ar6/",
        description: "Comprehensive scientific assessment of climate change evidence",
        userRating: null
      },
      {
        id: "ref-2", 
        title: "NASA Climate Evidence",
        url: "https://climate.nasa.gov/evidence/",
        description: "NASA's compilation of climate change evidence and data",
        userRating: "up"
      }
    ],
    comparisonSummary: "All referenced sources strongly align with the AI output, providing consistent evidence for human-caused climate change. The consensus data and scientific assessments support the confidence level.",
    userFeedback: null
  },
  {
    id: "2",
    text: "The stock market will likely experience significant volatility in the next quarter due to geopolitical tensions and inflation concerns. Investors should consider diversifying their portfolios.",
    confidence: 67,
    timestamp: "2024-01-14T15:45:00Z", 
    category: "Financial Analysis",
    references: [
      {
        id: "ref-3",
        title: "Federal Reserve Economic Data",
        url: "https://fred.stlouisfed.org/",
        description: "Latest economic indicators and inflation data",
        userRating: "up"
      },
      {
        id: "ref-4",
        title: "Market Analysis Report",
        url: "https://example.com/market-report",
        description: "Third-party analysis of current market conditions",
        userRating: null
      }
    ],
    comparisonSummary: "Economic data supports concerns about inflation, but market prediction sources show mixed signals. Some indicators suggest stability while others point to volatility, reflecting the moderate confidence score.",
    userFeedback: "disagree"
  },
  {
    id: "3",
    text: "Quantum computing could revolutionize cryptography within the next 5-10 years, potentially breaking current encryption methods. Organizations should start preparing quantum-resistant security measures.",
    confidence: 73,
    timestamp: "2024-01-13T09:20:00Z",
    category: "Technology",
    references: [
      {
        id: "ref-5",
        title: "NIST Post-Quantum Cryptography",
        url: "https://csrc.nist.gov/projects/post-quantum-cryptography",
        description: "Official NIST standards for quantum-resistant cryptography",
        userRating: "up"
      },
      {
        id: "ref-6",
        title: "IBM Quantum Computing Timeline",
        url: "https://research.ibm.com/quantum-computing",
        description: "IBM's roadmap for quantum computing development",
        userRating: null
      }
    ],
    comparisonSummary: "Official standards bodies and major tech companies acknowledge the quantum threat timeline, though exact timing remains uncertain. Sources generally support the 5-10 year timeframe with some variation.",
    userFeedback: "agree"
  },
  {
    id: "4",
    text: "Adding meditation to your daily routine can reduce stress levels by up to 40% according to recent studies. Even 10 minutes per day can make a significant difference in mental well-being.",
    confidence: 86,
    timestamp: "2024-01-12T14:15:00Z",
    category: "Health & Wellness", 
    references: [
      {
        id: "ref-7",
        title: "Mayo Clinic - Meditation Benefits",
        url: "https://mayoclinic.org/meditation",
        description: "Medical evidence for meditation's stress reduction benefits",
        userRating: "up"
      },
      {
        id: "ref-8",
        title: "Harvard Health - Mindfulness Research",
        url: "https://health.harvard.edu/mindfulness",
        description: "Harvard's research on mindfulness and stress reduction",
        userRating: "up"
      }
    ],
    comparisonSummary: "Multiple peer-reviewed studies and medical institutions consistently report stress reduction benefits from meditation. The 40% figure aligns with several research studies, supporting the high confidence level.",
    userFeedback: null
  },
  {
    id: "5",
    text: "The James Webb Space Telescope might discover signs of extraterrestrial life in the next few years by analyzing exoplanet atmospheres for biosignatures like oxygen and methane.",
    confidence: 45,
    timestamp: "2024-01-11T11:30:00Z",
    category: "Space Science",
    references: [
      {
        id: "ref-9",
        title: "NASA JWST Mission Overview",
        url: "https://jwst.nasa.gov/",
        description: "Official NASA documentation of JWST capabilities",
        userRating: null
      },
      {
        id: "ref-10",
        title: "Exoplanet Biosignature Research",
        url: "https://example.com/biosignatures",
        description: "Current research on detecting life through atmospheric analysis",
        userRating: "down"
      }
    ],
    comparisonSummary: "While JWST has the technical capability to detect atmospheric signatures, the likelihood of finding definitive biosignatures remains speculative. Scientific sources emphasize the challenges and uncertainties involved.",
    userFeedback: null
  },
  {
    id: "6",
    text: "This response currently has an unknown confidence from the backend.",
    confidence: "Unknown", 
    timestamp: "2024-01-10T08:00:00Z",
    category: "General Analysis",
    references: [],
    comparisonSummary: "Backend did not provide a numeric confidence score.",
    userFeedback: null,
  },
  
];

type Confidence = number | "Unknown";

export type AIOutput = {
  id: string;
  text: string;
  confidence: Confidence;
  timestamp: string;
  category: string;
  references: {
    id: string;
    title: string;
    url: string;
    description: string;
    userRating: "up" | "down" | null;
  }[];
  comparisonSummary: string;
  userFeedback: "agree" | "disagree" | null;
};

function sortKey(value: Confidence): number {
  return value === "Unknown" ? -1 : Number(value);
}

function labelOf(value: Confidence): string {
  return value === "Unknown" ? "Unknown" : `${value}%`;
}

export type ViewMode = "educational" | "critical";

// Dashboard component (moved from App)
function Dashboard() {
  const [outputs, setOutputs] = useState<AIOutput[]>(mockAIOutputs);
  const [confidenceThreshold, setConfidenceThreshold] = useState(0);
  const [sortOrder, setSortOrder] = useState<"high-to-low" | "low-to-high">("high-to-low");
  const [viewMode, setViewMode] = useState<ViewMode>("educational");
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // Filter and sort outputs
  const filteredAndSortedOutputs = useMemo(() => {
    const filtered = outputs.filter(o =>
      o.confidence === "Unknown" || Number(o.confidence) >= confidenceThreshold
    );

    return filtered.sort((a, b) => {
      const ka = sortKey(a.confidence);
      const kb = sortKey(b.confidence);
      if (sortOrder === "high-to-low") {
        return kb - ka;
      } else {
        if (a.confidence === "Unknown" && b.confidence !== "Unknown") return 1;
        if (b.confidence === "Unknown" && a.confidence !== "Unknown") return -1;
        return ka - kb;
      }
    });
  }, [outputs, confidenceThreshold, sortOrder]);

  const handleFeedbackChange = (outputId: string, feedback: "agree" | "disagree" | null) => {
    setOutputs(prev => prev.map(output => 
      output.id === outputId ? { ...output, userFeedback: feedback } : output
    ));
  };

  const handleReferenceRating = (outputId: string, referenceId: string, rating: "up" | "down" | null) => {
    setOutputs(prev => prev.map(output => 
      output.id === outputId 
        ? {
            ...output,
            references: output.references.map(ref =>
              ref.id === referenceId ? { ...ref, userRating: rating } : ref
            )
          }
        : output
    ));
  };

  // Simulate AI analysis of user input
  const handleAnalyze = async (inputText: string) => {
    setIsAnalyzing(true);
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Generate mock analysis based on input text
    const analysisResult = generateAnalysis(inputText);
    
    // Add to beginning of outputs list
    setOutputs(prev => [analysisResult, ...prev]);
    setIsAnalyzing(false);
  };

  // Mock analysis generation function
  const generateAnalysis = (text: string): AIOutput => {
    // Simple heuristics to determine confidence and category
    const textLength = text.length;
    const hasNumbers = /\d/.test(text);
    const hasScientificTerms = /\b(study|research|evidence|data|analysis|according to)\b/i.test(text);
    const hasPredictive = /\b(will|might|could|should|likely|probably|may)\b/i.test(text);
    
    // let confidence: number;
    let category: string;
    
    // Determine category based on content
    if (/\b(climate|temperature|carbon|emissions|global warming)\b/i.test(text)) {
      category = "Climate Science";
    } else if (/\b(stock|market|investment|financial|economy|inflation)\b/i.test(text)) {
      category = "Financial Analysis";
    } else if (/\b(technology|AI|quantum|computing|software|digital)\b/i.test(text)) {
      category = "Technology";
    } else if (/\b(health|medical|wellness|therapy|treatment|symptoms)\b/i.test(text)) {
      category = "Health & Wellness";
    } else if (/\b(space|planet|universe|telescope|astronomy|galaxy)\b/i.test(text)) {
      category = "Space Science";
    } else {
      category = "General Analysis";
    }
    
    // Calculate confidence based on text characteristics
    const isUnknown = Math.random() < 0.25;
    const confidence: Confidence = isUnknown
      ? "Unknown"
      : (() => {
          if (hasScientificTerms && hasNumbers && textLength > 100)
            return Math.floor(75 + Math.random() * 20); // 75-95
          if (hasPredictive || textLength < 50) return Math.floor(30 + Math.random() * 25); // 30-55
          return Math.floor(55 + Math.random() * 25); // 55-80
        })();

    const newId = `analysis-${Date.now()}`;
    
    return {
      id: newId,
      text: text,
      confidence: confidence,
      timestamp: new Date().toISOString(),
      category: category,
      references: [
        {
          id: `ref-${newId}-1`,
          title: "Source Analysis Database",
          url: "https://example.com/source-analysis",
          description: "Automated reference analysis for the provided content",
          userRating: null
        },
        {
          id: `ref-${newId}-2`,
          title: "Content Verification System",
          url: "https://example.com/verification",
          description: "Cross-referenced content validation and fact-checking",
          userRating: null
        }
      ],
      comparisonSummary: `Analysis of the provided text shows ${(confidence as number) >= 70 ? "strong" : (confidence as number) >= 50 ? 'moderate' : 'limited'} confidence based on content structure, factual indicators, and language patterns. ${hasScientificTerms ? 'Scientific terminology detected suggests higher reliability.' : ''} ${hasPredictive ? 'Predictive language indicates inherent uncertainty.' : ''}`,
      userFeedback: null
    };
  };

  return (
    <div>
        {/* Input Analysis Section */}
        <div className="mb-8">
          <InputAnalysis onAnalyze={handleAnalyze} isAnalyzing={isAnalyzing} />
        </div>

        {/* Filter Controls */}
        <div className="mb-8 bg-card rounded-lg p-6 shadow-sm border">
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
            <FilterControls
              confidenceThreshold={confidenceThreshold}
              onThresholdChange={setConfidenceThreshold}
              sortOrder={sortOrder}
              onSortOrderChange={setSortOrder}
            />
            <div className="flex gap-2">
              <ModeToggle viewMode={viewMode} onModeChange={setViewMode} />
              <ExportButton outputs={filteredAndSortedOutputs} />
            </div>
          </div>
        </div>

        {/* Results Summary */}
        <div className="mb-6">
          <p className="text-sm text-muted-foreground">
            Showing {filteredAndSortedOutputs.length} of {outputs.length} AI outputs
            {confidenceThreshold > 0 && ` with confidence ≥ ${confidenceThreshold}%`}
          </p>
        </div>

        {/* AI Output Cards */}
        <div className="space-y-6">
          {filteredAndSortedOutputs.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-muted-foreground">No AI outputs match your current filters.</p>
            </div>
          ) : (
            filteredAndSortedOutputs.map((output) => (
              <AIOutputCard
                key={output.id}
                output={output}
                viewMode={viewMode}
                onFeedbackChange={handleFeedbackChange}
                onReferenceRating={handleReferenceRating}
              />
            ))
          )}
        </div>
    </div>
  );
}

// Protected Route Component
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="mt-2 text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  // if (!isAuthenticated) {
  //   return <Navigate to="/login" replace />;
  // }

  return <>{children}</>;
}

// Dashboard with logout functionality
function DashboardWithAuth() {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-background">
      {/* Header with user info and logout */}
      <header className="bg-primary text-primary-foreground shadow-sm">
        <div className="container mx-auto px-4 py-6 max-w-6xl">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-white mb-2">AI Assistant Confidence Dashboard</h1>
              <p className="text-primary-foreground/80">
                Monitor and evaluate AI response confidence levels with detailed analysis and references
              </p>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm">Welcome, {user?.first_name || user?.email}</span>
              <button
                onClick={logout}
                className="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-md text-sm transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <Dashboard />
      </div>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route 
            path="/" 
            element={
              <ProtectedRoute>
                <DashboardWithAuth />
              </ProtectedRoute>
            } 
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}