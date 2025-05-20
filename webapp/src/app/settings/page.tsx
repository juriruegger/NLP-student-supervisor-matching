import { getAvailability } from "./actions";
import { Settings } from "./settings";

export default async function StudentFormPage() {
  let availability = await getAvailability();
  if (!availability) {
    availability = false;
  }
  return (
    <div className="space-y-6 w-full">
      <header className="mb-12">
        <h1 className="text-4xl font-bold mb-4">Settings</h1>
      </header>

      <Settings availability={availability} />
    </div>
  );
}
