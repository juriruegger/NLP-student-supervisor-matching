"use client";

import { Button } from "@/components/ui/button";
import { contactSupervisor } from "../actions";
import { Suggestion } from "@/lib/types";

type MeetingButtonProps = {
  suggestion: Suggestion;
  setContacted: (contacted: boolean) => void;
};

/**
 * Renders a button that allows the user to send an email to a supervisor to request a research project meeting.
 * When clicked, the button triggers the `contactSupervisor` function with the supervisor's UUID and updates the contacted state.
 */
export function MeetingButton({
  suggestion,
  setContacted,
}: MeetingButtonProps) {
  const onClick = (supervisor: string) => {
    contactSupervisor(supervisor);
    setContacted(true);
  };
  return (
    <a href={`mailto:${suggestion.email}?subject=Research%20Project%20Meeting`}>
      <Button onClick={() => onClick(suggestion.uuid)} variant="secondary">
        Send an email
      </Button>
    </a>
  );
}
