import { BASE_API_URL } from "./config";

export function make_url(...segments: string[]) {
    /** Make url from segments: e.g "foo", "bar" => foobar */
    segments = segments.map( (x) => x.replace(/\/?(.+?)\/?/, "$1"));
    return segments.join("/");
}

export async function post(route: string, data: object){
    const full_url: string = make_url(BASE_API_URL, route);

    const response = await fetch(full_url, {
        headers: {
            ""
        }
    })

}

export async function get(route: string){

}