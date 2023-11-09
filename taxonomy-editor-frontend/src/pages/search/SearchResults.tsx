import CircularProgress from "@mui/material/CircularProgress";
import { useState } from "react";
import { Link } from "react-router-dom";

import {
  Typography,
  Snackbar,
  Alert,
  Box,
  Grid,
  Stack,
  IconButton,
  Paper,
} from "@mui/material";
import Container from "@mui/material/Container";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import EditIcon from "@mui/icons-material/Edit";
import AddBoxIcon from "@mui/icons-material/AddBox";
import Dialog from "@mui/material/Dialog";

import useFetch from "../../components/useFetch";
import { createBaseURL } from "../../utils";
import { greyHexCode } from "../../constants";
import type { SearchAPIResponse } from "../../backend-types/types";
import CreateNodeDialogContent from "../../components/CreateNodeDialogContent";

type Props = {
  query: string;
  taxonomyName: string;
  branchName: string;
};

const SearchResults = ({ query, taxonomyName, branchName }: Props) => {
  const [openNewNodeDialog, setOpenNewNodeDialog] = useState(false);
  const [showNewNodeSuccess, setShowNewNodeSuccess] = useState(false);

  const baseUrl = createBaseURL(taxonomyName, branchName);
  const {
    data: nodeIds,
    isPending,
    isError,
    errorMessage,
  } = useFetch<SearchAPIResponse>(`${baseUrl}search?query=${encodeURI(query)}`);

  const handleCloseAddDialog = () => {
    setOpenNewNodeDialog(false);
  };

  const handleCloseSuccessSnackbar = () => {
    setShowNewNodeSuccess(false);
  };

  // Displaying errorMessages if any
  if (isError) {
    return (
      <Container component="main" maxWidth="xs">
        <Grid
          container
          direction="column"
          alignItems="center"
          justifyContent="center"
        >
          <Typography sx={{ mt: 2 }} variant="h5">
            {errorMessage}
          </Typography>
        </Grid>
      </Container>
    );
  }

  // Loading...
  if (isPending) {
    return (
      <Grid
        container
        direction="column"
        alignItems="center"
        justifyContent="center"
      >
        <Typography sx={{ mt: 2 }} variant="h5">
          <CircularProgress/>
        </Typography>
      </Grid>
    );
  }

  return (
    <Box>
      <Grid
        container
        direction="column"
        alignItems="center"
        justifyContent="center"
      >
        <Grid item xs={3} sx={{ mt: 4 }}>
          <Typography variant="h4">Search Results</Typography>
        </Grid>
        <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>
          Number of nodes found: {(nodeIds ?? []).length}
        </Typography>
        {/* Table for listing all nodes in taxonomy */}
        <TableContainer sx={{ width: 375 }} component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <Stack direction="row" alignItems="center">
                  <TableCell align="left">
                    <Typography variant="h6">Nodes</Typography>
                  </TableCell>
                  <IconButton
                    sx={{ ml: 1, color: greyHexCode }}
                    onClick={() => {
                      setOpenNewNodeDialog(true);
                    }}
                  >
                    <AddBoxIcon />
                  </IconButton>
                </Stack>
                <TableCell align="left">
                  <Typography variant="h6">Action</Typography>
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {(nodeIds ?? []).map((nodeId) => (
                <TableRow key={nodeId}>
                  <TableCell align="left" component="td" scope="row">
                    <Typography variant="subtitle1">{nodeId}</Typography>
                  </TableCell>
                  <TableCell align="left" component="td" scope="row">
                    <IconButton
                      component={Link}
                      to={`/${taxonomyName}/${branchName}/entry/${nodeId}`}
                      aria-label="edit"
                    >
                      <EditIcon color="primary" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Dialog box for adding nodes */}
        <Dialog open={openNewNodeDialog} onClose={handleCloseAddDialog}>
          <CreateNodeDialogContent
            taxonomyName={taxonomyName}
            branchName={branchName}
            onCloseDialog={handleCloseAddDialog}
            onSuccess={() => {
              setOpenNewNodeDialog(false);
              setShowNewNodeSuccess(true);
            }}
          />
        </Dialog>

        {/* Snackbar for acknowledgment of addition of node */}
        <Snackbar
          anchorOrigin={{ vertical: "top", horizontal: "right" }}
          open={showNewNodeSuccess}
          autoHideDuration={3000}
          onClose={handleCloseSuccessSnackbar}
        >
          <Alert
            elevation={6}
            variant="filled"
            onClose={handleCloseSuccessSnackbar}
            severity="success"
          >
            The node has been successfully added!
          </Alert>
        </Snackbar>
      </Grid>
    </Box>
  );
};

export default SearchResults;
