import CreateNodeDialogContent from "@/components/CreateNodeDialogContent";
import NodesTableBody from "@/components/NodesTableBody";
import { greyHexCode } from "@/constants";
import {
  TableContainer,
  Paper,
  Table,
  TableHead,
  TableRow,
  Stack,
  TableCell,
  Typography,
  IconButton,
  Dialog,
  Alert,
  Grid,
  Snackbar,
  TablePagination,
  Box,
  CircularProgress,
  Container,
} from "@mui/material";
import { Dispatch, SetStateAction, useState } from "react";
import AddBoxIcon from "@mui/icons-material/AddBox";
import { useParams } from "react-router-dom";
import { NodeInfo } from "@/backend-types/types";

type AdvancedResearchResultsType = {
  nodeInfos: NodeInfo[];
  nodeCount: number | undefined;
  currentPage: number;
  setCurrentPage: Dispatch<SetStateAction<number>>;
  isError: boolean;
  errorMessage: string;
  isPending: boolean;
};

export const AdvancedResearchResults = ({
  nodeInfos,
  nodeCount = 0,
  currentPage,
  setCurrentPage,
  isError,
  errorMessage,
  isPending,
}: AdvancedResearchResultsType) => {
  const { taxonomyName, branchName } = useParams() as unknown as {
    taxonomyName: string;
    branchName: string;
  };

  const [openNewNodeDialog, setOpenNewNodeDialog] = useState(false);
  const [showNewNodeSuccess, setShowNewNodeSuccess] = useState(false);

  const handleCloseAddDialog = () => {
    setOpenNewNodeDialog(false);
  };

  const handleCloseSuccessSnackbar = () => {
    setShowNewNodeSuccess(false);
  };

  const handlePageChange = (
    event: React.MouseEvent | null,
    newPage: number
  ) => {
    setCurrentPage(newPage + 1);
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
    <Grid
      container
      direction="column"
      alignItems="center"
      justifyContent="center"
      sx={{ mt: 4 }}
    >
      <TableContainer sx={{ width: 375 }} component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell align="left">
                <Stack direction="row" alignItems="center">
                  <Typography variant="h6">Nodes</Typography>
                  <IconButton
                    sx={{ ml: 1, color: greyHexCode }}
                    onClick={() => {
                      setOpenNewNodeDialog(true);
                    }}
                  >
                    <AddBoxIcon />
                  </IconButton>
                </Stack>
              </TableCell>
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
      <TablePagination
        count={nodeCount}
        rowsPerPage={50}
        page={currentPage - 1}
        component="div"
        onPageChange={handlePageChange}
      ></TablePagination>

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
  );
};
