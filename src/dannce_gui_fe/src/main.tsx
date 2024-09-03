import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
// import App from './App.tsx'
import {
  createBrowserRouter,
  RouterProvider
} from "react-router-dom"
import './index.css'
import Root from './pages/Home';
import SubmitJobPage from './pages/SubmitJobPage';
import MakeTrainingDirPage from './pages/MakeTrainingDirPage';
import MonitorJobs from './pages/MonitorJobsPage';
import { Toaster } from '@/components/ui/sonner';
import {
  QueryClient,
  QueryClientProvider,
  useQuery,
} from '@tanstack/react-query'

const router = createBrowserRouter([
  {
    path: "/",
    element: <Root />
  },
  {
    path: "/make-training-dir",
    element: <MakeTrainingDirPage />
  },
  {
    path: "/submit-job",
    element: <SubmitJobPage />
  },

  {
    path: "/monitor-jobs",
    element: <MonitorJobs />
  }
])

const queryClient = new QueryClient();

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Toaster />
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </StrictMode>,
)
