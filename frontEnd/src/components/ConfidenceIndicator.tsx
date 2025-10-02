// This code was extracted from Figma, make adjustments as needed but try to replicate Figma design
// import { Progress } from "./ui/progress";
// import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "./ui/tooltip";
// import { Badge } from "./ui/badge";
// import { CircleDot } from "lucide-react";
// import type { ViewMode } from "../App";

// interface ConfidenceIndicatorProps {
//   confidence: number;
//   viewMode: ViewMode;
//   explanation?: string;
// }

// export function ConfidenceIndicator({ confidence, viewMode, explanation }: ConfidenceIndicatorProps) {
//   const getTrafficLightColor = () => {
//     if (confidence >= 75) return "text-green-500";
//     if (confidence >= 50) return "text-yellow-500";
//     return "text-red-500";
//   };

//   const getTrafficLightBg = () => {
//     if (confidence >= 75) return "bg-green-100 border-green-200";
//     if (confidence >= 50) return "bg-yellow-100 border-yellow-200";
//     return "bg-red-100 border-red-200";
//   };

//   const getConfidenceLabel = () => {
//     if (confidence >= 75) return "High";
//     if (confidence >= 50) return "Medium";
//     return "Low";
//   };

//   const getProgressColor = () => {
//     if (confidence >= 75) return "bg-green-500";
//     if (confidence >= 50) return "bg-yellow-500";
//     return "bg-red-500";
//   };

//   if (viewMode === "educational") {
//     return (
//       <TooltipProvider>
//         <Tooltip>
//           <TooltipTrigger asChild>
//             <div className="flex items-center gap-3">
//               {/* Traffic Light Icon */}
//               <div className={`p-2 rounded-full border ${getTrafficLightBg()}`}>
//                 <CircleDot className={`h-5 w-5 ${getTrafficLightColor()}`} />
//               </div>
              
//               {/* Confidence Badge */}
//               <Badge variant="outline" className="gap-1">
//                 {getConfidenceLabel()}
//               </Badge>
//             </div>
//           </TooltipTrigger>
//           <TooltipContent side="left" className="max-w-xs">
//             <p>{explanation}</p>
//           </TooltipContent>
//         </Tooltip>
//       </TooltipProvider>
//     );
//   }

//   // Critical mode - show all details
//   return (
//     <TooltipProvider>
//       <Tooltip>
//         <TooltipTrigger asChild>
//           <div className="flex items-center gap-3 min-w-fit">
//             {/* Traffic Light Icon */}
//             <div className={`p-1.5 rounded-full border ${getTrafficLightBg()}`}>
//               <CircleDot className={`h-4 w-4 ${getTrafficLightColor()}`} />
//             </div>
            
//             {/* Progress Bar and Percentage */}
//             <div className="flex items-center gap-2 min-w-24">
//               <div className="relative w-16">
//                 <div className="bg-primary/20 relative h-2 w-full overflow-hidden rounded-full">
//                   <div 
//                     className={`h-full transition-all ${getProgressColor()}`}
//                     style={{ width: `${confidence}%` }}
//                   />
//                 </div>
//               </div>
//               <span className="text-sm font-medium min-w-fit">
//                 {confidence}%
//               </span>
//             </div>
//           </div>
//         </TooltipTrigger>
//         <TooltipContent side="left" className="max-w-sm">
//           <p>{explanation}</p>
//         </TooltipContent>
//       </Tooltip>
//     </TooltipProvider>
//   );
// }