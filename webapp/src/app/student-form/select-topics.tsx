"use client";

import { Badge } from "@/components/ui/badge";
import {
  Command,
  CommandInput,
  CommandEmpty,
  CommandGroup,
  CommandItem,
} from "@/components/ui/command";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Topics, Topic } from "@/lib/types";
import { X } from "lucide-react";
import { useMemo } from "react";

export type SelectTopicsProps = {
  topics: Topics;
  value: Topic[];
  onChange: (value: Topic[]) => void;
};

/**
 * The multi-select component for choosing topics.
 *
 * Displays selected topics as badges with the ability to remove them,
 * and allows searching and selecting topics.
 * Each topic displays its keywords as a tooltip.
 */
export function SelectTopics({ topics, value, onChange }: SelectTopicsProps) {
  const selected = useMemo(() => value ?? [], [value]);

  const handleSelect = (topic: Topic) => onChange([...selected, topic]);
  const handleRemove = (topic: Topic) =>
    onChange(selected.filter((t) => t.topicId !== topic.topicId));

  const unselectedTopics = useMemo(
    () => topics.filter((t) => !selected.some((s) => s.topicId === t.topicId)),
    [selected, topics],
  );

  return (
    <>
      <div className="flex flex-wrap gap-2">
        {selected.map((topic) => (
          <Badge variant="default" key={topic.topicId} className="gap-1">
            {prettify(topic.label)}
            <X className="size-3" onClick={() => handleRemove(topic)} />
          </Badge>
        ))}
      </div>
      <Command className="w-full">
        <CommandInput placeholder="Search topics..." />
        <CommandEmpty>No topics found.</CommandEmpty>
        <div className="max-h-96 overflow-y-auto">
          <CommandGroup className="flex-1 flex-col">
            {unselectedTopics.map((topic) => (
              <TooltipProvider key={topic.topicId}>
                <Tooltip>
                  <TooltipTrigger>
                    <CommandItem
                      key={topic.topicId}
                      value={[...topic.keywords].join(" ")}
                      onSelect={() => handleSelect(topic)}
                    >
                      {prettify(topic.label)}
                    </CommandItem>
                  </TooltipTrigger>
                  <TooltipContent>
                    {topic.keywords
                      .filter((keyword) => keyword.trim() !== "")
                      .map(prettify)
                      .join(", ")}
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            ))}
          </CommandGroup>
        </div>
      </Command>
    </>
  );
}

/**
 * Prettifies a string by capitalizing the first letter of each word,
 * while preserving acronyms in uppercase.
 */
export function prettify(text: string): string {
  return text
    .split(" ")
    .map((word) => {
      if (Object.keys(acronyms).includes(word.toLowerCase())) {
        return acronyms[word.toLowerCase()];
      }
      return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
    })
    .join(" ");
}

export const acronyms: Record<string, string> = {
  nlp: "NLP",
  css: "CSS",
  hci: "HCI",
  tinyml: "TinyML",
  ml: "ML",
  iot: "IoT",
  mpc: "MPC",
  llm: "LLM",
  ai: "AI",
  eeg: "EEG",
  esg: "ESG",
  "ui/ux": "UI/UX",
  cscw: "CSCW",
  sts: "STS",
  mrs: "MRS",
  ux: "UX",
  eaa: "EAA",
  wad: "WAD",
  api: "API",
  gpu: "GPU",
  genai: "GenAI",
  it: "IT",
};
