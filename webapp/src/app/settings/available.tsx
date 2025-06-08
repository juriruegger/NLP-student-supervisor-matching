"use client";

import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useState } from "react";
import { storeAvailability } from "./actions";

type SupervisorUnavailableProps = {
  available: boolean | undefined;
};

/**
 * Renders a select dropdown allowing a supervisor to set their availability status.
 */
export function SupervisorAvailable({ available }: SupervisorUnavailableProps) {
  const [availability, setAvailability] = useState<boolean>(available ?? true);

  const onChange = (value: string) => {
    const available = value === "available";
    setAvailability(available);
    storeAvailability(available);
  };

  return (
    <Select
      value={availability ? "available" : "unavailable"}
      onValueChange={onChange}
    >
      <SelectTrigger>
        <SelectValue placeholder="Are you available for supervision?" />
      </SelectTrigger>
      <SelectContent>
        <SelectGroup>
          <SelectItem value="available">Available</SelectItem>
          <SelectItem value="unavailable">Unavailable</SelectItem>
        </SelectGroup>
      </SelectContent>
    </Select>
  );
}
