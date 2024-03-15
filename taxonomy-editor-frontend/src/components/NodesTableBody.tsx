import {
  IconButton,
  TableBody,
  TableCell,
  TableRow,
  Typography,
} from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";
import { Link } from "react-router-dom";
import { NodeInfo } from "@/backend-types/types";

type Props = {
  nodeInfos: NodeInfo[];
  taxonomyName: string;
  branchName: string;
};

const NodesTableBody = ({ nodeInfos, taxonomyName, branchName }: Props) => {
  return (
    <>
      <TableBody>
        {nodeInfos.map(({ id, is_external: isExternal }) => (
          <TableRow key={id}>
            <TableCell align="left" component="td" scope="row">
              <Typography variant="subtitle1">{id}</Typography>
              {isExternal && (
                <Typography variant="subtitle2" color="secondary">
                  External Node
                </Typography>
              )}
            </TableCell>
            <TableCell align="left" component="td" scope="row">
              <IconButton
                component={Link}
                to={`/${taxonomyName}/${branchName}/entry/${id}`}
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
