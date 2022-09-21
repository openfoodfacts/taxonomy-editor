import useFetch from "../../components/useFetch";
import { Box, Typography } from "@mui/material";
import { Link } from "react-router-dom";
import { useEffect, useState } from "react";

const ListEntryParents = ({url}) => {
    const [relations, setRelations] = useState(null);
    const { data: incomingData, isPending, isError, isSuccess, errorMessage } = useFetch(url);
    
    useEffect(() => {
        setRelations(incomingData)
    }, [incomingData])

    // Check error in fetch
    if (isError) {
        return (<Typography sx={{ml: 4}} variant='h5'>{errorMessage}</Typography>)
    }
    if (isPending) {
        return (<Typography sx={{ml: 4}} variant='h5'>Loading..</Typography>)
    }
    return (
        <Box>
            {<Typography sx={{ml: 4, mb: 1}} variant='h5'>Parents</Typography>}

            {/* Renders parents or children of the node */}
            {relations && relations.map(relation => (
                <Box key={relation}>
                    <Link to={`/entry/${relation}`} style={{color: '#0064c8', display: 'inline-block'}}>
                        <Typography sx={{ml: 8, mb: 1}} variant='h6'>
                            {relation}
                        </Typography>
                    </Link>
                </Box>
            )) }

            {/* When no parents or children are present */}
            {relations && relations.length === 0 && <Typography sx={{ml: 8, mb: 1}} variant="h6"> None </Typography>}
        </Box>
    );
}
 
export default ListEntryParents;