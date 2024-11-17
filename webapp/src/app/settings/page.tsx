import { getModel } from "@/db";
import { Model } from "./model";

export default async function Page() {
  const bertModel = await getModel();
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Settings</h1>
      <Model model={bertModel} />
    </div>
  );
}
