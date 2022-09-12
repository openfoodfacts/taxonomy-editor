import useFetch from "../../components/useFetch";
import { Typography } from "@mui/material";
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
        return (<div>{errorMessage}</div>)
    }
    if (isPending) {
        return (<Typography sx={{ml: 4}} variant='h5' component={'div'}>Loading..</Typography>)
    }
    return (
        <div className="relations">
            {<Typography sx={{ml: 4, mb: 1}} variant='h5' component={'div'}>Parents</Typography>}

            {/* Renders parents or children of the node */}
            {relations && relations.map(relation => (
                <div className="relation-component" key={relation}>
                    <Link to={`/entry/${relation}`} style={{color: '#0064c8', display: 'inline-block'}}>
                        <Typography sx={{ml: 8, mb: 1}} variant='h6'>
                            {relation}
                        </Typography>
                    </Link>
                </div>
            )) }

            {/* When no parents or children are present */}
            {relations && relations.length === 0 && <Typography sx={{ml: 8, mb: 1}} variant="h6"> None </Typography>}
        </div>
    );
}
 
export default ListEntryParents;