"use client";

import type { Suggestion } from "@/lib/types";
import { ProfileImage } from "./profile-image";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { MeetingButton } from "./meeting-button";
import { Checkmark } from "./checkmark";
import { ChevronDown, ChevronUp, File, Building2 } from "lucide-react";
import { useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

export function SuggestionCard({ suggestion }: { suggestion: Suggestion }) {
  const [expanded, setExpanded] = useState(false);
  const [contacted, setContacted] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, x: -80 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{
        duration: 1,
        ease: "easeOut",
      }}
    >
      <Card className="w-full rounded-2xl">
        <CardContent className="p-6">
          <div className="flex flex-col sm:flex-row items-center justify-between">
            <div className="flex flex-col sm:flex-row items-center sm:items-start space-y-4 sm:space-y-0 sm:space-x-6 mb-4 sm:mb-0 flex-1">
              {suggestion.imageUrl ? (
                <ProfileImage
                  src={suggestion.imageUrl}
                  name={suggestion.name}
                />
              ) : (
                <ProfileImage
                  src="https://i.ibb.co/4YRNjF3/Profile-Picture.webp"
                  name={suggestion.name}
                />
              )}
              <div className="flex flex-col items-center sm:items-start space-y-4">
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger>
                      <div className="flex items-center gap-2">
                        <h2 className="text-xl font-bold text-center sm:text-left">
                          {suggestion.name}
                        </h2>
                        <Checkmark
                          contacted={contacted || suggestion.contacted}
                        />
                      </div>
                    </TooltipTrigger>
                    <TooltipContent>{suggestion.similarity}</TooltipContent>
                  </Tooltip>
                </TooltipProvider>
                <div className="flex flex-wrap gap-2">
                  {suggestion.keywords.map((keyword, index) => (
                    <Badge key={index} variant="secondary">
                      {keyword}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
            <Button
              variant="ghost"
              onClick={() => setExpanded(!expanded)}
              aria-expanded={expanded}
              aria-controls={`expandable-content-${suggestion.name}`}
            >
              {expanded ? (
                <ChevronUp className="h-4 w-4" />
              ) : (
                <ChevronDown className="h-4 w-4" />
              )}
              <span className="sr-only">
                {expanded ? "Show less" : "Show more"}
              </span>
            </Button>
          </div>

          <AnimatePresence>
            {expanded && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.3, ease: "easeInOut" }}
                className="overflow-hidden mt-4 space-y-6"
              >
                <Separator />
                {suggestion.topPaper && suggestion.topPaper.url && (
                  <>
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold">
                        Research Alignment
                      </h3>
                      <div className="space-y-3">
                        <p className="text-sm text-muted-foreground">
                          Your research interests seem to align well with this
                          paper from {suggestion.firstName}
                        </p>
                        <div className="max-w-full overflow-hidden">
                          <Link
                            href={suggestion.topPaper?.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex gap-2 items-start text-sm hover:underline text-primary"
                          >
                            <File className="h-4 w-4 mt-0.5" />
                            <span className="flex-1 min-w-0 break-words leading-relaxed">
                              {suggestion.topPaper?.title}
                            </span>
                          </Link>
                        </div>
                      </div>
                    </div>
                    <Separator />
                  </>
                )}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Affiliations</h3>
                  <ul className="space-y-2">
                    {Array.from(
                      new Map(
                        suggestion.organisationalUnits.map((organisation) => [
                          organisation.name,
                          organisation,
                        ])
                      ).values()
                    ).map((organisation, idx) => (
                      <li key={idx} className="flex items-center space-x-2">
                        <Building2 className="h-4 w-4 text-muted-foreground" />
                        <Link
                          href={organisation.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm hover:underline"
                        >
                          {organisation.name}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="pt-4 flex justify-end">
                  <MeetingButton
                    suggestion={suggestion}
                    setContacted={setContacted}
                  />
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </CardContent>
      </Card>
    </motion.div>
  );
}
