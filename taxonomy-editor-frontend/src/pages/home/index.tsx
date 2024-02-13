import { Link } from "react-router-dom";

import Button from "@mui/material/Button";
import { Link as MuiLink } from "@mui/material";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Stack from "@mui/material/Stack";
import Container from "@mui/material/Container";
import logoUrl from "@/assets/logo.png";
import classificationImgUrl from "@/assets/classification.png";
import { ResponsiveAppBar } from "@/components/ResponsiveAppBar";

export const Home = () => {
  return (
    <>
      <ResponsiveAppBar displayedPages={[]} />
      <Container component="main" maxWidth="md">
        <Box
          sx={{
            marginTop: 4,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          <Box
            component="img"
            height={140}
            width={700}
            src={logoUrl}
            alt="Open Food Facts Logo"
          />
          <Box sx={{ mt: 1 }} />
          <Box
            component="img"
            width={128}
            height={128}
            src={classificationImgUrl}
            alt="Classification Logo"
          />
          <Typography sx={{ mt: 4, mb: 6 }} variant="h2">
            Taxonomy Editor
          </Typography>
          <Stack direction="row" alignItems="center">
            <Button
              variant="contained"
              component={Link}
              to="startproject"
              sx={{ textDecoration: "none", mb: 2, mr: 4 }}
            >
              Create new project
            </Button>
            <Button
              variant="contained"
              component={Link}
              to="gotoproject"
              sx={{ textDecoration: "none", mb: 2 }}
            >
              Open existing project
            </Button>
          </Stack>
        </Box>
        <Typography
          variant="body2"
          color="text.secondary"
          align="center"
          sx={{ mt: 8, mb: 4 }}
        >
          {"Copyright © "}
          <MuiLink color="inherit" href="https://world.openfoodfacts.org/">
            Open Food Facts
          </MuiLink>{" "}
          {new Date().getFullYear()}
          {"."}
        </Typography>
      </Container>
    </>
  );
};
