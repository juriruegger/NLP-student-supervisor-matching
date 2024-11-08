import Matches from "./matches";
import { getSuggestions } from "./actions";
import Link from "next/link";

type PageProps = {
  searchParams: {
    email: string;
  };
};
export default async function Page({ searchParams }: PageProps) {
  const email = searchParams.email;

  if (!email) {
    return <pre><Link href={'/student-form'}>No email found. Please proceed to the form</Link></pre>;
  }

  const suggestions = await getSuggestions(email);

  const topThree = await suggestions.slice(0, 3);


  return <Matches suggestions={topThree} />;
}
