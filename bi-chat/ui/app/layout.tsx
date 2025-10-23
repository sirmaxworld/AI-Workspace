import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BI Intelligence Chat",
  description: "Intelligent chat interface for business intelligence analysis",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
