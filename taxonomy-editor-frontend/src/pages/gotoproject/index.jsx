import { Typography, Box, Grid } from "@mui/material";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import useFetch from "../../components/useFetch";
import { API_URL } from "../../constants";
import MaterialTable from "@material-table/core";
import EditIcon from "@mui/icons-material/Edit";
import { useEffect } from "react";
import { toSnakeCase, toTitleCase } from "../../utils";

const GotoProject = () => {
  /* eslint no-unused-vars: ["error", { varsIgnorePattern: "^__" }] */
  const {
    data: incomingData,
    isPending,
    isError,
    __isSuccess,
    errorMessage,
  } = useFetch(`${API_URL}projects?status=OPEN`);
  const [projectData, setProjectData] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const renderedProjects = [];
    if (incomingData) {
      incomingData.forEach((element) => {
        const projectNode = element[0];
        renderedProjects.push({
          id: Math.random().toString(), // Used as Material Table component key
          projectName: projectNode["id"],
          taxonomyName: toTitleCase(projectNode["taxonomy_name"]),
          branchName: projectNode["branch_name"],
          description: projectNode["description"],
        });
      });
    }
    setProjectData(renderedProjects);
  }, [incomingData]);

  // Check error in fetch
  if (isError) {
    return <Typography variant="h5">{errorMessage}</Typography>;
  }
  if (isPending) {
    return <Typography variant="h5">Loading..</Typography>;
  }

  return (
    <Box>
      <Grid
        container
        direction="column"
        alignItems="center"
        justifyContent="center"
      >
        <Typography sx={{ mt: 4 }} variant="h3">
          Existing Project?
        </Typography>
        <Typography sx={{ mt: 2 }} variant="h6">
          List of open projects
        </Typography>
        <MaterialTable
          data={projectData}
          columns={[
            { title: "Project", field: "projectName" },
            { title: "Taxonomy", field: "taxonomyName" },
            { title: "Branch", field: "branchName" },
            { title: "Description", field: "description", width: "15vw" },
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

export default GotoProject;
