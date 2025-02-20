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

// Menu items.
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
      <SidebarContent className="mt-1.5">
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
        <NavUser
          username={user?.fullName}
          userEmail={user?.primaryEmailAddress?.emailAddress}
        />
      </SidebarFooter>
    </Sidebar>
  );
}
