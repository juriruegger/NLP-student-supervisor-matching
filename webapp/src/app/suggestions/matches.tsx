"use client";

import { content } from "../../lib/content";
import { Suggestion } from "@/lib/types";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Loading from "./loading";
import { supabase } from "@/utils/utils";
import { SuggestionCard } from "./components/suggestion-card";
import { AnimatePresence, motion } from "motion/react";

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
      <header className="mb-12 text-center">
        <h1 className="text-4xl font-bold mb-4">{content.suggestions.title}</h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Based on your research interests, we have identified potential
          supervisors who align with your academic goals.
        </p>
      </header>
      <AnimatePresence mode="wait">
        <div className="space-y-6">
          {suggestions.map((suggestion, index) => (
            <motion.div
              key={suggestion.uuid}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: index * 0.2 }}
            >
              <SuggestionCard suggestion={suggestion} />
            </motion.div>
          ))}
        </div>
      </AnimatePresence>
    </div>
  );
}
