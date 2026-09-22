import { Box, FormControl, InputLabel, Select, MenuItem } from "@mui/material";
import { ProjectStatus } from "@/client";
import { toTitleCase } from "@/utils";
import { useState, useEffect } from "react";

export const usePersistentState = <T,>(key: string, initialValue: T) => {
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

export const ProjectsFilterBar = ({
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
