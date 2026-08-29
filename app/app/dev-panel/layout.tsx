import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Dev Panel | Donglyn",
  description: "Developer dashboard",
};

export default function DevPanelLayout({ children }: { children: React.ReactNode }) {
  return children;
}
