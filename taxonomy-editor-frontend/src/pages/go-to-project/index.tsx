import { useState, useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";

import {
  Typography,
  Box,
  Grid,
  Link as MuiLink,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from "@mui/material";
import { DataGrid, GridColDef, GridRowParams } from "@mui/x-data-grid";
import CircularProgress from "@mui/material/CircularProgress";
import { useQuery } from "@tanstack/react-query";

import { toSnakeCase, toTitleCase } from "@/utils";
import { DefaultService, Project, ProjectStatus } from "@/client";

const usePersistentState = <T,>(key: string, initialValue: T) => {
  const [state, setState] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch {
      return initialValue;
    }
  });

  useEffect(() => {
    window.localStorage.setItem(key, JSON.stringify(state));
  }, [key, state]);

  return [state, setState] as const;
};

const ProjectsFilterBar = ({
  owners,
  taxonomies,
  ownerFilter,
  setOwnerFilter,
  taxonomyFilter,
  setTaxonomyFilter,
  statusFilter,
  setStatusFilter,
  errorsFilter,
  setErrorsFilter,
}: {
  owners: string[];
  taxonomies: string[];
  ownerFilter: string;
  setOwnerFilter: (val: string) => void;
  taxonomyFilter: string;
  setTaxonomyFilter: (val: string) => void;
  statusFilter: string;
  setStatusFilter: (val: string) => void;
  errorsFilter: string;
  setErrorsFilter: (val: string) => void;
}) => {
  return (
    <Box
      sx={{
        display: "flex",
        gap: 2,
        mb: 2,
        flexWrap: "wrap",
        width: "100%",
        bgcolor: "#f2e9e4",
        p: 2,
        borderRadius: 1,
      }}
    >
      <FormControl size="small" sx={{ minWidth: 150 }}>
        <InputLabel>Owner</InputLabel>
        <Select
          value={ownerFilter}
          label="Owner"
          onChange={(e) => setOwnerFilter(e.target.value)}
        >
          <MenuItem value="All">All</MenuItem>
          {owners.map((owner) => (
            <MenuItem key={owner} value={owner}>
              {owner}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <FormControl size="small" sx={{ minWidth: 150 }}>
        <InputLabel>Taxonomy</InputLabel>
        <Select
          value={taxonomyFilter}
          label="Taxonomy"
          onChange={(e) => setTaxonomyFilter(e.target.value)}
        >
          <MenuItem value="All">All</MenuItem>
          {taxonomies.map((tax) => (
            <MenuItem key={tax} value={tax}>
              {toTitleCase(tax)}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <FormControl size="small" sx={{ minWidth: 150 }}>
        <InputLabel>Status</InputLabel>
        <Select
          value={statusFilter}
          label="Status"
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <MenuItem value="All">All</MenuItem>
          <MenuItem value="Not Exported">Not Exported</MenuItem>
          {Object.values(ProjectStatus).map((status) => (
            <MenuItem key={status} value={status}>
              {status}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <FormControl size="small" sx={{ minWidth: 150 }}>
        <InputLabel>Errors</InputLabel>
        <Select
          value={errorsFilter}
          label="Errors"
          onChange={(e) => setErrorsFilter(e.target.value)}
        >
          <MenuItem value="All">All</MenuItem>
          <MenuItem value="Has Errors">Has Errors</MenuItem>
          <MenuItem value="No Errors">No Errors</MenuItem>
        </Select>
      </FormControl>
    </Box>
  );
};
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
      `/${toSnakeCase(params.row.taxonomyName)}/${params.row.branchName}/entry`,
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
  const [ownerFilter, setOwnerFilter] = usePersistentState<string>(
    "projects_ownerFilter",
    "All",
  );
  const [taxonomyFilter, setTaxonomyFilter] = usePersistentState<string>(
    "projects_taxonomyFilter",
    "All",
  );
  const [statusFilter, setStatusFilter] = usePersistentState<string>(
    "projects_statusFilter",
    "All",
  );
  const [errorsFilter, setErrorsFilter] = usePersistentState<string>(
    "projects_errorsFilter",
    "All",
  );

  const filteredData = useMemo(() => {
    if (!data) return [];
    return data.filter((project) => {
      if (ownerFilter !== "All" && project.ownerName !== ownerFilter)
        return false;
      if (taxonomyFilter !== "All" && project.taxonomyName !== taxonomyFilter)
        return false;
      if (statusFilter === "Not Exported") {
        if (project.status === ProjectStatus.EXPORTED) return false;
      } else if (statusFilter !== "All" && project.status !== statusFilter) {
        return false;
      }
      if (errorsFilter === "Has Errors" && project.errorsCount === 0)
        return false;
      if (errorsFilter === "No Errors" && project.errorsCount > 0) return false;
      return true;
    });
  }, [data, ownerFilter, taxonomyFilter, statusFilter, errorsFilter]);

  const uniqueOwners = useMemo(() => {
    if (!data) return [];
    return Array.from(
      new Set(
        data
          .map((p) => p.ownerName)
          .filter((name): name is string => name !== null),
      ),
    ).sort();
  }, [data]);

  const uniqueTaxonomies = useMemo(() => {
    if (!data) return [];
    return Array.from(new Set(data.map((p) => p.taxonomyName))).sort();
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
    <>
      <Alert severity="warning">
        Please be careful when editing projects you do not own.
      </Alert>
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
            <ProjectsFilterBar
              owners={uniqueOwners}
              taxonomies={uniqueTaxonomies}
              ownerFilter={ownerFilter}
              setOwnerFilter={setOwnerFilter}
              taxonomyFilter={taxonomyFilter}
              setTaxonomyFilter={setTaxonomyFilter}
              statusFilter={statusFilter}
              setStatusFilter={setStatusFilter}
              errorsFilter={errorsFilter}
              setErrorsFilter={setErrorsFilter}
            />
            <ProjectsTable projects={filteredData} />
          </Box>
        </Grid>
      </Box>
    </>
  );
};
