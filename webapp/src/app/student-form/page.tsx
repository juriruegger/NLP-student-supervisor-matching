"use client";

import { content } from "../content";
import { StudentInput } from "./_components/studentInput";

export default function page() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">{content.studentForm.title}</h1>
      <StudentInput />
    </div>
  );
}
