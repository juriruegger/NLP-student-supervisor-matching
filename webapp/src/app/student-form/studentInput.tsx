"use client";

import z from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
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
import { useToast } from "@/hooks/use-toast";
import { useRouter } from "next/navigation";
import { storeSuggestions } from "./actions";

const formSchema = z.object({
  text: z
    .string()
    .min(10, { message: "Your submission must be at least 10 characters" }),
});

export function StudentInput() {
  const router = useRouter();
  const { toast } = useToast();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
  });

  function onSubmit(data: z.infer<typeof formSchema>) {
    storeSuggestions(data.text);

    toast({
      title: `Form submitted, calculating suggestions`,
    });

    router.push(`/suggestions`);
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="text"
          render={({ field }) => (
            <FormItem className="shadow-md focus-within:shadow-lg p-2 transition-shadow duration-300 rounded-2xl dark:border-0 border">
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
