'use client'

import { useState } from 'react'
import { ThemeProvider } from 'next-themes'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { WebSocketProvider } from '@/hooks/useWebSocket'

export function Providers({ children }: { children: React.ReactNode }) {
  // Create QueryClient instance
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 5000, // Data is fresh for 5 seconds
        refetchOnWindowFocus: true,
        refetchOnReconnect: true,
        retry: 3,
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      },
      mutations: {
        retry: 1,
      },
    },
  }))

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider
        attribute="class"
        defaultTheme="dark"
        enableSystem
        disableTransitionOnChange
      >
        <WebSocketProvider>
          {children}
        </WebSocketProvider>
      </ThemeProvider>
    </QueryClientProvider>
  )
}
