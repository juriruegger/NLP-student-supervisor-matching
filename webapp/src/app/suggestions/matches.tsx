'use client';

import { content } from "../../lib/content";
import Image from "next/image";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Check } from "lucide-react";
import { Supervisors } from "@/lib/types";

type MatchesProps = {
  suggestions: Supervisors[];
};

export default function Matches({ suggestions }: MatchesProps) {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">{content.suggestions.title}</h1>

      <div className="space-y-6">
        {suggestions.map((supervisor, index) => (
          <div
            key={index}
            className="flex flex-col sm:flex-row items-center justify-between bg-card rounded-lg p-6 shadow-sm"
          >
            <div className="flex flex-col sm:flex-row items-center space-y-4 sm:space-y-0 sm:space-x-6 mb-4 sm:mb-0">
              <Image
                src={"https://i.ibb.co/HBnGqCD/realistic-animal3.webp"}
                alt={supervisor.supervisor}
                width={80}
                height={80}
                className="rounded-full"
              />
              <h2 className="text-xl font-bold text-center sm:text-left">
                {supervisor.supervisor}
              </h2>
            </div>
            <div className="flex flex-col sm:flex-row items-center space-y-4 sm:space-y-0 sm:space-x-4">
              <a href={`mailto:${supervisor.email}`}>
                <Button variant="secondary">Set up a meeting</Button>
              </a>
              <Check size={24} className="text-green-500" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
