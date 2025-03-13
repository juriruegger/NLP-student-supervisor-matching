import type React from "react";
import { Skeleton } from "@/components/ui/skeleton";

const MatchesSkeleton: React.FC = () => {
  return (
    <div className="container mx-auto px-4 space-y-8">
      <header className="mb-12 text-center">
        <Skeleton className="h-20 w-full max-w-2xl mx-auto mb-4 rounded-2xl" />
        <Skeleton className="h-12 w-full max-w-2xl mx-auto rounded-2xl" />
      </header>
      <div className="space-y-4">
        {Array.from({ length: 5 }).map((_, index) => (
          <Skeleton key={index} className="w-full h-32 rounded-2xl" />
        ))}
      </div>
    </div>
  );
};

export default MatchesSkeleton;
