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
};

export const AdvancedResearchResults = ({
  nodeInfos,
  nodeCount = 0,
  currentPage,
  setCurrentPage,
}: AdvancedResearchResultsType) => {
  const { taxonomyName, branchName } = useParams<{
    taxonomyName: string;
    branchName: string;
  }>();

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

  return (
    <Grid
      container
      direction="column"
      alignItems="center"
      justifyContent="center"
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
            taxonomyName={taxonomyName ?? ""}
            branchName={branchName ?? ""}
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
          taxonomyName={taxonomyName ?? ""}
          branchName={branchName ?? ""}
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
