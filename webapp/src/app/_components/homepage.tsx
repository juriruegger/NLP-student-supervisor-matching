"use client";

import { Button } from "@/components/ui/button";
import Link from "next/link";
import { content } from "../../lib/content";

export function Homepage() {
  return (
    <div className="space-y-8">
      <header className="mb-12 text-center">
        <h1 className="text-4xl font-bold mb-4">{content.homepage.title}</h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Find the perfect supervisor to guide you through your academic project
        </p>
      </header>
      <p>{content.homepage.text1}</p>
      <p>{content.homepage.text2}</p>
      <p>{content.homepage.text3}</p>
      <div className="flex justify-center">
        <Link href="/student-form">
          <Button>Begin</Button>
        </Link>
      </div>
    </div>
  );
}
