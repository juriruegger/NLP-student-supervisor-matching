import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

if (!supabaseUrl) {
  throw new Error("Missing env.NEXT_PUBLIC_SUPABASE_URL");
}

if (!supabaseAnonKey) {
  throw new Error("Missing env.NEXT_PUBLIC_SUPABASE_ANON_KEY");
}

const supabase = createClient(supabaseUrl, supabaseAnonKey);

export async function setStudent(name: string, email: string, text: string) {
  const { data, error } = await supabase
    .from("students")
    .upsert({ name: name, email: email, text: text });

  if (error) {
    console.error(error);
  }

  return data;
}

export async function getText(email: string) {
  const { data: student, error } = await supabase
    .from("students")
    .select("text")
    .eq("email", `${email}`)
    .single();

  if (error) {
    console.error(error);
  }

  const studentText = student?.text;

  return studentText;
}
