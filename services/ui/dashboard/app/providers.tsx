'use client'

import { ThemeProvider } from 'next-themes'
import { SWRConfig } from 'swr'
import { SocketProvider } from '@/lib/socket'

const fetcher = async (url: string) => {
  const res = await fetch(url)
  if (!res.ok) {
    throw new Error('Failed to fetch')
  }
  return res.json()
}

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="dark"
      enableSystem
      disableTransitionOnChange
    >
      <SWRConfig
        value={{
          fetcher,
          refreshInterval: 5000, // Refresh every 5 seconds
          revalidateOnFocus: true,
          revalidateOnReconnect: true,
          errorRetryCount: 3,
          errorRetryInterval: 1000,
        }}
      >
        <SocketProvider>
          {children}
        </SocketProvider>
      </SWRConfig>
    </ThemeProvider>
  )
}
