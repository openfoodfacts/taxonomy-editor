import {
  IconButton,
  TableBody,
  TableCell,
  TableRow,
  Typography,
} from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";
import { Link } from "react-router-dom";

type Props = {
  nodeIds: string[];
  taxonomyName: string;
  branchName: string;
};

const NodesTableBody = ({ nodeIds, taxonomyName, branchName }: Props) => {
  return (
    <>
      <TableBody>
        {nodeIds.map((nodeId) => (
          <TableRow key={nodeId}>
            <TableCell align="left" component="td" scope="row">
              <Typography variant="subtitle1">{nodeId}</Typography>
            </TableCell>
            <TableCell align="left" component="td" scope="row">
              <IconButton
                component={Link}
                to={`/${taxonomyName}/${branchName}/entry/${nodeId}`}
                aria-label="edit"
              >
                <EditIcon color="primary" />
              </IconButton>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </>
  );
};

export default NodesTableBody;
