"use clinet";

import { Button } from "@/components/ui/button";
import Link from "next/link";
import { content } from "../content";

export function Homepage() {
  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">{content.homepage.title}</h1>
      <p>{content.homepage.text1}</p>
      <p>{content.homepage.text2}</p>
      <div>
        <Link href="/student-form">
          <Button>Student Form</Button>
        </Link>
      </div>
    </div>
  );
}
