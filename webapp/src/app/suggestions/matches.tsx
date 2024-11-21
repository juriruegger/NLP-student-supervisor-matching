"use client";

import { content } from "../../lib/content";
import { Suggestion } from "@/lib/types";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useEffect } from "react";
import { MeetingButton } from "./components/meeting-button";
import { Checkmark } from "./components/checkmark";
import { useRouter } from "next/navigation";
import Loading from "./loading";
import { supabase } from "@/utils/utils";
import { ProfileImage } from "./components/profile-image";

type MatchesProps = {
  suggestions: Suggestion[];
  user: string;
};

export default function Matches({ suggestions, user }: MatchesProps) {
  const router = useRouter();

  useEffect(() => {
    // We are looking for changes to the student_supervisor table and refreshing the page, once the new data arrives.
    const channel = supabase
      .channel("custom-filter-channel")
      .on(
        "postgres_changes",
        {
          event: "INSERT",
          schema: "public",
          table: "student_supervisor",
          filter: `student_id=eq.${user}`,
        },
        () => {
          router.refresh();
        },
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [user, router]);

  if (suggestions.length === 0) {
    return <Loading />;
  }

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold mb-8">{content.suggestions.title}</h1>
      <div className="space-y-6">
        {suggestions.map((suggestion, index) => (
          <div
            key={index}
            className="flex flex-col sm:flex-row items-center justify-between bg-card rounded-lg p-6 shadow-sm"
          >
            <div className="flex flex-col sm:flex-row items-center space-y-4 sm:space-y-0 sm:space-x-6 mb-4 sm:mb-0">
              {suggestion.supervisors.image_url ? (
                <ProfileImage
                  src={suggestion.supervisors.image_url}
                  name={suggestion.supervisors.name}
                />
              ) : (
                <ProfileImage
                  src="https://i.ibb.co/4YRNjF3/Profile-Picture.webp"
                  name={suggestion.supervisors.name}
                />
              )}
              <div className="flex flex-col items-center sm:items-start">
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger>
                      <h2 className="text-xl font-bold text-center sm:text-left">
                        {suggestion.supervisors.name}
                      </h2>
                    </TooltipTrigger>
                    <TooltipContent>{suggestion.similarity}</TooltipContent>
                  </Tooltip>
                </TooltipProvider>
                <p className="text-sm text-gray-500">
                  {suggestion.supervisors.organisational_units}
                </p>
              </div>
            </div>
            <div className="flex flex-col sm:flex-row items-center space-y-4 sm:space-y-0 sm:space-x-4 ml-8">
              <MeetingButton suggestion={suggestion} />
              <Checkmark contacted={suggestion.contacted} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
