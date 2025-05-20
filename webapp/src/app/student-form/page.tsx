import { content } from "../../lib/content";
import { getTopics } from "./actions";
import { StudentInput } from "./studentInput";

export default async function StudentFormPage() {
  const topics = await getTopics();
  return (
    <div className="space-y-6">
      <header className="mb-12 text-center">
        <h1 className="text-4xl font-bold mb-4">{content.studentForm.title}</h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Share your research interests and academic background with us.
        </p>
      </header>
      <StudentInput topics={topics} />
    </div>
  );
}
