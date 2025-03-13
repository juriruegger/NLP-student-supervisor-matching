import { getModel, getUserId } from "@/db";
import { Model } from "./model";

export default async function Page() {
  const userId = await getUserId();
  const bertModel = await getModel(userId);
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Settings</h1>
      <div className="space-y-2">
        <p>Model</p>
        <Model model={bertModel} />
      </div>
    </div>
  );
}
