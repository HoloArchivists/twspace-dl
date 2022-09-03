type space = {
  id: string;
  url: string;
  title: string;
  creator_name: string;
  start_date: string;
  state: string;
  available_for_replay: string;
  media_key: string
}

let metadata () =
  Format.printf "called metadata command\n"

let url () =
  Format.printf "called url command\n"

open Lwt
open Cohttp
open Cohttp_lwt_unix
open Uri

let metadata_json id =
  let open Str in
  let params = global_replace (regexp "[ \n]") "" (Format.sprintf {|\
    "{"id":"%s",\
    "isMetatagsQuery":false,\
    "withSuperFollowsUserFields":true,\
    "withUserResults":true,\
    "withBirdwatchPivots":false,\
    "withReactionsMetadata":false,\
    "withReactionsPerspective":false,\
    "withSuperFollowsTweetFields":true,\
    "withReplays":true,\
    "withScheduledSpaces":true}"\
    |} id)
  in
  let query = [
    (
      "variables",
      params
    )
  ] in
  let headers = Header.of_list [
      (
        "authorization",
        "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
      )
    ]
  in
  let uri = with_query' (Uri.of_string "https://twitter.com/i/api/graphql/jyQ0_DEMZHeoluCgHJ-U5Q/AudioSpaceById") query in
  Client.get ~headers uri >>= fun (resp, body) ->
  let code = resp |> Response.status |> Code.code_of_status in
  Printf.printf "Response code: %d\n" code;
  Printf.printf "Headers: %s\n" (resp |> Response.headers |> Header.to_string);
  body |> Cohttp_lwt.Body.to_string >|= fun body ->
  Printf.printf "Body of length: %d\n" (String.length body);
  Yojson.Safe.from_string body

let metadata json =
  let open Yojson.Basic.Util in
  let root = json
             |> member "data"
             |> member "audioSpace"
             |> member "metadata"
  in
  let creator_info = root
                     |> member "creator_results"
                     |> member "result"
                     |> member "legacy"
  in
  let id = root |> member "rest_id" |> to_string in
  let url = "https://twitter.com/i/spaces/"^id in
  let title = root |> member "title" |> to_string in
  let creator_name = creator_info |> member "name" |> to_string in
  let start_date = root |> member "started_at" |> to_string_option in
  let state = root |> member "state" |> to_string in
  let available_for_replay = root |> member "available_for_replay" |> to_string in
  let media_key = root |> member "media_key" |> to_string in
  match start_date with
  | Some start_date -> Ok {
      id;
      url;
      title;
      creator_name;
      start_date;
      state;
      available_for_replay;
      media_key
    }
  | None ->
    let scheduled_start = root |> member "scheduled_start" |> to_string_option in
    match scheduled_start with
    | Some start -> Error ("Starts at "^start)
    | None -> Error "Space error"

let url {media_key; _} =
  let url = "https://twitter.com/i/api/1.1/live_video_stream/status/"^media_key in
  let headers = Header.of_list [
      (
        "authorization",
        "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
      );
      ("cookie", "auth_token=")
    ]
  in
  Client.get ~headers (Uri.of_string url)>>= fun (resp, body) ->
  let code = resp |> Response.status |> Code.code_of_status in
  Printf.printf "Response code: %d\n" code;
  Printf.printf "Headers: %s\n" (resp |> Response.headers |> Header.to_string);
  body |> Cohttp_lwt.Body.to_string >|= fun body ->
  Printf.printf "Body of length: %d\n" (String.length body);
  let json = Yojson.Safe.from_string body in
  let open Yojson.Safe.Util in
  json |> member "source" |> member "location" |> to_string



let () =
  let body = Lwt_main.run (metadata_json "https://reddit.com/") in
  print_endline ("Received body\n" ^ Yojson.Safe.to_string body)
