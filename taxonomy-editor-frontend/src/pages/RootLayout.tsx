import { ResponsiveAppBar } from "@/components/ResponsiveAppBar";
import { TestEnvironmentBanner } from "@/components/TestEnvironmentBanner";
import { Outlet } from "react-router-dom";

export const RootLayout = () => {
  return (
    <>
      <ResponsiveAppBar />
      <TestEnvironmentBanner />
      <Outlet />
    </>
  );
};
