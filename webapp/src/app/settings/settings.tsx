"use client";

import { SupervisorAvailable } from "./available";

type SettingsProps = {
  availability: boolean | undefined;
};
export function Settings({ availability }: SettingsProps) {
  return (
    <div className="space-y-6 w-full">
      <h2 className="text-2xl font-semibold mb-4">Supervision</h2>
      <p className="text-xl text-muted-foreground max-w-2xl">
        Are you available for supervision in the upcoming semester?
      </p>
      <SupervisorAvailable available={availability} />
    </div>
  );
}
