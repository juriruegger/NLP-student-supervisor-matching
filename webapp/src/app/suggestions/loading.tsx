import React from "react";

const MatchesSkeleton: React.FC = () => {
  return (
    <div>
      <h1 className="text-3xl font-bold bg-gray-300 rounded-md w-1/3 h-8 mb-4 animate-pulse"></h1>
      <p className="bg-gray-300 rounded-md w-full h-6 mb-6 animate-pulse"></p>
      <div className="mt-12 flex flex-col space-y-12">
        {Array.from({ length: 3 }).map((_, index) => (
          <div key={index} className="flex items-center space-x-20 w-full">
            <div className="rounded-full bg-gray-300 w-24 h-24 animate-pulse"></div>
            <div>
              <div className="bg-gray-300 rounded-md w-32 h-6 mb-2 animate-pulse"></div>
              <div className="bg-gray-300 rounded-md w-24 h-6 animate-pulse"></div>
            </div>
            <div className="bg-gray-300 rounded-md w-36 h-10 animate-pulse"></div>
            <div className="bg-gray-300 rounded-full w-8 h-8 animate-pulse"></div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MatchesSkeleton;
