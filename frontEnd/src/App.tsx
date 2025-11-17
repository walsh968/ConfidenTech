import { useState, useMemo, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AIOutputCard } from "./components/ai-output-card";
import { FilterControls } from "./components/filter-controls";
import { ExportButton } from "./components/export-button";
import { ModeToggle } from "./components/mode-toggle";
import { InputAnalysis } from "./components/input-analysis";
import { LoginPage } from "./components/LoginPage";
import { RegisterPage } from "./components/RegisterPage";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import { ProfileMenu } from "./components/profile-menu";
import React from "react";
import { createPortal } from "react-dom";

/* =========================
   Types
========================= */
type Confidence = number | "Unknown";

export type AIOutput = {
  id: string;
  question?: string;
  text: string;
  confidence: Confidence;
  timestamp: string; // ISO
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
  sentenceAlignment?: {
    aligned: number[]; // Indices of aligned sentences
    conflicting: number[]; // Indices of conflicting sentences
    sentences?: string[]; // Split sentences for highlighting
  };
};

export type ViewMode = "educational" | "critical";
type SortOrder = "time" | "high-to-low" | "low-to-high";

/* =========================
   Mock data
========================= */
const mockAIOutputs: AIOutput[] = [
  {
    id: "1",
    question: "q1?",
    text:
      "Climate change is primarily caused by human activities, particularly the emission of greenhouse gases from burning fossil fuels. The scientific consensus is overwhelming, with over 97% of climate scientists agreeing on this fact.",
    confidence: 94,
    timestamp: "2024-01-15T10:30:00Z",
    category: "Climate Science",
    references: [
      {
        id: "ref-1",
        title: "IPCC Sixth Assessment Report",
        url: "https://ipcc.ch/assessment-report/ar6/",
        description: "Comprehensive scientific assessment of climate change evidence",
        userRating: null,
      },
      {
        id: "ref-2",
        title: "NASA Climate Evidence",
        url: "https://climate.nasa.gov/evidence/",
        description: "NASA's compilation of climate change evidence and data",
        userRating: "up",
      },
    ],
    comparisonSummary:
      "All referenced sources strongly align with the AI output, providing consistent evidence for human-caused climate change. The consensus data and scientific assessments support the confidence level.",
    userFeedback: null,
  },
  {
    id: "2",
    question: "q2?",
    text:
      "The stock market will likely experience significant volatility in the next quarter due to geopolitical tensions and inflation concerns. Investors should consider diversifying their portfolios.",
    confidence: 67,
    timestamp: "2024-01-14T15:45:00Z",
    category: "Financial Analysis",
    references: [
      {
        id: "ref-3",
        title: "Federal Reserve Economic Data",
        url: "https://fred.stlouisfed.org/",
        description: "Latest economic indicators and inflation data",
        userRating: "up",
      },
      {
        id: "ref-4",
        title: "Market Analysis Report",
        url: "https://example.com/market-report",
        description: "Third-party analysis of current market conditions",
        userRating: null,
      },
    ],
    comparisonSummary:
      "Economic data supports concerns about inflation, but market prediction sources show mixed signals. Some indicators suggest stability while others point to volatility, reflecting the moderate confidence score.",
    userFeedback: "disagree",
  },
  {
    id: "3",
    question: "q3?",
    text:
      "Quantum computing could revolutionize cryptography within the next 5-10 years, potentially breaking current encryption methods. Organizations should start preparing quantum-resistant security measures.",
    confidence: 73,
    timestamp: "2024-01-13T09:20:00Z",
    category: "Technology",
    references: [
      {
        id: "ref-5",
        title: "NIST Post-Quantum Cryptography",
        url: "https://csrc.nist.gov/projects/post-quantum-cryptography",
        description: "Official NIST standards for quantum-resistant cryptography",
        userRating: "up",
      },
      {
        id: "ref-6",
        title: "IBM Quantum Computing Timeline",
        url: "https://research.ibm.com/quantum-computing",
        description: "IBM's roadmap for quantum computing development",
        userRating: null,
      },
    ],
    comparisonSummary:
      "Official standards bodies and major tech companies acknowledge the quantum threat timeline, though exact timing remains uncertain. Sources generally support the 5-10 year timeframe with some variation.",
    userFeedback: "agree",
  },
  {
    id: "4",
    question: "q4?",
    text:
      "Adding meditation to your daily routine can reduce stress levels by up to 40% according to recent studies. Even 10 minutes per day can make a significant difference in mental well-being.",
    confidence: 86,
    timestamp: "2024-01-12T14:15:00Z",
    category: "Health & Wellness",
    references: [
      {
        id: "ref-7",
        title: "Mayo Clinic - Meditation Benefits",
        url: "https://mayoclinic.org/meditation",
        description: "Medical evidence for meditation's stress reduction benefits",
        userRating: "up",
      },
      {
        id: "ref-8",
        title: "Harvard Health - Mindfulness Research",
        url: "https://health.harvard.edu/mindfulness",
        description: "Harvard's research on mindfulness and stress reduction",
        userRating: "up",
      },
    ],
    comparisonSummary:
      "Multiple peer-reviewed studies and medical institutions consistently report stress reduction benefits from meditation. The 40% figure aligns with several research studies, supporting the high confidence level.",
    userFeedback: null,
  },
  {
    id: "5",
    question: "q5?",
    text:
      "The James Webb Space Telescope might discover signs of extraterrestrial life in the next few years by analyzing exoplanet atmospheres for biosignatures like oxygen and methane.",
    confidence: 45,
    timestamp: "2024-01-11T11:30:00Z",
    category: "Space Science",
    references: [
      {
        id: "ref-9",
        title: "NASA JWST Mission Overview",
        url: "https://jwst.nasa.gov/",
        description: "Official NASA documentation of JWST capabilities",
        userRating: null,
      },
      {
        id: "ref-10",
        title: "Exoplanet Biosignature Research",
        url: "https://example.com/biosignatures",
        description: "Current research on detecting life through atmospheric analysis",
        userRating: "down",
      },
    ],
    comparisonSummary:
      "While JWST has the technical capability to detect atmospheric signatures, the likelihood of finding definitive biosignatures remains speculative. Scientific sources emphasize the challenges and uncertainties involved.",
    userFeedback: null,
  },
  {
    id: "6",
    question: "q6?",
    text: "This response currently has an unknown confidence from the backend.",
    confidence: "Unknown",
    timestamp: "2024-01-10T08:00:00Z",
    category: "General Analysis",
    references: [],
    comparisonSummary: "Backend did not provide a numeric confidence score.",
    userFeedback: null,
  },
];

/* =========================
   Fixed input bar via Portal
========================= */
function FixedInputBar({ children }: { children: React.ReactNode }) {
  const ref = React.useRef<HTMLDivElement | null>(null);

  React.useEffect(() => {
    if (!ref.current) return;

    const el = ref.current;
    const setVar = () => {
      const h = el.offsetHeight;
      document.documentElement.style.setProperty("--input-bar-height", `${h}px`);
    };
    setVar();
    const ro = new ResizeObserver(setVar);
    ro.observe(el);
    window.addEventListener("resize", setVar);
    return () => {
      ro.disconnect();
      window.removeEventListener("resize", setVar);
    };
  }, []);

  return createPortal(
    <div ref={ref} className="fixed-input-bar">
      <div className="mx-auto w-full max-w-6xl px-4">
        <div className="py-3">
          {children}
        </div>
      </div>
    </div>,
    document.body
  );
}



/* =========================
   Dashboard
========================= */
function Dashboard() {
  // Load outputs from localStorage on initial mount
  const loadOutputsFromStorage = (): AIOutput[] => {
    try {
      const stored = localStorage.getItem('confidenTech_outputs');
      if (stored) {
        const parsed = JSON.parse(stored);
        // Validate that it's an array
        if (Array.isArray(parsed) && parsed.length > 0) {
          return parsed;
        }
      }
    } catch (error) {
      console.error('Error loading outputs from localStorage:', error);
    }
    // Return empty array instead of mock data for fresh starts
    return [];
  };

  const [outputs, setOutputs] = useState<AIOutput[]>(loadOutputsFromStorage);
  const [confidenceThreshold, setConfidenceThreshold] = useState(0);
  const [sortOrder, setSortOrder] = useState<SortOrder>("time");
  const [viewMode, setViewMode] = useState<ViewMode>("educational");
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // Save outputs to localStorage whenever they change
  useEffect(() => {
    try {
      localStorage.setItem('confidenTech_outputs', JSON.stringify(outputs));
    } catch (error) {
      console.error('Error saving outputs to localStorage:', error);
    }
  }, [outputs]);

  // sorted by time
  const filteredAndSortedOutputs = useMemo(() => {
    const allowUnknown = (sortOrder === "time") && (confidenceThreshold === 0);
    const filtered = outputs.filter((o) => {
      if (o.confidence === "Unknown") {
        return allowUnknown; 
      }
      return Number(o.confidence) >= confidenceThreshold;
    });
  
    if (sortOrder === "time") {
      return filtered.sort(
        (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
      );
    } else {
      const dir = sortOrder === "high-to-low" ? -1 : 1;
      return filtered.sort((a, b) => {
        const ca = Number(a.confidence);
        const cb = Number(b.confidence);
        return (ca - cb) * dir;
      });
    }
  }, [outputs, confidenceThreshold, sortOrder]);

  const handleAnalyze = async (inputText: string) => {
    setIsAnalyzing(true);

    // Implement actual API call
    const response = await fetch("http://127.0.0.1:8000/api/users/analyze/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json",
      },
      body: JSON.stringify({
        text: inputText,
      }),
    });

    const data = await response.json();
    console.log("Confidence Score: ", data.score);
    console.log("Answer: ", data.answer);

    let references: AIOutput['references'] = [];
    let sentenceAlignment: AIOutput['sentenceAlignment'] = undefined;
    
    try {
      const response2 = await fetch("http://127.0.0.1:8000/api/users/sites/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json",
        },
        body: JSON.stringify({
          prompt: inputText,
          answer: data.answer,
        }),
      });

      if (response2.ok) {
        const data2 = await response2.json();
        console.log("References data: ", data2);
        console.log("Titles: ", data2.title);
        console.log("Links: ", data2.link);
        console.log("Snippets: ", data2.snippet);
        console.log("Sentence Alignment: ", data2.sentenceAlignment);

        // Map backend references to frontend format
        if (data2.title && Array.isArray(data2.title) && data2.title.length > 0) {
          references = data2.title.map((title: string, index: number) => ({
            id: `ref-${Date.now()}-${index}`,
            title: title || "Untitled Reference",
            url: data2.link?.[index] || "",
            description: data2.snippet?.[index] || "No description available",
            userRating: null as "up" | "down" | null,
          }));
        }

        // Get sentence alignment data from backend
        if (data2.sentenceAlignment) {
          sentenceAlignment = {
            aligned: data2.sentenceAlignment.aligned || [],
            conflicting: data2.sentenceAlignment.conflicting || [],
            sentences: data2.sentenceAlignment.sentences || [],
          };
        }
      } else {
        console.error("Failed to fetch references:", response2.status, response2.statusText);
      }
    } catch (error) {
      console.error("Error fetching references:", error);
      // Continue with empty references array
    }

    //await new Promise((resolve) => setTimeout(resolve, 2000));
    const analysisResult = generateAnalysis(inputText, data.answer, data.score, references, sentenceAlignment);
    setOutputs((prev) => [...prev, analysisResult]);
    setIsAnalyzing(false);
  };

  const handleFeedbackChange = (
    outputId: string,
    feedback: "agree" | "disagree" | null
  ) => {
    setOutputs((prev) =>
      prev.map((output) => (output.id === outputId ? { ...output, userFeedback: feedback } : output))
    );
  };

  const handleReferenceRating = (
    outputId: string,
    referenceId: string,
    rating: "up" | "down" | null
  ) => {
    setOutputs((prev) =>
      prev.map((output) =>
        output.id === outputId
          ? {
              ...output,
              references: output.references.map((ref) =>
                ref.id === referenceId ? { ...ref, userRating: rating } : ref
              ),
            }
          : output
      )
    );
  };

  const generateAnalysis = (
    question: string, 
    text: string, 
    score: number, 
    references: AIOutput['references'] = [],
    sentenceAlignment?: AIOutput['sentenceAlignment']
  ): AIOutput => {
    const textLength = text.length;
    const hasNumbers = /\d/.test(text);
    const hasScientificTerms = /\b(study|research|evidence|data|analysis|according to)\b/i.test(text);
    const hasPredictive = /\b(will|might|could|should|likely|probably|may)\b/i.test(text);

    let category: string;
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

    const newId = `analysis-${Date.now()}`;
    let confidence = score;

    // Use actual references from backend, or fallback to empty array
    const actualReferences = references.length > 0 ? references : [];

    // Generate comparison summary based on references
    let comparisonSummary = `Analysis of the provided text shows ${
      (confidence as number) >= 70 ? "strong" : (confidence as number) >= 50 ? "moderate" : "limited"
    } confidence based on content structure, factual indicators, and language patterns.`;
    
    if (actualReferences.length > 0) {
      comparisonSummary += ` Found ${actualReferences.length} relevant reference${actualReferences.length > 1 ? 's' : ''} to support this information.`;
    } else {
      comparisonSummary += " No external references were found for this response.";
    }
    
    if (hasScientificTerms) {
      comparisonSummary += " Scientific terminology detected suggests higher reliability.";
    }
    if (hasPredictive) {
      comparisonSummary += " Predictive language indicates inherent uncertainty.";
    }

    return {
      id: newId,
      question: question,
      text: text,
      confidence,
      timestamp: new Date().toISOString(),
      category,
      references: actualReferences,
      comparisonSummary,
      userFeedback: null,
      sentenceAlignment: sentenceAlignment,
    };
  };

  return (
    <>
      <div className="app-main min-h-screen overflow-y-auto">
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
      <FixedInputBar>
        <InputAnalysis onAnalyze={handleAnalyze} isAnalyzing={isAnalyzing} />
      </FixedInputBar>
    </>
  );
}

/* =========================
   Auth wrappers
========================= */
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

  if (!isAuthenticated) {
     return <Navigate to="/login" replace />;
   }

  return <>{children}</>;
}

function DashboardWithAuth() {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-primary text-primary-foreground shadow-sm">
        <div className="container mx-auto px-4 py-6 max-w-6xl">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-white mb-2">ConfidenTech</h1>
              <p className="text-primary-foreground/80">
                Monitor and evaluate AI response confidence levels with detailed analysis and references
              </p>
            </div>
            <div className="flex items-center gap-4">
              <ProfileMenu user={user} onLogout={logout} />
            </div>
          </div>
        </div>
      </header>

      {/* Body */}
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <Dashboard />
      </div>
    </div>
  );
}

/* =========================
   App Root
========================= */
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
