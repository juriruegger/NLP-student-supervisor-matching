import type { Metadata } from "next";
import "./globals.css";
import { ThemeProvider } from "@/components/theme-provider";
import { Toaster } from "@/components/ui/toaster";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/ui/app-sidebar";
import { Card } from "@/components/ui/card";
import { ModeToggle } from "@/components/ui/mode-toggle";
import { ClerkProvider, SignedIn } from "@clerk/nextjs";
import { cookies } from "next/headers";

export const metadata: Metadata = {
  title: "SupervisorMatch",
  description: "An application to match students with supervisors",
};

export default async function Layout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const cookieStore = await cookies();
  const defaultOpen = cookieStore.get("sidebar:state")?.value === "true";

  return (
    <ClerkProvider>
      <html lang="en" suppressHydrationWarning>
        <body>
          <ThemeProvider
            attribute="class"
            defaultTheme="system"
            enableSystem
            disableTransitionOnChange
          >
            <SignedIn>
              <SidebarProvider defaultOpen={defaultOpen}>
                <AppSidebar />
                <div className="grow">
                  <Card className="md:m-2 p-6 bg-backgroundCard grow">
                    <div className="relative min-h-screen">
                      <div className="sticky top-4 left-0 z-10 flex justify-between w-full px-4">
                        <SidebarTrigger className="mt-1.5" />
                        <ModeToggle />
                      </div>
                      <div className="pt-12 pb-20 px-4 md:px-12 lg:px-24 xl:px-52 transition-all ease-out">
                        {children}
                      </div>
                    </div>
                  </Card>
                </div>

                <Toaster />
              </SidebarProvider>
            </SignedIn>
          </ThemeProvider>
        </body>
      </html>
    </ClerkProvider>
  );
}
