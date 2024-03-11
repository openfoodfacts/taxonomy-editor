import { useMemo } from "react";
import { useNavigate } from "react-router-dom";

import { Typography, Box, Grid, Link as MuiLink } from "@mui/material";
import MaterialTable from "@material-table/core";
import EditIcon from "@mui/icons-material/Edit";
import CircularProgress from "@mui/material/CircularProgress";
import { useQuery } from "@tanstack/react-query";

import { toSnakeCase, toTitleCase } from "@/utils";
import { DefaultService } from "@/client";

type ProjectType = {
  id: string;
  projectName: string;
  taxonomyName: string;
  ownerName: string;
  branchName: string;
  description: string;
  errors_count: number;
};

export const GoToProject = () => {
  const navigate = useNavigate();

  const { data, isPending, isError } = useQuery({
    queryKey: ["getAllProjectsProjectsGet"],
    queryFn: async () => {
      return await DefaultService.getAllProjectsProjectsGet();
    },
  });

  const projectData: ProjectType[] = useMemo(() => {
    if (!data) return [];
    return data.map(
      ({
        id,
        branch_name,
        taxonomy_name,
        owner_name,
        description,
        errors_count,
        status,
      }) => {
        return {
          id, // needed by MaterialTable as key
          projectName: id,
          taxonomyName: toTitleCase(taxonomy_name),
          ownerName: owner_name ? owner_name : "unknown",
          branchName: branch_name,
          description: description,
          errors_count: errors_count,
          status: status,
        };
      }
    );
  }, [data]);

  if (isError) {
    return (
      <Typography variant="h5">
        Something went wrong. Please try again
      </Typography>
    );
  }

  if (isPending) {
    return (
      <Box sx={{ textAlign: "center", my: 10 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ overflowY: "scroll" }}>
      <Grid
        container
        direction="column"
        alignItems="center"
        justifyContent="center"
      >
        <Typography sx={{ mt: 2 }} variant="h6">
          List of current projects
        </Typography>
        <MaterialTable
          data={projectData}
          columns={[
            { title: "Project", field: "projectName" },
            { title: "Taxonomy", field: "taxonomyName" },
            { title: "Branch", field: "branchName" },
            { title: "owner", field: "ownerName" },
            { title: "Description", field: "description", width: "10vw" },
            {
              title: "Errors",
              field: "errors_count",
              render: (rowData) => {
                if (rowData["errors_count"] > 0) {
                  return (
                    <MuiLink
                      color="error"
                      href={`/${toSnakeCase(rowData["taxonomyName"])}/${
                        rowData["branchName"]
                      }/errors`}
                    >
                      {rowData["errors_count"] + " errors"}
                    </MuiLink>
                  );
                }
              },
            },
            { title: "Status", field: "status" },
          ]}
          options={{
            actionsColumnIndex: -1,
            addRowPosition: "last",
            showTitle: false,
          }}
          actions={[
            {
              icon: () => <EditIcon />,
              tooltip: "Edit project",
              onClick: (event, rowData) => {
                navigate(
                  `/${toSnakeCase(rowData["taxonomyName"])}/${
                    rowData["branchName"]
                  }/entry`
                );
              },
            },
          ]}
        />
      </Grid>
    </Box>
  );
};
