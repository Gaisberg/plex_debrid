// routes/Routing.tsx
import React from 'react';
import { Route, Routes } from 'react-router-dom';

// import ConsolePage from '../components/ConsolePage';
import MediaPage from '../pages/MediaPage';
import Dashboard from '../pages/Dashboard';
// import SettingsPage from '../components/ContentPage';

const Routing: React.FC = () => {
  return (
    <Routes>
      {/* <Route path="/console" element={<ConsolePage />} /> */}
      <Route path="/media" element={<MediaPage />} />
      {/* <Route path="/settings" element={<SettingsPage />} /> */}
      <Route path="/" element={<Dashboard />} />
    </Routes>
  );
};

export default Routing;
