"use client";

import { content } from "../../lib/content";
import { Suggestion } from "@/lib/types";
import { SuggestionCard } from "./components/suggestion-card";
import { AnimatePresence, motion } from "motion/react";

type MatchesProps = {
  suggestions: Suggestion[];
};

/**
 * Renders a list of suggested supervisor matches based on the user's research interests.
 *
 * @param suggestions - An array of the suggested supervisors.
 */
export default function Matches({ suggestions }: MatchesProps) {
  return (
    <div className="space-y-8">
      <header className="mb-12 text-center">
        <h1 className="text-4xl font-bold mb-4">{content.suggestions.title}</h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Based on your research interests, we have identified potential
          supervisors who align with your academic goals
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
