"use client";

import { Button } from "@/components/ui/button";
import { contactSupervisor } from "../actions";
import { Suggestion } from "@/lib/types";
import { useRouter } from "next/navigation";

type MeetingButtonProps = {
  suggestion: Suggestion;
};

export function MeetingButton({ suggestion }: MeetingButtonProps) {
  const router = useRouter();
  const onClick = (supervisor: string) => {
    contactSupervisor(supervisor);
    router.refresh();
  };
  return (
    <a
      href={`mailto:${suggestion.supervisor.email}?subject=Research%20Project%20Meeting`}
    >
      <Button
        onClick={() => onClick(suggestion.supervisor.name)}
        variant="secondary"
      >
        Send an email
      </Button>
    </a>
  );
}
