import { useNavigate } from "react-router-dom";

import { Typography, Box, Grid, Link as MuiLink } from "@mui/material";
import { DataGrid, GridColDef, GridRowParams } from "@mui/x-data-grid";
import CircularProgress from "@mui/material/CircularProgress";
import { useQuery } from "@tanstack/react-query";

import { toSnakeCase, toTitleCase } from "@/utils";
import { DefaultService, Project, ProjectStatus } from "@/client";

const ProjectsTable = ({ projects }: { projects: Project[] }) => {
  const navigate = useNavigate();

  const columns: GridColDef<Project>[] = [
    { headerName: "Project", field: "id", flex: 3 },
    {
      headerName: "Taxonomy",
      field: "taxonomyName",
      flex: 2,
      valueFormatter: ({ value }) => toTitleCase(value),
    },
    { headerName: "Branch", field: "branchName", flex: 3 },
    { headerName: "Owner", field: "ownerName", flex: 2 },
    { headerName: "Description", field: "description", flex: 3 },
    {
      headerName: "Errors",
      field: "errorsCount",
      renderCell: ({ row }) => {
        if (row.errorsCount == 0) {
          return null;
        }

        return (
          <MuiLink
            color="error"
            href={`/${toSnakeCase(row.taxonomyName)}/${row.branchName}/errors`}
            onClick={(event) => event.stopPropagation()}
          >
            {row.errorsCount + " errors"}
          </MuiLink>
        );
      },
    },
    {
      headerName: "Status",
      field: "status",
      renderCell: ({ row }) => {
        if (row.status === ProjectStatus.EXPORTED) {
          return (
            <MuiLink
              target="_blank"
              rel="noopener"
              href={row.githubPrUrl as string}
              onClick={(event) => event.stopPropagation()}
            >
              {row.status}
            </MuiLink>
          );
        }
      },
    },
  ];

  const onRowClick = (params: GridRowParams<Project>) => {
    navigate(
      `/${toSnakeCase(params.row.taxonomyName)}/${params.row.branchName}/entry`
    );
  };

  return (
    <DataGrid
      rows={projects}
      columns={columns}
      onRowClick={onRowClick}
      pageSizeOptions={[]}
      initialState={{
        pagination: { paginationModel: { pageSize: 25 } },
      }}
    />
  );
};

export const GoToProject = () => {
  const { data, isPending, isError } = useQuery({
    queryKey: ["getAllProjectsProjectsGet"],
    queryFn: async () => {
      return await DefaultService.getAllProjectsProjectsGet();
    },
  });

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
        gap={2}
      >
        <Typography sx={{ mt: 2 }} variant="h6">
          List of current projects
        </Typography>
        <Box sx={{ width: "90%", mb: 6 }}>
          <ProjectsTable projects={data} />
        </Box>
      </Grid>
    </Box>
  );
};
