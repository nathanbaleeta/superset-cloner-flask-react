import React from "react";
import DashboardIcon from '@mui/icons-material/Dashboard';
import { Outlet } from 'react-router';
import { ReactRouterAppProvider } from '@toolpad/core/react-router';
import type { Navigation } from '@toolpad/core/AppProvider';

import CssBaseline from '@mui/material/CssBaseline';
import { CssVarsProvider as JoyCssVarsProvider } from '@mui/joy/styles';
import {
  createTheme,
  ThemeProvider,
  THEME_ID as MATERIAL_THEME_ID,
} from '@mui/material/styles';

const NAVIGATION: Navigation = [
  {
    kind: 'header',
    title: 'Main items',
  },
  {
    title: 'Dashboard',
    icon: <DashboardIcon />,
  },
];

const BRANDING = {
  title: "Dashboard Cloner",
};




// https://mui.com/joy-ui/integrations/material-ui/
const materialTheme = createTheme();

export default function App() {

  
  return (
    <ReactRouterAppProvider navigation={NAVIGATION} branding={BRANDING}>
     <ThemeProvider theme={{ [MATERIAL_THEME_ID]: materialTheme }}>
      <JoyCssVarsProvider>
        <CssBaseline enableColorScheme />
            <Outlet />
      </JoyCssVarsProvider>
    </ThemeProvider>
    </ReactRouterAppProvider>
  );
}