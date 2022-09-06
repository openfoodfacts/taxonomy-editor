import useFetch from "../../components/useFetch";
import { Box, Typography } from "@mui/material";
import { Link } from "react-router-dom";

const ListAllEntryRelationships = ({url, title}) => {
    const { data: relations, isPending, isError, isSuccess, errorMessage } = useFetch(url);
    // Check error in fetch
    if (isError) {
        return (
            <Box>
                <Typography sx={{ml: 4}} variant='h5'>{errorMessage}</Typography>
            </Box>
        )
    }
    if (isPending) {
        return (
            <Typography sx={{ml: 4}} variant='h5'>Loading..</Typography>
        )
    }
    return (
        <Box>
            <Typography sx={{ml: 4, mb: 1}} variant='h5'>{title}</Typography>

            {/* When no parents or children are present */}
            {relations && relations.length === 0 && <Typography sx={{ml: 8, mb: 1}} variant="h6"> None </Typography>}

            {/* Renders parents or children of the node */}
            {relations && relations.map(relation => (
                <Box key={relation}>
                    <Link to={`/entry/${relation}`}>
                        <Typography sx={{ml: 8, mb: 1}} variant='h6'>
                            {relation}
                        </Typography>
                    </Link>
                </Box>
            )) }
        </Box>
    );
}
 
export default ListAllEntryRelationships;