"use client";

import z from "zod";
import { useForm } from "react-hook-form";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormMessage,
} from "@/components/ui/form";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";

const formSchema = z.object({
  text: z
    .string()
    .min(10, { message: "Your submission must be at least 10 characters" }),
  projectType: z.enum(["specific", "general"]).optional(),
});

type InterestFormProps = {
  onSubmit: (data: z.infer<typeof formSchema>) => void;
  form: ReturnType<typeof useForm<z.infer<typeof formSchema>>>;
};

export function InterestForm({ onSubmit, form }: InterestFormProps) {
  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)}>
        <FormField
          control={form.control}
          name="text"
          render={({ field }) => (
            <FormItem className="shadow-md focus-within:shadow-lg transition-shadow duration-300 rounded-2xl border border-border">
              <FormControl>
                <Textarea
                  placeholder="What are you interested in? The more detail, the better!"
                  className="resize-none h-80 w-full rounded-2xl bg-input"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <div className="flex justify-center">
          <Button type="submit">Submit</Button>
        </div>
      </form>
    </Form>
  );
}
