"use client";

import { Sidebar } from "@/components/features/sidebar";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <div className="container max-w-5xl py-8 px-6">{children}</div>
      </main>
    </div>
  );
}
