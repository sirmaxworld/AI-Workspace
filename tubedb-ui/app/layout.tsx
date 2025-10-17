import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'TubeDB UI - Quality Assurance Dashboard',
  description: 'Internal QA dashboard for video transcript analysis',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-gradient-to-br from-slate-50 via-gray-50 to-blue-50 min-h-screen`}>{children}</body>
    </html>
  )
}
