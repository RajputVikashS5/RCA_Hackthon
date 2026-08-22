import { createBrowserRouter } from 'react-router-dom'
import { AppShell } from '../components/layout/AppShell'
import { DashboardPage, AnalyzePage, HistoryPage, DetailPage, SimilarPage, HealthPage, SettingsPage } from '../pages/Pages'
export const router = createBrowserRouter([{ element: <AppShell />, children: [{ path: '/', element: <DashboardPage /> }, { path: '/analyze', element: <AnalyzePage /> }, { path: '/incidents', element: <HistoryPage /> }, { path: '/incidents/:id', element: <DetailPage /> }, { path: '/similar', element: <SimilarPage /> }, { path: '/system-health', element: <HealthPage /> }, { path: '/settings', element: <SettingsPage /> }] }])
