import Matches from "./matches";
import { getSuggestions } from "./actions";
import { redirect } from "next/navigation";

export const dynamic = "force-dynamic";

type PageProps = {
  searchParams: {
    email: string;
  };
};

export default async function Page({ searchParams }: PageProps) {
  const email = searchParams.email;

  if (!email) {
    redirect("/student-form");
  }

  try {
    const suggestions = await getSuggestions(email);

    if (suggestions.length > 0) {
      const topThree = suggestions.slice(0, 3);
      return <Matches suggestions={topThree} />;
    }
  } catch (error: any) {
    return <pre>Error: {error.message}</pre>;
  }
}
