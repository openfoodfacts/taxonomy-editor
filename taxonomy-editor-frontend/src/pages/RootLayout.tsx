import { ResponsiveAppBar } from "@/components/ResponsiveAppBar";
import { Outlet } from "react-router-dom";

export const RootLayout = () => {
  return (
    <>
      <ResponsiveAppBar />
      <Outlet />
    </>
  );
};
