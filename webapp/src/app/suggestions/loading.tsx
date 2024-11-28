import { content } from "@/lib/content";
import React from "react";

const MatchesSkeleton: React.FC = () => {
  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">{content.suggestions.title}</h1>
      <div className="mt-12 flex flex-col space-y-12">
        {Array.from({ length: 5 }).map((_, index) => (
          <div key={index} className="flex items-center space-x-6 w-full">
            <div className="rounded-full bg-gray-300 w-24 h-24 animate-pulse"></div>
            <div>
              <div className="bg-gray-300 rounded-md w-56 h-6 mb-2 animate-pulse"></div>
              <div className="bg-gray-300 rounded-md w-96 h-12 animate-pulse"></div>
            </div>
            <div className="bg-gray-300 rounded-md w-36 h-10 animate-pulse"></div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MatchesSkeleton;
