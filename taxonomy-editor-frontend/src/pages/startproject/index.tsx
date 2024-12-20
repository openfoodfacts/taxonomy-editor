import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import {
  Typography,
  Box,
  Grid,
  TextField,
  Snackbar,
  Alert,
  CircularProgress,
  Button,
  InputLabel,
  FormControl,
  Select,
  MenuItem,
  FormHelperText,
} from "@mui/material";

import { TAXONOMY_NAMES } from "@/constants";
import { createBaseURL, toSnakeCase } from "@/utils";
import { useAppContext } from "@/components/UseContext";

const branchNameRegEx = /[^a-z0-9_]+/;

function formatDate(date) {
  const map = {
    mm: ("0" + (date.getMonth() + 1)).slice(-2),
    dd: ("0" + date.getDate()).slice(-2),
    yy: ("0" + date.getFullYear()).slice(-2),
    HH: ("0" + date.getHours()).slice(-2),
    MinMin: ("0" + date.getMinutes()).slice(-2),
  };

  return `${map.mm}${map.dd}${map.yy}_${map.HH}_${map.MinMin}`;
}

export const StartProject = () => {
  const { taxonomyName, setTaxonomyName, ownerName, setOwnerName, description, setDescription } = useAppContext();
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const navigate = useNavigate();

  const findDefaultBranchName = useCallback(() => {
    if (taxonomyName === "" || ownerName === "") return "";
    return `${formatDate(new Date())}_${taxonomyName}_${ownerName}`
      .replace(/[\s-]+/g, "_")
      .toLowerCase();
  }, [ownerName, taxonomyName]);

  const [branchName, setBranchName] = useState(findDefaultBranchName());

  useEffect(() => {
    setBranchName(findDefaultBranchName());
  }, [ownerName, taxonomyName, findDefaultBranchName]);

  useEffect(() => {
    const handleBeforeUnload = (event) => {
      if (taxonomyName.length > 0 || ownerName.length > 0 || description.length > 0) {
        event.preventDefault();
        event.returnValue = "You have unsaved changes. Are you sure you want to leave?";
      }
    };

    window.addEventListener("beforeunload", handleBeforeUnload);

    return () => {
      window.removeEventListener("beforeunload", handleBeforeUnload);
    };
  }, [taxonomyName, ownerName, description]);

  const handleSubmit = () => {
    if (!taxonomyName || !branchName || !ownerName) return;

    const baseUrl = createBaseURL(toSnakeCase(taxonomyName), branchName);
    setLoading(true);
    const dataToBeSent = { description, ownerName };
    let errorMessage = "Unable to import";

    fetch(`${baseUrl}import`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dataToBeSent),
    })
      .then(async (response) => {
        const responseBody = await response.json();
        if (!response.ok) {
          errorMessage = responseBody?.detail ?? "Unable to import";
          throw new Error(errorMessage);
        }
        navigate(`/${toSnakeCase(taxonomyName)}/${branchName}/entry`);
      })
      .catch(() => {
        setErrorMessage(errorMessage);
        setLoading(false);
      });
  };

  const handleCloseErrorSnackbar = () => {
    setErrorMessage("");
  };

  const isInvalidBranchName = branchNameRegEx.test(branchName);

  const handleFieldChange = (setter) => (event) => {
    setter(event.target.value);
  };

  return (
    <>
      <Alert severity="info">
        Feel free to start a new project. Any changes you make will first have
        to be exported and reviewed by the community before being accepted.
        Don&apos;t be scared to test things!
      </Alert>
      <Box>
        <Grid
          container
          direction="column"
          alignItems="center"
          justifyContent="center"
        >
          <Typography sx={{ mt: 4 }} variant="h3">
            Start a project
          </Typography>
          <div>
            <FormControl fullWidth sx={{ width: 265, mt: 4 }}>
              <InputLabel id="taxonomy-name-label">Taxonomy</InputLabel>
              <Select
                labelId="taxonomy-name-label"
                id="taxonomy-name"
                value={taxonomyName}
                label="Taxonomy"
                onChange={handleFieldChange(setTaxonomyName)}
              >
                {TAXONOMY_NAMES.map((taxonomyItem) => (
                  <MenuItem value={taxonomyItem} key={taxonomyItem}>
                    {taxonomyItem}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </div>

          <TextField
            size="small"
            sx={{ width: 265, mt: 2 }}
            onChange={handleFieldChange(setOwnerName)}
            value={ownerName}
            variant="outlined"
            label="Your Name"
            required={true}
          />

          <TextField
            size="small"
            sx={{ width: 265, mt: 2 }}
            onChange={handleFieldChange(setBranchName)}
            value={branchName}
            variant="outlined"
            label="Branch Name"
            required={true}
          />

          <TextField
            sx={{ width: 265, mt: 2 }}
            minRows={4}
            multiline
            onChange={handleFieldChange(setDescription)}
            value={description}
            variant="outlined"
            label="Description"
          />

          <Button
            variant="contained"
            sx={{ mt: 3 }}
            onClick={handleSubmit}
            disabled={
              !branchName || !taxonomyName || loading || isInvalidBranchName
            }
          >
            {loading ? (
              <>
                <CircularProgress size={24} /> Importing Taxonomy...
              </>
            ) : (
              "Submit"
            )}
          </Button>
        </Grid>
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
      </Box>
    </>
  );
};
