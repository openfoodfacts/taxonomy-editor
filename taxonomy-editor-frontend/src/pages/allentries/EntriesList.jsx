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

    // Handler function for button clicks
    const handleClick = (event, id) => {
        event.preventDefault();
        navigate('/entry/'+id);
    }
    return ( 
        <div className="entry">
            <Typography sx={{mb: 1, mt:2, ml: 2}} variant="h4">
                List of nodes in {title} Taxonomy:
            </Typography>
            <Typography variant="h6" sx={{mt: 2, ml: 2, mb: 1}}>
                Number of nodes in taxonomy: {nodes.length}
            </Typography>
            {/* Table for listing all nodes in taxonomy */}
            <div className="entry-preview">
                <TableContainer sx={{ml: 2}} component={Paper}>
                    <Table sx={{ width: 400 }}>
                        <TableHead>
                        <TableRow>
                            <TableCell align="left">
                            <Typography variant="h6">
                                Nodes
                            </Typography>
                            </TableCell>
                            <TableCell align="left">
                            <Typography variant="h6">
                                Action
                            </Typography>
                            </TableCell>
                        </TableRow>
                        </TableHead>
                        <TableBody>
                            {nodes.map((node) => (
                                <TableRow
                                key={node[0].id}
                                >   
                                    <TableCell align="left" component="td" scope="row">
                                        <Typography variant="subtitle1">
                                            {node[0].id}
                                        </Typography>
                                    </TableCell>
                                    <TableCell align="left" component="td" scope="row">
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