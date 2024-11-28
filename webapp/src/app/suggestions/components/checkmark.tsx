"use client";

import { Check } from "lucide-react";

type CheckmarkProps = {
  contacted: boolean;
};

export function Checkmark({ contacted }: CheckmarkProps) {
  return (
    <>
      {contacted ? (
        <Check size={24} className="text-green-500" />
      ) : (
        <Check size={24} className="text-transparent" /> // Hidden
      )}
    </>
  );
}
