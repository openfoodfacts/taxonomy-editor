import { Box, Button, Typography } from "@mui/material";
import { Link } from "react-router-dom";

export const ProjectNotFound = () => {
  return (
    <Box
      sx={{
        textAlign: "center",
        my: 10,
      }}
    >
      <Typography variant="h3">This project does not exist</Typography>
      <Button component={Link} to="/" sx={{ textDecoration: "none", mt: 10 }}>
        Back To Homepage
      </Button>
    </Box>
  );
};
