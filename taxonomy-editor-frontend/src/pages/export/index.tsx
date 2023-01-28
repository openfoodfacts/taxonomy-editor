import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";

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

import { createBaseURL } from "../editentry/createURL";

type Props = {
  addNavLinks: () => void;
};

const ExportTaxonomy = ({ addNavLinks }: Props) => {
  const [isCreatingGithubPR, setIsCreatingGithubPR] = useState(false);
  const [pullRequestURL, setPullRequestURL] = useState("");
  const [isDownloadingFile, setIsDownloadingFile] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const { taxonomyName, branchName } = useParams();
  const baseURL = createBaseURL(taxonomyName, branchName);

  useEffect(
    function defineMainNavLinks() {
      if (!branchName || !taxonomyName) return;

      addNavLinks({ branchName, taxonomyName });
    },
    [taxonomyName, branchName, addNavLinks]
  );

  const handleDownload = () => {
    setIsDownloadingFile(true);
    setErrorMessage("");

    fetch(`${baseURL}downloadexport`, {
      method: "GET",
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Unable to download file");
        }
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
        setErrorMessage("Unable to download file");
      })
      .finally(() => {
        setIsDownloadingFile(false);
      });
  };

  const handleGithub = () => {
    setIsCreatingGithubPR(true);
    setErrorMessage("");
    setPullRequestURL("");

    fetch(`${baseURL}githubexport`, {
      method: "GET",
    })
      .then(async (response) => {
        const responseBody = await response.json();
        if (!response.ok) {
          throw new Error(responseBody?.detail ?? "Unable to export to Github");
        } else {
          setPullRequestURL(responseBody);
        }
      })
      .catch(() => {
        setErrorMessage("Unable to export to Github");
      })
      .finally(() => {
        setIsCreatingGithubPR(false);
      });
  };

  const handleCloseErrorSnackbar = () => {
    setErrorMessage("");
  };

  const handleClosePullRequestDialog = () => {
    setPullRequestURL("");
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
          disabled={isDownloadingFile}
          variant="contained"
          onClick={handleDownload}
          sx={{ mt: 4, width: "150px" }}
        >
          {isDownloadingFile ? <CircularProgress size={24} /> : "Download"}
        </Button>
        <Typography
          sx={{ mt: 10, flexGrow: 1, textAlign: "center" }}
          variant="h5"
        >
          Click the button below to create a Pull Request to Github
        </Typography>
        <Button
          startIcon={<GitHubIcon />}
          disabled={isCreatingGithubPR}
          variant="contained"
          onClick={handleGithub}
          sx={{ mt: 4, width: "230px" }}
        >
          {isCreatingGithubPR ? (
            <CircularProgress size={24} />
          ) : (
            "Create Pull Request"
          )}
        </Button>
      </Grid>

      {/* Snackbar to show errors */}
      <Snackbar
        anchorOrigin={{ vertical: "top", horizontal: "right" }}
        open={errorMessage.length > 0}
        autoHideDuration={6000}
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
      <Dialog open={pullRequestURL.length > 0}>
        <DialogTitle>Your pull request has been created!</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Thank you for contributing! A maintainer will review your changes
            soon.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClosePullRequestDialog}>Cancel</Button>
          <Button component={MuiLink} href={pullRequestURL}>
            Go to PR
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
export default ExportTaxonomy;
