import { API_URL } from "../../constants.js"

export function createURL(id) {

    // Finding URL to send requests
    let url = API_URL;
    let isEntry = false;

    // ID's can look like: __header__, __footer__, synomym:0, stopword:0
    // For an entry, id looks like en:yogurts
    if (id.startsWith('__header__')) { url += 'header/' }
    else if (id.startsWith('__footer__')) { url += 'footer/' }
    else if (id.startsWith('synonym')) { url += `synonym/${id}/` }
    else if (id.startsWith('stopword')) { url += `stopword/${id}/` }
    else { url += `entry/${id}/`; isEntry = true; }

    return {url, isEntry}
}