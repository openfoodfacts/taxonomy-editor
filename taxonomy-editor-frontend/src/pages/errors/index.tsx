import useFetch from "@/components/useFetch";
import { toTitleCase } from "@/utils";
import { createBaseURL } from "@/utils";
import { useParams } from "react-router-dom";
import {
  Box,
  Typography,
  Table,
  TableCell,
  TableBody,
  TableHead,
  TableContainer,
  Stack,
} from "@mui/material";
import MaterialTable from "@material-table/core";
import { Alert, CircularProgress } from "@mui/material";
import { useState, useEffect } from "react";

interface ErrorParams {
  taxonomyName: string;
  branchName: string;
}

const Errors = ({ addNavLinks }) => {
  const { taxonomyName, branchName } = useParams() as unknown as ErrorParams;
  const baseUrl = createBaseURL(taxonomyName, branchName);
  const [errors, setErrors] = useState([]);
  const {
    data: errorData,
    isPending,
    isError,
  } = useFetch(`${baseUrl}parsing_errors`);

  useEffect(() => {
    if (!errorData) return;
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-expect-error
    const newErrors = errorData.errors.map((error, index) => ({
      id: index + 1,
      error: error,
    }));
    setErrors(newErrors);
  }, [errorData]);

  useEffect(
    function defineMainNavLinks() {
      if (!branchName || !taxonomyName) return;

      addNavLinks({ branchName, taxonomyName });
    },
    [taxonomyName, branchName, addNavLinks]
  );

  if (isError) {
    return (
      <Box>
        <Typography variant="h5">Unable to load errors.</Typography>
      </Box>
    );
  }
  if (isPending) {
    return (
      <Box
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
        }}
      >
        <CircularProgress sx={{ textAlign: "center" }} />
      </Box>
    );
  }

  return (
    <Box
      sx={{ display: "flex", flexDirection: "column", my: 4, mx: 6, gap: 2 }}
    >
      <TableContainer sx={{ width: 375, mb: 2 }}>
        <Table style={{ border: "solid", borderWidth: 1.5 }}>
          <TableHead>
            <TableCell align="left">
              <Typography variant="h6">Taxonomy name</Typography>
            </TableCell>
            <TableCell align="left">
              <Typography variant="h6">Branch name</Typography>
            </TableCell>
          </TableHead>
          <TableBody>
            <TableCell align="left" component="td" scope="row">
              <Typography variant="body1">
                {toTitleCase(taxonomyName || "")}
              </Typography>
            </TableCell>
            <TableCell align="left" component="td" scope="row">
              <Typography variant="body1">{branchName}</Typography>
            </TableCell>
          </TableBody>
        </Table>
      </TableContainer>
      <Stack
        sx={{ display: "flex", flexDirection: "column", alignItems: "center" }}
      >
        {errors.length > 0 && (
          <>
            <Alert severity="warning">
              These errors must be fixed manually first, by creating a cleanup
              PR on GitHub:
              https://github.com/openfoodfacts/openfoodfacts-server/tree/main/taxonomies
            </Alert>
            <Box
              sx={{
                border: "solid",
                borderWidth: 1.5,
              }}
            >
              <MaterialTable
                data={errors}
                columns={[
                  {
                    title: "No.",
                    field: "id",
                    width: "10%",
                  },
                  { title: "Error", field: "error" },
                ]}
                title="Errors"
                options={{
                  tableLayout: "fixed",
                  pageSize: 50,
                  pageSizeOptions: [20, 50, 100, 200],
                }}
              />
            </Box>
          </>
        )}
        {errors.length === 0 && (
          <Typography>
            ✅ Well done! No errors: {toTitleCase(taxonomyName || "")} can be
            edited
          </Typography>
        )}
      </Stack>
    </Box>
  );
};

export default Errors;
