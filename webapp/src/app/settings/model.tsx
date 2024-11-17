"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useState } from "react";
import { storeModel } from "./actions";

type ModelProps = {
  model: string;
};

export function Model({ model }: ModelProps) {
  const [value, setValue] = useState<string>(model ?? "bert");

  const onChange = (value: string) => {
    setValue(value);
    storeModel(value);
  };

  return (
    <Select value={value} onValueChange={onChange}>
      <SelectTrigger className="w-[180px]">
        <SelectValue placeholder="Bert model" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="bert">Bert</SelectItem>
        <SelectItem value="scibert">SciBert</SelectItem>
      </SelectContent>
    </Select>
  );
}
