import { ResponsiveAppBar } from "@/components/ResponsiveAppBar";
import { Box, Button, Typography } from "@mui/material";
import { Link } from "react-router-dom";

export const PageNotFound = () => {
  return (
    <>
      <ResponsiveAppBar displayedPages={[]} />
      <Box
        sx={{
          textAlign: "center",
          my: 10,
        }}
      >
        <Typography variant="h3">Page not found</Typography>
        <Button component={Link} to="/" sx={{ textDecoration: "none", mt: 10 }}>
          Back To Homepage
        </Button>
      </Box>
    </>
  );
};
