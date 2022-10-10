/**
 * Build the taxonomy api url from ui url
 * @param URL location
 * @returns string
 */
function taxonomyApiUrlFromUi(location) {
    let components = location.host.split(".");
    if (components[0] === "ui") {
        // we build api url by just replacing ui by api
        components[0] = "api";
        return location.protocol + "//" + components.join(".") + "/"
    }
    else {
        // this is a default for simple dev setup
        return "http://localhost:80/"
    }
}
export const API_URL = taxonomyApiUrlFromUi(window.location);