import { CheckCheck, Home, LetterText, Settings } from "lucide-react";

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarSeparator,
} from "@/components/ui/sidebar";
import { NavUser } from "./nav-user";
import { currentUser } from "@clerk/nextjs/server";
import Link from "next/link";
import Image from "next/image";

/**
 * Main navigation items for the application sidebar.
 */
const items = [
  {
    title: "Home",
    url: "/",
    icon: Home,
  },
  {
    title: "Student form",
    url: "/student-form",
    icon: LetterText,
  },
  {
    title: "Suggestions",
    url: "/suggestions",
    icon: CheckCheck,
  },
];

const settings = [
  {
    title: "Settings",
    url: "/settings",
    icon: Settings,
  },
];

export async function AppSidebar() {
  const user = await currentUser();

  return (
    <Sidebar collapsible="icon" variant="inset">
      <SidebarHeader>
        <Link href="/" >
          <Image
            src="https://i.ibb.co/zV62nj6Q/May-18-2025-Optimizing-Modern-BERT-API.png"
            alt="Logo"
            width={32}
            height={32}
            className="rounded-xl mt-1.5"
          />
        </Link>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {items.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <a href={item.url}>
                      <item.icon />
                      <span>{item.title}</span>
                    </a>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
        <SidebarSeparator />
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {settings.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <a href={item.url}>
                      <item.icon />
                      <span>{item.title}</span>
                    </a>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter>
        <NavUser userEmail={user?.primaryEmailAddress?.emailAddress} />
      </SidebarFooter>
    </Sidebar>
  );
}
