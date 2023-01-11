import {
  Box,
  Grid,
  Typography,
  Alert,
  Snackbar,
  Button,
  Link as MuiLink,
  CircularProgress,
} from "@mui/material";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import DownloadIcon from "@mui/icons-material/Download";
import GitHubIcon from "@mui/icons-material/GitHub";
import { useParams } from "react-router-dom";
import { createBaseURL } from "../editentry/createURL";
import { useState, useEffect } from "react";

const ExportTaxonomy = ({ setDisplayedPages }) => {
  const { taxonomyName, branchName } = useParams();
  const urlPrefix = `${taxonomyName}/${branchName}/`;
  const baseURL = createBaseURL(taxonomyName, branchName);

  const [loadingForDownload, setLoadingForDownload] = useState(false);
  const [loadingForGithub, setLoadingForGitHub] = useState(false);
  const [openSuccessDialog, setOpenSuccessDialog] = useState(false);
  const [pullRequestURL, setPullRequestURL] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  // Set url prefix for navbar component
  useEffect(() => {
    setDisplayedPages([
      { url: urlPrefix + "entry", translationKey: "Nodes" },
      { url: urlPrefix + "search", translationKey: "Search" },
      { url: urlPrefix + "export", translationKey: "Export" },
    ]);
  }, [urlPrefix, setDisplayedPages]);

  const handleDownload = () => {
    setLoadingForDownload(true);
    fetch(baseURL + "downloadexport", {
      method: "GET",
    })
      .then((response) => {
        return response.blob();
      })
      .then((blob) => {
        // Download taxonomy without opening in browser
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = taxonomyName + ".txt"; // Setting filename
        a.click();
        a.remove(); // Virtual click for download
        URL.revokeObjectURL(url);
      })
      .catch(() => {
        setErrorMessage("Download failed!");
      })
      .finally(() => {
        setLoadingForDownload(false);
      });
  };

  const handleGithub = () => {
    setLoadingForGitHub(true);
    fetch(baseURL + "githubexport", {
      method: "GET",
    })
      .then(async (response) => {
        const responseBody = await response.json();
        if (!response.ok && responseBody.detail) {
          throw new Error(responseBody.detail);
        } else {
          setPullRequestURL(responseBody);
          setOpenSuccessDialog(true);
        }
      })
      .catch((detail) => {
        setErrorMessage("Unable to export to Github!");
      })
      .finally(() => {
        setLoadingForGitHub(false);
      });
  };

  const handleCloseErrorSnackbar = () => {
    setErrorMessage(null);
  };
  const handleCloseSuccessDialog = () => {
    setOpenSuccessDialog(false);
  };

  return (
    <Box>
      <Grid
        container
        direction="column"
        alignItems="center"
        justifyContent="center"
      >
        <Typography
          sx={{ mt: 4, flexGrow: 1, textAlign: "center" }}
          variant="h3"
        >
          Export Taxonomy
        </Typography>
        <Typography
          sx={{ mt: 8, flexGrow: 1, textAlign: "center" }}
          variant="h5"
        >
          Click the button below to download your edited taxonomy
        </Typography>
        <Button
          startIcon={<DownloadIcon />}
          disabled={loadingForDownload}
          variant="contained"
          onClick={handleDownload}
          sx={{ mt: 4, width: "150px" }}
        >
          {loadingForDownload ? <CircularProgress size={24} /> : "Download"}
        </Button>
        <Typography
          sx={{ mt: 10, flexGrow: 1, textAlign: "center" }}
          variant="h5"
        >
          Click the button below to create a Pull Request to Github
        </Typography>
        <Button
          startIcon={<GitHubIcon />}
          disabled={loadingForGithub}
          variant="contained"
          onClick={handleGithub}
          sx={{ mt: 4, width: "230px" }}
        >
          {loadingForGithub ? (
            <CircularProgress size={24} />
          ) : (
            "Create Pull Request"
          )}
        </Button>
      </Grid>
      {/* Snackbar to show errors */}
      <Snackbar
        anchorOrigin={{ vertical: "top", horizontal: "right" }}
        open={!!errorMessage}
        autoHideDuration={3000}
        onClose={handleCloseErrorSnackbar}
      >
        <Alert
          elevation={6}
          variant="filled"
          onClose={handleCloseErrorSnackbar}
          severity="error"
        >
          {errorMessage}
        </Alert>
      </Snackbar>
      {/* Dialog box for acknowledgement the creation of a pull request */}
      <Dialog open={openSuccessDialog}>
        <DialogTitle>Your pull request has been created!</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Thank you for contributing! A maintainer will review your changes
            soon.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseSuccessDialog}>Cancel</Button>
          <Button component={MuiLink} href={pullRequestURL} autoFocus>
            Go to PR
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
export default ExportTaxonomy;
