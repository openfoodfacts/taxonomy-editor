import { FiltersType } from "./AdvancedResearchForm";

type OneFilterType<T extends FiltersType[keyof FiltersType]> = {
    [K in keyof FiltersType]: FiltersType[K] extends T ? { [Key in K]: T } : never;
}[keyof FiltersType];


export function splitQueryIntoSearchTerms(query: string): string[] {
    query = query.trim();
    const searchTerms: string[] = [];
    let insideQuotes = false;
    let termStart = 0;

    for (let termEnd = 0; termEnd < query.length; termEnd++) {
        if (query[termEnd] === '"') {
            insideQuotes = !insideQuotes;
        } else if (query[termEnd] === " " && !insideQuotes) {
            const searchTerm = query.substring(termStart, termEnd);
            searchTerms.push(searchTerm);
            termStart = termEnd + 1;
        }
    }

    searchTerms.push(query.substring(termStart));

    return searchTerms;
}

export function parseFilterSearchTerm(searchTerm: string): OneFilterType<boolean> | OneFilterType<string[]> | null {
    if (!searchTerm.includes(":")) {
        console.log("null because does not include : ", searchTerm);
        return null;
    }

    const splitTerm = searchTerm.split(":", 2);
    const filterName = splitTerm[0];
    let filterValue = splitTerm[1];

    if (filterValue.startsWith('"') && filterValue.endsWith('"')) {
        filterValue = filterValue.slice(1, -1);
    }

    if (filterValue.includes('"')) {
        console.log('null because include "');
        return null;
    }

    switch (filterName) {
        case "is":
            if (filterValue === "root") {
                return {is_root: true};
            }
            if (filterValue === "modified") {
                return {is_modified: true};
            }
            break;
        case "language":
            return {with_languages: [filterValue]}
        // case "not(language)":
        //     if (filterValue.length !== 2 || !filterValue.match(/^[a-zA-Z]+$/)) {
        //         return null;
        //     }
        //     return new LanguageFilterSearchTerm(filterValue, filterName === "not(language)");
        // case "parent":
        //     return new ParentFilterSearchTerm(filterValue);
        // case "child":
        //     return new ChildFilterSearchTerm(filterValue);
        // case "ancestor":
        //     return new AncestorFilterSearchTerm(filterValue);
        // case "descendant":
        //     return new DescendantFilterSearchTerm(filterValue);
        default:
            break;
    }
    console.log("null because end of function");
    return null;
}
