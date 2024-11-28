"use client";

import { SidebarMenu, SidebarMenuItem } from "@/components/ui/sidebar";
import { SignedIn, SignedOut, SignInButton, UserButton } from "@clerk/nextjs";

type NavUserProps = {
  username: string | null | undefined;
  userEmail: string | null | undefined;
};

export function NavUser({ username, userEmail }: NavUserProps) {
  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <div className="flex items-center space-x-2">
          <SignedOut>
            <SignInButton />
          </SignedOut>
          <SignedIn>
            <div className="flex px-1.5">
              <UserButton />
            </div>
            <div className="grid flex-1 text-left text-sm leading-tight">
              <span className="truncate font-semibold">{username}</span>
              <span className="truncate text-xs">{userEmail}</span>
            </div>
          </SignedIn>
        </div>
      </SidebarMenuItem>
    </SidebarMenu>
  );
}
