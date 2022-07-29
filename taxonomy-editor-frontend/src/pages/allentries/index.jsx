import useFetch from "../../components/useFetch";
import EntriesList from "./EntriesList";

const Entry = () => {
    const {data: nodes, isPending, error} = useFetch('http://localhost:80/nodes');
    // console.log(nodes, isPending, error);
    return (
        <div className="allentries">
            {error && <div>{error}</div>}
            {isPending && <div>Loading...</div>}
            {nodes && <EntriesList nodes={nodes} title={"Test"}/>}
        </div>
    );
}
 
export default Entry;