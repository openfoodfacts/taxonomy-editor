import { Alert, AlertTitle, Box, Link } from "@mui/material";

export const TestEnvironmentBanner: React.FC = () => {
  // Check if we're on the .net (test) environment
  // For local testing, temporarily add: || window.location.hostname.includes("localhost")
  const isTestEnvironment = window.location.hostname.includes(".net");

  if (!isTestEnvironment) {
    return null;
  }

  return (
    <Box sx={{ width: "100%", position: "sticky", top: 0, zIndex: 1100 }}>
      <Alert severity="warning" sx={{ borderRadius: 0 }}>
        <AlertTitle>Test Environment</AlertTitle>
        You are using the TEST environment (.net). Changes made here will NOT be
        saved to the production database. Use{" "}
        <Link
          href="https://ui.taxonomy.openfoodfacts.org"
          target="_blank"
          rel="noopener noreferrer"
          sx={{ fontWeight: "bold", color: "inherit", textDecoration: "underline" }}
        >
          taxonomy.openfoodfacts.org
        </Link>{" "}
        for real edits.
      </Alert>
    </Box>
  );
};
