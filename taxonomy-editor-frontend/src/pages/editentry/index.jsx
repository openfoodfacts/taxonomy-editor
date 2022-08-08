import { Typography } from "@mui/material";
import { useParams } from "react-router-dom";
import AccumulateAllComponents from "./AccumulateAllComponents";

const EditEntry = () => {
    const { id } = useParams();
    return (
        <div className="main-content">
            {/* Renders id of current node */}
            <div className="node-title">
                <Typography sx={{mb: 2, mt:2, ml: 2}} variant="h4">
                    You are now editing "{id}" 
                </Typography>
            </div>
            {/* Renders node info based on id */}
            <AccumulateAllComponents id={id} />
        </div>
    );
}
 
export default EditEntry;