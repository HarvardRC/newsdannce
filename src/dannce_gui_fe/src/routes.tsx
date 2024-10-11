import { createBrowserRouter } from 'react-router-dom';
import RootLayout from './components/Layout';
import Root from './pages/Home';
import SettingsPage from './pages/SettingsPage';
import MonitorJobs from './pages/MonitorJobsPage';
import CreateRuntimePage from './pages/MakeRuntimePage';
import MakeVideoFolderPage from './pages/MakeVideoFolderPage';
import RuntimesPage from './pages/RuntimesPage';
import MakeTrainingFolderPage from './pages/MakeTrainingFolderPage';
import TrainingFoldersPage from './pages/TrainingFoldersPage';
import VideoFoldersPage from './pages/VideoFoldersPage';
import VideoFolderDetailsPage from './pages/VideoFolderDetailsPage';
import PredictJobDetailsPage from './pages/PredictJobDetailsPage';
import TrainJobDetailsPage from './pages/TrainJobDetailsPage';
import ComTrainPage from './pages/ComTrainPage';
import DannceTrainPage from './pages/DannceTrainPage';
import ComPredictPage from './pages/ComPredictPage';
import PredictionsPage from './pages/PredictionsPage';

type AppPage = {
  path: string;
  element: JSX.Element;
  title: string;
};

export const appPages = {
  root: {
    path: '/',
    element: <Root />,
    title: 'Home',
  },
  makeTrainingFolder: {
    path: '/make-training-folder',
    element: <MakeTrainingFolderPage />,
    title: 'Make Training Folder',
  },
  makeVideoFolder: {
    path: '/make-video-folder',
    element: <MakeVideoFolderPage />,
    title: 'Make Video Folder',
  },
  settings: {
    path: '/settings',
    element: <SettingsPage />,
    title: 'Settings',
  },
  monitorJobs: {
    path: '/jobs',
    element: <MonitorJobs />,
    title: 'Monitor Jobs',
  },
  runtimes: {
    path: '/runtimes',
    element: <RuntimesPage />,
    title: 'Runtimes',
  },
  makeRuntime: {
    path: '/make-runtime',
    element: <CreateRuntimePage />,
    title: 'Create Runtime',
  },
  videoFolders: {
    path: '/video-folders',
    element: <VideoFoldersPage />,
    title: 'Video Folders',
  },
  trainingFolders: {
    path: '/training-folders',
    element: <TrainingFoldersPage />,
    title: 'Train Folders',
  },
  models: {
    path: '/models',
    element: <TrainingFoldersPage />,
    title: 'Models',
  },
  videoFolderDetails: {
    path: '/video-folder/:id',
    element: <VideoFolderDetailsPage />,
    title: 'Video Folder Details',
  },
  predictJobDetails: {
    path: '/predict-job/:id',
    element: <PredictJobDetailsPage />,
    title: 'Predict Job Details',
  },
  trainJobDetails: {
    path: '/train-job/:id',
    element: <TrainJobDetailsPage />,
    title: 'Train Job Details',
  },
  comTrainPage: {
    path: '/com-train',
    element: <ComTrainPage />,
    title: 'Train COM Model',
  },
  comPredictPage: {
    path: '/com-predict',
    element: <ComPredictPage />,
    title: 'Predict COM Model',
  },
  dannceTrainPage: {
    path: '/dannce-train',
    element: <DannceTrainPage />,
    title: 'Train DANNCE Model',
  },
  predictionsPage: {
    path: 'predictions/:id',
    element: <PredictionsPage />,
    title: 'Predictions',
  },
} as const satisfies Record<string, AppPage>;

export const customRouter = createBrowserRouter([
  {
    element: <RootLayout />,
    children: Object.values(appPages).map((x) => ({
      path: x.path,
      element: x.element,
    })),
  },
]);

export const headerLinks: AppPage[] = [
  appPages.runtimes,
  appPages.videoFolders,
  appPages.monitorJobs,
  appPages.settings,
  appPages.predictionsPage,
];

export const homePages = [
  appPages.comTrainPage,
  appPages.comPredictPage,
  appPages.dannceTrainPage,
  appPages.monitorJobs,
];
