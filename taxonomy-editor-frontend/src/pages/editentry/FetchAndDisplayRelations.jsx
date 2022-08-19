import useFetch from "../../components/useFetch";
import { Typography } from "@mui/material";
import { Link } from "react-router-dom";

const FetchRelations = ({url, title}) => {
    const { data: relations, errorMessage, isPending } = useFetch(url);
    // Check error in fetch
    if (errorMessage) {
        return (<div>{errorMessage}</div>)
    }
    return (
        <div className="relations">
            {isPending && <Typography sx={{ml: 4}} variant='h5' component={'div'}>Loading..</Typography>}
            {/* Title */}
            {!isPending && <Typography sx={{ml: 4, mb: 1}} variant='h5' component={'div'}>{title}</Typography>}

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
 
export default FetchRelations;