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
            {topic.label}
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
                      {topic.label}
                    </CommandItem>
                  </TooltipTrigger>
                  <TooltipContent>{topic.keywords.join(", ")}</TooltipContent>
                </Tooltip>
              </TooltipProvider>
            ))}
          </CommandGroup>
        </div>
      </Command>
    </>
  );
}
