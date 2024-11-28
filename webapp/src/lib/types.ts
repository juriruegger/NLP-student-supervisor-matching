export type Supervisor = {
  email: string;
  name: string;
  image_url?: string;
  organisational_units?: string;
};

export type Suggestion = {
  similarity: number;
  contacted: boolean;
  supervisor: Supervisor;
};

export type Suggestions = Suggestion[];
