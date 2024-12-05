import './index.css';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { RouterProvider } from 'react-router-dom';
import { Toaster } from '@/components/ui/sonner';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import { customRouter } from './routes';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
    },
  },
});

// console.log("HOME PAGE URL IS" , )
(window as any).remix_router = customRouter;

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Toaster duration={5000} />
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={customRouter} />
    </QueryClientProvider>
  </StrictMode>
);
