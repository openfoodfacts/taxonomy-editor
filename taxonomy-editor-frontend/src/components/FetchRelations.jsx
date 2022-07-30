import useFetch from "./useFetch";
import { Typography } from "@mui/material";
import { Link } from "react-router-dom";
import OpenInNewIcon from '@mui/icons-material/OpenInNew';

const FetchRelations = ({url, title}) => {
    const { data: parents, error, isPending } = useFetch(url);
    return (
        <div className="relations">
            {isPending && <Typography sx={{ml: 4}} variant='h5' component={'div'}>Loading..</Typography>}
            {!isPending && <Typography sx={{ml: 4, mb: 1, textDecoration: 'underline'}} variant='h5' component={'div'}>{title}</Typography>}
            {parents && parents.map(parent => (
                <div className="parent-comp" key={parent}>
                    <Typography sx={{ml: 8, mb: 1}} variant='h6'>
                        {parent}
                        <Link to={`/entry/${parent}`}>
                            <OpenInNewIcon style={{marginLeft: 12 ,position: 'relative', top: '6px'}} color="primary"/>
                        </Link>
                    </Typography>
                </div>
            )) }
        </div>
     );
}
 
export default FetchRelations;