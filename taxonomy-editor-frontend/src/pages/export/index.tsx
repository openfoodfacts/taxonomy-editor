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

import { createBaseURL } from "@/utils";

interface ExportTaxonomyToGithubProps {
  baseURL: string;
  setErrorMessage: (message: string) => void;
}

const ExportTaxonomyToGithub = ({
  baseURL,
  setErrorMessage,
}: ExportTaxonomyToGithubProps) => {
  const [isExportingToGithub, setIsExportingToGithub] = useState(false);
  const [pullRequestURL, setPullRequestURL] = useState("");

  const handleGithub = () => {
    setIsExportingToGithub(true);
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
        setIsExportingToGithub(false);
      });
  };

  const handleClosePullRequestDialog = () => {
    setPullRequestURL("");
  };

  return (
    <>
      <Typography
        sx={{ mt: 10, flexGrow: 1, textAlign: "center" }}
        variant="h5"
      >
        Click the button below to export to Github
      </Typography>
      <Button
        startIcon={<GitHubIcon />}
        disabled={isExportingToGithub}
        variant="contained"
        onClick={handleGithub}
        sx={{ mt: 4, width: "230px" }}
      >
        {isExportingToGithub ? (
          <CircularProgress size={24} />
        ) : (
          "Export to Github"
        )}
      </Button>

      {/* Dialog box to the PR link */}
      <Dialog open={pullRequestURL.length > 0}>
        <DialogTitle>Your changes have been exported to Github!</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Thank you for contributing! A maintainer will review your changes
            soon.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClosePullRequestDialog}>Cancel</Button>
          <Button component={MuiLink} target="_blank" href={pullRequestURL}>
            Go to PR
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

type ExportTaxonomyProps = {
  addNavLinks: ({
    branchName,
    taxonomyName,
  }: {
    branchName: string;
    taxonomyName: string;
  }) => void;
  taxonomyName: string;
  branchName: string;
};

const ExportTaxonomy = ({
  addNavLinks,
  taxonomyName,
  branchName,
}: ExportTaxonomyProps) => {
  const [isDownloadingFile, setIsDownloadingFile] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const baseURL = createBaseURL(taxonomyName, branchName);

  useEffect(
    function defineMainNavLinks() {
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

  const handleCloseErrorSnackbar = () => {
    setErrorMessage("");
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
        <ExportTaxonomyToGithub
          baseURL={baseURL}
          setErrorMessage={setErrorMessage}
        />
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
    </Box>
  );
};

type ExportTaxonomyWrapperProps = {
  addNavLinks: ({
    branchName,
    taxonomyName,
  }: {
    branchName: string;
    taxonomyName: string;
  }) => void;
};

const ExportTaxonomyWrapper = ({ addNavLinks }: ExportTaxonomyWrapperProps) => {
  const { taxonomyName, branchName } = useParams();

  if (!taxonomyName || !branchName)
    return (
      <Typography variant="h3">
        Oops, something went wrong! Please try again later.
      </Typography>
    );

  return (
    <ExportTaxonomy
      addNavLinks={addNavLinks}
      taxonomyName={taxonomyName}
      branchName={branchName}
    />
  );
};
export default ExportTaxonomyWrapper;
