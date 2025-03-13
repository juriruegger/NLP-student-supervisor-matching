"use client";

import z from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { useToast } from "@/hooks/use-toast";
import { useRouter } from "next/navigation";
import { storeTextSuggestions, storeTopicSuggestions } from "./actions";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { LoaderCircle } from "lucide-react";
import { SelectTopics } from "./select-topics";
import { Topics } from "@/lib/types";

const formSchema = z.discriminatedUnion("projectType", [
  z.object({
    projectType: z.literal("specific"),
    text: z.string().min(10, "Your submission must be at least 10 characters"),
    topics: z.undefined().optional(),
  }),
  z.object({
    projectType: z.literal("general"),
    text: z.string().optional(),
    topics: z
      .array(
        z.object({
          topicId: z.number(),
          label: z.string(),
          keywords: z.array(z.string()),
        })
      )
      .min(1, "Select at least one topic"),
  }),
  z.object({
    projectType: z.undefined(),
    text: z.string().optional(),
    topics: z.array(z.any()).optional(),
  }),
]);

export function StudentInput({ topics }: { topics: Topics }) {
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const { toast } = useToast();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      projectType: undefined,
    },
  });

  async function onSubmit(data: z.infer<typeof formSchema>) {
    setLoading(true);
    toast({
      title: `Form submitted, calculating suggestions`,
    });

    data.projectType === "specific" &&
      (await storeTextSuggestions({
        projectType: data.projectType,
        text: data.text,
      }));

    data.projectType === "general" &&
      (await storeTopicSuggestions({
        projectType: data.projectType,
        topics: data.topics ?? [],
      }));

    router.push(`/suggestions`);
  }

  return (
    <div className="space-y-6 w-full">
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)}>
          <div className="mb-6 w-full space-y-6">
            <FormField
              control={form.control}
              name="projectType"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Project Type</FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    defaultValue={field.value}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select an option" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="specific">
                        I have a specific project in mind
                      </SelectItem>
                      <SelectItem value="general">
                        I have a general idea
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </FormItem>
              )}
            />
            {form.watch("projectType") === "general" && (
              <FormField
                control={form.control}
                name="topics"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Topics</FormLabel>
                    <FormControl>
                      <SelectTopics topics={topics} value={field.value ?? []} onChange={field.onChange} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            )}
            {form.watch("projectType") === "specific" && (
              <FormField
                control={form.control}
                name="text"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Project details</FormLabel>
                    <div className="shadow-md focus-within:shadow-lg transition-shadow duration-300 rounded-2xl border border-border">
                      <FormControl>
                        <Textarea
                          placeholder="What are your current thoughts for the project? The more detail, the better!"
                          className="resize-none h-80 w-full rounded-2xl bg-input"
                          {...field}
                        />
                      </FormControl>
                    </div>
                    <FormMessage />
                  </FormItem>
                )}
              />
            )}
          </div>
          <Button
            type="submit"
            className="w-full"
            disabled={!form.watch("projectType") || loading}
          >
            {loading ? <LoaderCircle className="animate-spin" /> : "Submit"}
          </Button>
        </form>
      </Form>
    </div>
  );
}
