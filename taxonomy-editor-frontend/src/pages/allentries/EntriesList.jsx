import { Typography } from "@mui/material";
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import EditIcon from '@mui/icons-material/Edit';
import IconButton from '@mui/material/IconButton';
import { useNavigate } from "react-router-dom";

const EntriesList = ({ nodes, title }) => {
    const navigate = useNavigate();
    const handleClick = (event, id) => {
        event.preventDefault();
        navigate('/entry/'+id);
    }
    return ( 
        <div className="entry">
            <Typography sx={{mb: 1, mt:2, ml: 2}} variant="h4">
                List of nodes in {title} Taxonomy:
            </Typography>
            <div className="entry-preview">
                <TableContainer sx={{ml: 2}} component={Paper}>
                    <Table sx={{ width: 500 }}>
                        <TableHead>
                        <TableRow>
                            <TableCell align="center">
                            <Typography variant="h6">
                                #
                            </Typography>
                            </TableCell>
                            <TableCell align="center">
                            <Typography variant="h6">
                                Nodes
                            </Typography>
                            </TableCell>
                            <TableCell align="center">
                            <Typography variant="h6">
                                Action
                            </Typography>
                            </TableCell>
                        </TableRow>
                        </TableHead>
                        <TableBody>
                            {nodes.map((node, index) => (
                                <TableRow
                                key={node[0].id}
                                sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                                >
                                    <TableCell align="center" component="td" scope="row">
                                        <Typography variant="subtitle1">
                                            {index+1}
                                        </Typography>
                                    </TableCell>    
                                    <TableCell align="center" component="td" scope="row">
                                        <Typography variant="subtitle1">
                                            {node[0].id}
                                        </Typography>
                                    </TableCell>
                                    <TableCell align="center" component="td" scope="row">
                                        <IconButton onClick={event => handleClick(event, node[0].id) } aria-label="edit">
                                            <EditIcon color="primary"/>
                                        </IconButton>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            </div>
        </div>
     );
}
 
export default EntriesList;