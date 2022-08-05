import useFetch from "../../components/useFetch";
import { Typography } from "@mui/material";
import { Link } from "react-router-dom";
import OpenInNewIcon from '@mui/icons-material/OpenInNew';

const FetchRelations = ({url, title}) => {
    const { data: relations, error, isPending } = useFetch(url);
    if (error) {
        return (<div>{error}</div>)
    }
    return (
        <div className="relations">
            {isPending && <Typography sx={{ml: 4}} variant='h5' component={'div'}>Loading..</Typography>}
            {!isPending && <Typography sx={{ml: 4, mb: 1, textDecoration: 'underline'}} variant='h5' component={'div'}>{title}</Typography>}
            {relations && relations.map(relation => (
                <div className="relation-component" key={relation}>
                    <Typography sx={{ml: 8, mb: 1}} variant='h6'>
                        {relation}
                        <Link to={`/entry/${relation}`}>
                            <OpenInNewIcon style={{marginLeft: 12, position: 'relative', top: '6px'}} color="primary"/>
                        </Link>
                    </Typography>
                </div>
            )) }
            {relations && relations.length === 0 && <Typography sx={{ml: 8, mb: 1}} variant="h6"> None </Typography>}
        </div>
    );
}
 
export default FetchRelations;