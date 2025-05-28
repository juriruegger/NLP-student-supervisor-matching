"use client";

import { SidebarMenu, SidebarMenuItem } from "@/components/ui/sidebar";
import { SignedIn, SignedOut, SignInButton, UserButton } from "@clerk/nextjs";

type NavUserProps = {
  userEmail: string | null | undefined;
};

export function NavUser({ userEmail }: NavUserProps) {
  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <div className="flex items-center space-x-2">
          <SignedOut>
            <SignInButton />
          </SignedOut>
          <SignedIn>
            <div className="flex mx-0.5">
              <UserButton
                appearance={{
                  layout: {
                    shimmer: false,
                  },
                }}
              />
            </div>
            <div className="grid flex-1 text-left text-sm leading-tight">
              <span className="truncate font-semibold">{userEmail}</span>
            </div>
          </SignedIn>
        </div>
      </SidebarMenuItem>
    </SidebarMenu>
  );
}
