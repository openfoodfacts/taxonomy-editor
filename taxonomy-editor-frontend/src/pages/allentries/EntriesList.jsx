import { Button, Typography } from "@mui/material";
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
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
                                Index
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
                                    <TableCell align="center" component="th" scope="row">
                                        {index+1}
                                    </TableCell>    
                                    <TableCell align="center" component="th" scope="row">
                                        {node[0].id}
                                    </TableCell>
                                    <TableCell align="center" component="th" scope="row">
                                        <Button onClick={event => handleClick(event, node[0].id) } variant="contained">
                                            Edit
                                        </Button>
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