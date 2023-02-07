import { useState, useEffect } from "react";
import { Link, useParams } from "react-router-dom";

import {
  Typography,
  Snackbar,
  Alert,
  Box,
  Stack,
  IconButton,
} from "@mui/material";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import EditIcon from "@mui/icons-material/Edit";
import AddBoxIcon from "@mui/icons-material/AddBox";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";

import CreateNodeDialogContent from "./CreateNodeDialogContent";
import useFetch from "../../components/useFetch";
import { createBaseURL } from "../editentry/createURL";
import { toTitleCase } from "../../utils";
import { greyHexCode } from "../../constants";
import type { RootEntriesAPIResponse } from "../../backend-types/types";

type Props = {
  addNavLinks: ({
    taxonomyName,
    branchName,
  }: {
    taxonomyName: string;
    branchName: string;
  }) => void;
};

const RootNodes = ({ addNavLinks }: Props) => {
  const [openCreateNodeDialog, setOpenCreateNodeDialog] = useState(false);
  const [openCreateNodeSuccessSnackbar, setCreateNodeOpenSuccessSnackbar] =
    useState(false);

  const { taxonomyName, branchName } = useParams();
  const baseUrl = createBaseURL(taxonomyName, branchName);

  const {
    data: nodes,
    isPending,
    isError,
    errorMessage,
  } = useFetch<RootEntriesAPIResponse>(`${baseUrl}rootentries`);

  useEffect(
    function defineMainNavLinks() {
      if (!branchName || !taxonomyName) return;

      addNavLinks({ branchName, taxonomyName });
    },
    [taxonomyName, branchName, addNavLinks]
  );

  const handleCloseAddDialog = () => {
    setOpenCreateNodeDialog(false);
  };

  const handleCloseSuccessSnackbar = () => {
    setCreateNodeOpenSuccessSnackbar(false);
  };

  if (isError || !branchName || !taxonomyName) {
    return (
      <Box>
        <Typography variant="h5">{errorMessage}</Typography>
      </Box>
    );
  }

  if (isPending || !nodes) {
    return (
      <Box>
        <Typography variant="h5">Loading...</Typography>
      </Box>
    );
  }

  return (
    <>
      <div>
        <Typography sx={{ mb: 2, mt: 2, ml: 2 }} variant="h4">
          Root Nodes:
        </Typography>

        <TableContainer sx={{ ml: 2, width: 375 }}>
          <Table style={{ border: "solid", borderWidth: 1.5 }}>
            <TableHead>
              <TableCell align="left">
                <Typography variant="h6">Taxonony Name</Typography>
              </TableCell>
              <TableCell align="left">
                <Typography variant="h6">Branch Name</Typography>
              </TableCell>
            </TableHead>
            <TableBody>
              <TableCell align="left" component="td" scope="row">
                <Typography variant="body1">
                  {toTitleCase(taxonomyName ?? "")}
                </Typography>
              </TableCell>
              <TableCell align="left" component="td" scope="row">
                <Typography variant="body1">{branchName}</Typography>
              </TableCell>
            </TableBody>
          </Table>
        </TableContainer>

        <Typography variant="h6" sx={{ mt: 2, ml: 2, mb: 1 }}>
          Number of root nodes in taxonomy: {nodes.length}
        </Typography>

        {/* Table for listing all nodes in taxonomy */}
        <TableContainer sx={{ ml: 2, width: 375 }}>
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
                      setOpenCreateNodeDialog(true);
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
              {nodes.map((node) => (
                <TableRow key={node[0].id}>
                  <TableCell align="left" component="td" scope="row">
                    <Typography variant="subtitle1">{node[0].id}</Typography>
                  </TableCell>
                  <TableCell align="left" component="td" scope="row">
                    <IconButton
                      component={Link}
                      to={`${node[0].id}`}
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
      </div>

      {/* Dialog box for adding nodes */}
      <Dialog open={openCreateNodeDialog} onClose={handleCloseAddDialog}>
        <DialogTitle>Create new node</DialogTitle>

        <CreateNodeDialogContent
          taxonomyName={taxonomyName}
          branchName={branchName}
          onCloseDialog={handleCloseAddDialog}
          onSuccess={() => {
            setOpenCreateNodeDialog(false);
            setCreateNodeOpenSuccessSnackbar(true);
          }}
        />
      </Dialog>

      {/* Snackbar for acknowledgment of addition of node */}
      <Snackbar
        anchorOrigin={{ vertical: "top", horizontal: "right" }}
        open={openCreateNodeSuccessSnackbar}
        autoHideDuration={6000}
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
    </>
  );
};

export default RootNodes;