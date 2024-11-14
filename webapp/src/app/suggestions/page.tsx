import Matches from "./matches";
import { getUserSuggestions } from "./actions";

export default async function Page() {
  const suggestions = await getUserSuggestions();

  return <Matches suggestions={suggestions} />;
}
