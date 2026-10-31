import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import App from "./App";
import ComparisonDashboard from "./pages/ComparisonDashboard";
import DatasetAnalysis from "./pages/DatasetAnalysis";
import History from "./pages/History";
import Landing from "./pages/Landing";
import Methodology from "./pages/Methodology";
import NewEvaluation from "./pages/NewEvaluation";
import Settings from "./pages/Settings";
import "./styles.css";

const queryClient = new QueryClient();

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      { index: true, element: <Landing /> },
      { path: "new", element: <NewEvaluation /> },
      { path: "analysis", element: <DatasetAnalysis /> },
      { path: "comparisons/:id", element: <ComparisonDashboard /> },
      { path: "history", element: <History /> },
      { path: "methodology", element: <Methodology /> },
      { path: "settings", element: <Settings /> },
    ],
  },
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </React.StrictMode>,
);

