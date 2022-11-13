import { API_URL } from "../../constants.js"

/**
 * Finds type of ID
 * Eg: Stopword, Synonym, Entry, Header or Footer
*/ 
export function getIdType(id) {
    let idType = '';

    if (id.startsWith('__header__')) { idType = 'Header' }
    else if (id.startsWith('__footer__')) { idType = 'Footer' }
    else if (id.startsWith('synonym')) { idType = 'Synonyms' }
    else if (id.startsWith('stopword')) { idType = 'Stopwords' }
    else { idType = 'entry' }

    return idType
}

/**
 * Creating base URL for server requests
 */
export function createBaseURL(taxonomyName, branchName) {
    return `${API_URL}${taxonomyName}/${branchName}/`
}

/**
 * Finding ID-specific URL for server requests
*/
export function createURL(taxonomyName, branchName, id) {

    let url = createBaseURL(taxonomyName, branchName);

    // ID's can look like: __header__, __footer__, synomym:0, stopword:0
    // For an entry, id looks like en:yogurts

    if (getIdType(id) === 'Header') { url += 'header/' }
    else if (getIdType(id) === 'Footer') { url += 'footer/' }
    else if (getIdType(id) === 'Synonyms') { url += `synonym/${id}/` }
    else if (getIdType(id) === 'Stopwords') { url += `stopword/${id}/` }
    else { url += `entry/${id}/` }

    return url
}