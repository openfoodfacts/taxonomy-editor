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

import { TAXONOMY_NAMES } from "../../constants";
import { createBaseURL, toSnakeCase } from "../../utils";

const BranchNameRegEx = /[^a-z0-9_]+/;

const StartProject = ({ clearNavBarLinks }) => {
  const [branchName, setBranchName] = useState("");
  const [taxonomyName, setTaxonomyName] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const navigate = useNavigate();

  useEffect(
    function cleanMainNavLinks() {
      clearNavBarLinks();
    },
    [clearNavBarLinks]
  );

  const handleSubmit = () => {
    if (!taxonomyName || !branchName) return;

    const baseUrl = createBaseURL(toSnakeCase(taxonomyName), branchName);
    setLoading(true);
    const dataToBeSent = { description: description };

    fetch(`${baseUrl}import`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dataToBeSent),
    })
      .then(async (response) => {
        const responseBody = await response.json();
        if (!response.ok) {
          throw new Error(responseBody?.detail ?? "Unable to import");
        }
        navigate(`/${toSnakeCase(taxonomyName)}/${branchName}/entry`);
      })
      .catch(() => {
        setErrorMessage("Unable to import");
      })
      .finally(() => setLoading(false));
  };

  const handleCloseErrorSnackbar = () => {
    setErrorMessage("");
  };


  const isValidBranchName = BranchNameRegEx.test(branchName);

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

        <div>
          <TextField
            error={isValidBranchName}
            helperText={isValidBranchName && "Special characters, capital letters and white spaces are not allowed"}
            size="small"
            sx={{ width: 265, mt: 2 }}
            onChange={(event) => {
              setBranchName(event.target.value);
            }}
            value={branchName}
            variant="outlined"
            label="Branch Name"
          />
        </div>

        <div>
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
        </div>

        <Button
          variant="contained"
          sx={{ mt: 3 }}
          onClick={handleSubmit}
          disabled={!branchName || !taxonomyName || loading || isValidBranchName}
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
