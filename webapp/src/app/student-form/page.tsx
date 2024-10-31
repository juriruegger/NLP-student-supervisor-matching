import { content } from "../../lib/content";
import { StudentInput } from "./studentInput";

export default function StudentFormPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">{content.studentForm.title}</h1>
      <StudentInput />
    </div>
  );
}
