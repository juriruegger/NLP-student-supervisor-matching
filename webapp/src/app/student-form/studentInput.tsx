"use client";

import z from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { useToast } from "@/hooks/use-toast";
import { useRouter } from "next/navigation";
import { storeSuggestions } from "./actions";
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

const formSchema = z.object({
  text: z
    .string()
    .min(10, { message: "Your submission must be at least 10 characters" }),
  projectType: z.enum(["specific", "general"]).optional(),
});

export function StudentInput() {
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
    
    await storeSuggestions(data.text, data.projectType);

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
            { loading ? <LoaderCircle className="animate-spin"/> : "Submit" }
          </Button>
        </form>
      </Form>
    </div>
  );
}
