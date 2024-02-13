import { useState } from "react";
import { useParams } from "react-router-dom";

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
import AddBoxIcon from "@mui/icons-material/AddBox";
import Dialog from "@mui/material/Dialog";
import CircularProgress from "@mui/material/CircularProgress";

import CreateNodeDialogContent from "@/components/CreateNodeDialogContent";
import { toTitleCase, createBaseURL } from "@/utils";
import { greyHexCode } from "@/constants";
import {
  type ProjectInfoAPIResponse,
  type RootEntriesAPIResponse,
  ProjectStatus,
} from "@/backend-types/types";
import NodesTableBody from "@/components/NodesTableBody";
import WarningParsingErrors from "@/components/WarningParsingErrors";
import { useQuery } from "@tanstack/react-query";

type RootNodesProps = {
  taxonomyName: string;
  branchName: string;
};

const RootNodes = ({ taxonomyName, branchName }: RootNodesProps) => {
  const [openCreateNodeDialog, setOpenCreateNodeDialog] = useState(false);
  const [openCreateNodeSuccessSnackbar, setCreateNodeOpenSuccessSnackbar] =
    useState(false);

  const baseUrl = createBaseURL(taxonomyName, branchName);
  const projectInfoUrl = `${baseUrl}project`;
  const rootNodesUrl = `${baseUrl}rootentries`;

  const {
    data: info,
    isPending: infoPending,
    isError: infoIsError,
    error: infoError,
  } = useQuery<ProjectInfoAPIResponse>({
    queryKey: [projectInfoUrl],
    queryFn: async () => {
      const response = await fetch(projectInfoUrl);
      if (!response.ok) {
        throw new Error("Failed to fetch project info");
      }
      return response.json();
    },
    refetchInterval: (d) => {
      return d.state.status === "success" &&
        d.state.data?.status === ProjectStatus.LOADING
        ? 1000
        : false;
    },
  });

  const {
    data: nodes,
    isPending,
    isError,
    error,
  } = useQuery<RootEntriesAPIResponse>({
    queryKey: [rootNodesUrl],
    queryFn: async () => {
      const response = await fetch(rootNodesUrl);
      if (!response.ok) {
        throw new Error("Failed to fetch root nodes");
      }
      return response.json();
    },
    // fetch root nodes after receiving project status
    enabled:
      !!info &&
      [
        ProjectStatus.OPEN,
        ProjectStatus.CLOSED,
        ProjectStatus.EXPORTED,
      ].includes(info.status as ProjectStatus),
  });

  let nodeIds: string[] = [];
  if (nodes && nodes.length > 0) {
    nodeIds = nodes.map((node) => node[0].id);
  }

  const handleCloseAddDialog = () => {
    setOpenCreateNodeDialog(false);
  };

  const handleCloseSuccessSnackbar = () => {
    setCreateNodeOpenSuccessSnackbar(false);
  };

  if (isError || infoIsError || !branchName || !taxonomyName) {
    return (
      <Box>
        <Typography variant="h5">
          {error?.message ?? infoError?.message}
        </Typography>
      </Box>
    );
  }

  if (info && info["status"] === ProjectStatus.FAILED) {
    return (
      <Typography variant="h5">
        Parsing of the project has failed, rendering it uneditable.
      </Typography>
    );
  }

  if (isPending || infoPending || !nodes) {
    return (
      <Box
        sx={{
          textAlign: "center",
          my: 10,
        }}
      >
        <CircularProgress />
        {info && info["status"] === ProjectStatus.LOADING && (
          <Typography sx={{ m: 5 }} variant="h6">
            Taxonomy parsing may take several minutes, depending on the
            complexity of the taxonomy being imported.
          </Typography>
        )}
      </Box>
    );
  }

  return (
    <>
      <WarningParsingErrors baseUrl={baseUrl} />
      <div>
        <Typography sx={{ mb: 2, mt: 2, ml: 2 }} variant="h4">
          Root Nodes:
        </Typography>

        <TableContainer sx={{ ml: 2, width: 375 }}>
          <Table style={{ border: "solid", borderWidth: 1.5 }}>
            <TableHead>
              <TableCell align="left">
                <Typography variant="h6">Taxonomy Name</Typography>
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
            <NodesTableBody
              nodeIds={nodeIds}
              taxonomyName={taxonomyName}
              branchName={branchName}
            />
          </Table>
        </TableContainer>
      </div>

      {/* Dialog box for adding nodes */}
      <Dialog open={openCreateNodeDialog} onClose={handleCloseAddDialog}>
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

export const RootNodesWrapper = () => {
  const { taxonomyName, branchName } = useParams();
  if (!taxonomyName || !branchName)
    return (
      <Typography variant="h3">
        Oops, something went wrong! Please try again later.
      </Typography>
    );

  return <RootNodes taxonomyName={taxonomyName} branchName={branchName} />;
};
