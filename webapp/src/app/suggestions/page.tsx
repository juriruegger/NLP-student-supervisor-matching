import Matches from "./_components/matches";

type PageProps = {
  searchParams: {
    email: string;
  };
};
export default async function Page({ searchParams }: PageProps) {
  const email = searchParams.email;

  if (!email || typeof email !== "string") {
    return <div>Missing email</div>;
  }

  return <Matches />;
}
