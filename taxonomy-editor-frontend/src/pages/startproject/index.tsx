import { useEffect, useState } from "react";
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
} from "@mui/material";

import { TAXONOMY_NAMES } from "@/constants";
import { createBaseURL, toSnakeCase } from "@/utils";

const branchNameRegEx = /[^a-z0-9_]+/;

const StartProject = ({ clearNavBarLinks }) => {
  const [ownerName, setOwnerName] = useState("");
  const [taxonomyName, setTaxonomyName] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const navigate = useNavigate();

  const findDefaultBranchName = () => {
    if (taxonomyName === "" || ownerName === "") return "";
    return `${taxonomyName.toLowerCase()}_${ownerName
      .replace(" ", "")
      .toLowerCase()}_${Math.floor(Date.now() / 1000)}`;
  };

  const [branchName, setBranchName] = useState(findDefaultBranchName());

  useEffect(
    function cleanMainNavLinks() {
      clearNavBarLinks();
    },
    [clearNavBarLinks]
  );

  useEffect(() => {
    setBranchName(findDefaultBranchName());
  }, [ownerName, taxonomyName]);

  const handleSubmit = () => {
    if (!taxonomyName || !branchName || !ownerName) return;

    const baseUrl = createBaseURL(toSnakeCase(taxonomyName), branchName);
    setLoading(true);
    const dataToBeSent = { description: description, ownerName: ownerName };
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
      })
      .finally(() => setLoading(false));
  };

  const handleCloseErrorSnackbar = () => {
    setErrorMessage("");
  };

  const isInvalidBranchName = branchNameRegEx.test(branchName);

  const isOwnerNameInvalid = (name: string) => {
    if (name === "") return false;
    const pattern = /^[a-zA-Z0-9 _]+$/;
    if (!pattern.test(name)) {
      return true;
    }
    return false;
  };

  return (
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
              onChange={(event) => setTaxonomyName(event.target.value)}
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
          error={isOwnerNameInvalid(ownerName)}
          helperText={
            isOwnerNameInvalid(ownerName) &&
            "Special characters are not allowed"
          }
          size="small"
          sx={{ width: 265, mt: 2 }}
          onChange={(event) => {
            setOwnerName(event.target.value);
          }}
          value={ownerName}
          variant="outlined"
          label="Your Name"
          required={true}
        />

        <TextField
          error={isInvalidBranchName}
          helperText={
            isInvalidBranchName &&
            "Special characters, capital letters and white spaces are not allowed"
          }
          size="small"
          sx={{ width: 265, mt: 2 }}
          onChange={(event) => {
            setBranchName(event.target.value);
          }}
          value={branchName}
          variant="outlined"
          label="Branch Name"
          required={true}
        />

        <TextField
          sx={{ width: 265, mt: 2 }}
          minRows={4}
          multiline
          onChange={(event) => {
            setDescription(event.target.value);
          }}
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
  );
};

export default StartProject;
