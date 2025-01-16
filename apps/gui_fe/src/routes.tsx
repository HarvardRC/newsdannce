import { createHashRouter } from 'react-router-dom';
import RootLayout from './components/Layout';
import Root from './pages/Home';
import MonitorJobs from './pages/MonitorJobsPage';
import CreateRuntimePage from './pages/MakeRuntimePage';
import MakeVideoFolderPage from './pages/MakeVideoFolderPage';
import RuntimesPage from './pages/RuntimesPage';
import VideoFoldersPage from './pages/VideoFoldersPage';
import VideoFolderDetailsPage from './pages/VideoFolderDetailsPage';
import PredictJobDetailsPage from './pages/PredictJobDetailsPage';
import TrainJobDetailsPage from './pages/TrainJobDetailsPage';
import ComTrainPage from './pages/ComTrainPage';
import DannceTrainPage from './pages/DannceTrainPage';
import ComPredictPage from './pages/ComPredictPage';
import PredictionsPage from './pages/PredictionsPage';
import PredictionDetailsPage from './pages/PredictionDetailsPage';
import WeightsPage from './pages/WeightsPage';
import ImportVideoFoldersPage from './pages/ImportVideoFoldersPage';
import DanncePredictPage from './pages/DanncePredictPage';
import TestPage from './pages/TestPage';

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
  makeVideoFolder: {
    path: '/make-video-folder',
    element: <MakeVideoFolderPage />,
    title: 'Make Video Folder',
  },
  // settings: {
  //   path: '/settings',
  //   element: <SettingsPage />,
  //   title: 'Settings',
  // },
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
  models: {
    path: '/weights',
    element: <WeightsPage />,
    title: 'Trained Weights',
  },
  videoFolderDetails: {
    path: '/video-folder/:id',
    element: <VideoFolderDetailsPage />,
    title: 'Video Folder Details',
  },
  importVideoFolderPage: {
    path: '/video-folder/import',
    element: <ImportVideoFoldersPage />,
    title: 'Import Video Folders',
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
  danncePredictPage: {
    path: '/dannce-predict',
    element: <DanncePredictPage />,
    title: 'Predict DANNCE Model',
  },
  predictionsPage: {
    path: '/predictions',
    element: <PredictionsPage />,
    title: 'Predictions',
  },
  predictionDetailsPage: {
    path: '/predictions/:id',
    element: <PredictionDetailsPage />,
    title: 'Prediction Details',
  },
  testPage: {
    path: '/test',
    element: <TestPage />,
    title: 'Test Page',
  },
} as const satisfies Record<string, AppPage>;

export const customRouter = createHashRouter(
  [
    {
      element: <RootLayout />,
      children: [
        {
          path: '/abc',
          element: <div>ABC ROUTE</div>,
        },
        ...Object.values(appPages).map((x) => ({
          path: x.path,
          element: x.element,
        })),
      ],
    },
  ],
  {
    // basename: import.meta.env.GUI_APP_URL,
  }
);
// export const customRouter = createBrowserRouter(
//   [
//     {
//       element: <RootLayout />,
//       children: [
//         {
//           path: '/abc',
//           element: <div>ABC ROUTE</div>,
//         },
//         ...Object.values(appPages).map((x) => ({
//           path: x.path,
//           element: x.element,
//         })),
//       ],
//     },
//   ]
//   // {
//   //   basename: import.meta.env.BASE_URL,
//   // }
// );

console.log('IMPORTED BASENAME', import.meta.env.BASE_URL);
console.log('ROUTER BASENAME', customRouter.basename);
// console.log('BASENAME SHOULD BE', process.env.GUI_APP_URL);

export const headerLinks: AppPage[] = [
  appPages.runtimes,
  appPages.videoFolders,
  appPages.monitorJobs,
  // appPages.settings,
  appPages.predictionsPage,
];

export const homePages = [
  appPages.comTrainPage,
  appPages.comPredictPage,
  appPages.dannceTrainPage,
  appPages.danncePredictPage,
  appPages.monitorJobs,
];
