import type { Metadata } from "next";
import "./globals.css";
import { ThemeProvider } from "@/components/theme-provider";
import { Toaster } from "@/components/ui/toaster";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/ui/app-sidebar";
import { Card } from "@/components/ui/card";
import { ModeToggle } from "@/components/ui/mode-toggle";

export const metadata: Metadata = {
  title: "SSM",
  description: "An application to match students with supervisors",
  icons: {
    icon: "https://i.ibb.co/q0vwRGg/realistic-animal2.webp",
  },
};

export default function Layout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <SidebarProvider>
            <AppSidebar />
            <main style={{ flexGrow: 1 }}>
              <Card
                className="md:m-2 h-full p-6 card-full-height bg-backgroundCard"
                style={{ height: "98%" }}
              >
                <div className="relative h-screen">
                  <div className="sticky top-4 left-0 z-10 flex justify-between w-full px-4">
                    <SidebarTrigger className="mt-1.5" />
                    <ModeToggle />
                  </div>
                  <div className="mt-12 mx-4 md:mx-12 lg:mx-24 xl:mx-52 transition-all ease-out">
                    {children}
                  </div>
                </div>
              </Card>
            </main>

            <Toaster />
          </SidebarProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
