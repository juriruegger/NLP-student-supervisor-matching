import { Avatar, AvatarImage } from "@/components/ui/avatar";
import { content } from "../content";
import Image from "next/image";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Check } from "lucide-react";
import { supervisors } from "./supervisors";

export default function Page() {
  return (
    <div>
      <h1 className="text-3xl font-bold">{content.suggestions.title}</h1>

      <div className="mt-12 flex flex-col space-y-12">
        {supervisors.map(
          (supervisor, index) => (
            <div key={index} className="flex items-center space-x-20 w-full">
              <Image
                src={supervisor.image}
                alt={supervisor.name}
                width={100}
                height={100}
                className="rounded-full"
              />
              <div>
                <h2 className="text-xl font-bold">{supervisor.name}</h2>
                <p>{supervisor.field}</p>
              </div>
              <Link href={supervisor.website}>
                <Button variant={'secondary'} disabled={supervisor.contacted}>Set up a meeting</Button>
              </Link>
              {supervisor.contacted && <Check size={32} />}
            </div>
          )
        )}
      </div>
    </div>
  );
}
