"use client";

import { Check } from "lucide-react";

type CheckmarkProps = {
  contacted: boolean;
};

export function Checkmark({ contacted }: CheckmarkProps) {
  return <>{contacted && <Check size={24} />}</>;
}
