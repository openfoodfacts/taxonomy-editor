import CircularProgress from "@mui/material/CircularProgress";
import { useState } from "react";

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
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import AddBoxIcon from "@mui/icons-material/AddBox";
import Dialog from "@mui/material/Dialog";

import useFetch from "@/components/useFetch";
import { createBaseURL } from "@/utils";
import { greyHexCode } from "@/constants";

import CreateNodeDialogContent from "@/components/CreateNodeDialogContent";
import NodesTableBody from "@/components/NodesTableBody";
import { EntryNodeSearchResult } from "@/client";

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
    data: result,
    isPending,
    isError,
    errorMessage,
  } = useFetch<EntryNodeSearchResult>(
    `${baseUrl}nodes/entry?q=${encodeURI(query)}`
  );

  const nodes = result?.nodes;
  const nodeInfos = nodes?.map((node) => {
    return {
      id: node.id,
      is_external: node.isExternal,
    };
  });

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
        height="100%"
      >
        <Box
          sx={{
            flex: 1,
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            marginTop: "1em",
          }}
        >
          <CircularProgress sx={{ textAlign: "center" }} />
        </Box>
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
          Number of nodes found:{" "}
          {`${result?.nodeCount} | pages: ${result?.pageCount}`}
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
            <NodesTableBody
              nodeInfos={nodeInfos ?? []}
              taxonomyName={taxonomyName}
              branchName={branchName}
            />
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
