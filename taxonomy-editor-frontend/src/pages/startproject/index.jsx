import {
  Typography,
  Box,
  Grid,
  TextField,
  Stack,
  Autocomplete,
  Snackbar,
  Alert,
  CircularProgress,
  Button,
} from "@mui/material";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { TAXONOMY_NAMES } from "../../constants";
import { createBaseURL } from "../editentry/createURL";
import { toSnakeCase } from "../../components/interConvertNames";

const StartProject = () => {
  const [branchName, setBranchName] = useState("");
  const [taxonomyName, setTaxonomyName] = useState(null);
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = () => {
    const baseUrl = createBaseURL(taxonomyName, branchName);
    setLoading(true);
    const dataToBeSent = { description: description };
    fetch(baseUrl + "import", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dataToBeSent),
    })
      .then(async (response) => {
        const responseBody = await response.json();
        if (!response.ok && responseBody.detail) {
          throw new Error(responseBody.detail);
        }
        navigate(`/${taxonomyName}/${branchName}/entry`);
      })
      .catch((detail) => {
        setErrorMessage("Unable to import");
        setLoading(false);
      });
  };
  const handleClose = () => {
    setErrorMessage(null);
  };
  const LoadingButton = (props) => {
    const { onClick, loading, text, sx } = props;
    return (
      <Button variant="contained" sx={sx} onClick={onClick} disabled={loading}>
        {loading && <CircularProgress size={24} />}
        {!loading && text}
      </Button>
    );
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
        <Stack sx={{ mt: 4, mb: 4 }} direction="row" alignItems="center">
          <Typography sx={{ mr: 4 }} variant="h5">
            Taxonomy Name
          </Typography>
          <Autocomplete
            sx={{ width: 265 }}
            options={TAXONOMY_NAMES}
            onChange={(e, selectedTaxonomy) => {
              if (selectedTaxonomy)
                setTaxonomyName(toSnakeCase(selectedTaxonomy));
              else setTaxonomyName(null);
            }}
            renderInput={(params) => <TextField {...params} />}
          ></Autocomplete>
        </Stack>
        <Stack direction="row" alignItems="center">
          <Typography sx={{ mr: 8 }} variant="h5">
            Branch Name
          </Typography>
          <TextField
            size="small"
            sx={{ width: 265 }}
            onChange={(event) => {
              setBranchName(event.target.value);
            }}
            value={branchName}
            variant="outlined"
          />
        </Stack>
        <Stack sx={{ mt: 4 }} direction="row" alignItems="center">
          <Typography sx={{ mr: 10 }} variant="h5">
            Description
          </Typography>
          <TextField
            sx={{ width: 265 }}
            minRows={4}
            multiline
            onChange={(event) => {
              setDescription(event.target.value);
            }}
            value={description}
            variant="outlined"
          />
        </Stack>
        {/* Button for submitting edits */}
        <LoadingButton
          loading={loading}
          disabled={!branchName || !taxonomyName}
          onClick={handleSubmit}
          sx={{ mt: 4, width: 130 }}
          text="Submit"
        ></LoadingButton>
      </Grid>
      <Snackbar
        anchorOrigin={{ vertical: "top", horizontal: "right" }}
        open={!!errorMessage}
        autoHideDuration={3000}
        onClose={handleClose}
      >
        <Alert
          elevation={6}
          variant="filled"
          onClose={handleClose}
          severity="error"
        >
          {errorMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default StartProject;
