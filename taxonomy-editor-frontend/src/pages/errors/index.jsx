import useFetch from "../../components/useFetch";
import { toTitleCase } from "../../components/interConvertNames";
import { createBaseURL } from "../editentry/createURL";
import { useParams } from "react-router-dom";
import {
  Box,
  Typography,
  Table,
  TableCell,
  TableBody,
  TableHead,
  TableContainer,
} from "@mui/material";
import MaterialTable from "@material-table/core";
import { useState, useEffect } from "react";

const Errors = ({ setDisplayedPages }) => {
  const { taxonomyName, branchName } = useParams();
  const title = toTitleCase(taxonomyName);
  const baseUrl = createBaseURL(taxonomyName, branchName);
  const urlPrefix = `${taxonomyName}/${branchName}/`;
  const [errors, setErrors] = useState([]);
  /* eslint no-unused-vars: ["error", { varsIgnorePattern: "^__" }] */
  const {
    data: errorData,
    isPending,
    isError,
    __isSuccess,
    errorMessage,
  } = useFetch(`${baseUrl}parsing_errors`);

  useEffect(() => {
    if (!errorData) return;
    errorData.errors.forEach((error, index) => {
      setErrors((prevErrors) => [
        ...prevErrors,
        {
          id: index + 1,
          error: error,
        },
      ]);
    });
  }, [errorData]);

  // Set url prefix for navbar component
  useEffect(
    function addUrlPrefixToNavbar() {
      setDisplayedPages([
        { url: urlPrefix + "entry", translationKey: "Nodes" },
        { url: urlPrefix + "search", translationKey: "Search" },
        { url: urlPrefix + "errors", translationKey: "Errors" },
        { url: urlPrefix + "export", translationKey: "Export" },
      ]);
    },
    [urlPrefix, setDisplayedPages]
  );

  if (isError) {
    return (
      <Box>
        <Typography variant="h5">{errorMessage}</Typography>
      </Box>
    );
  }
  if (isPending) {
    return (
      <Box>
        <Typography variant="h5">Loading..</Typography>
      </Box>
    );
  }

  return (
    <>
      <TableContainer sx={{ ml: 2, width: 375, mt: 2 }}>
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
              <Typography variant="body1">{title}</Typography>
            </TableCell>
            <TableCell align="left" component="td" scope="row">
              <Typography variant="body1">{branchName}</Typography>
            </TableCell>
          </TableBody>
        </Table>
      </TableContainer>
      <Box
        sx={{
          width: 500,
          ml: 2,
          mt: 2,
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
          }}
        />
      </Box>
    </>
  );
};

export default Errors;
