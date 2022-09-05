type space = {
  id: string;
  url: string;
  title: string;
  creator_name: string;
  start_date: int option;
  scheduled_start: int option;
  state: string;
  available_for_replay: bool;
  media_key: string
}

open Lwt
open Cohttp
open Cohttp_lwt_unix
open Uri

let metadata_json id =
  let open Re.Str in
  let params = global_replace (regexp "[ \n]") "" (Format.sprintf {|
         {"id":"%s",
         "isMetatagsQuery":false,
         "withSuperFollowsUserFields":true,
         "withDownvotePerspective":false,
         "withReactionsMetadata":false,
         "withReactionsPerspective":false,
         "withSuperFollowsTweetFields":true,
         "withReplays":true}
       |} id)
  in
  (* let params = {|{"id":"1mnxeddoEYrJX","isMetatagsQuery":true,"withSuperFollowsUserFields":true,"withDownvotePerspective":false,"withReactionsMetadata":false,"withReactionsPerspective":false,"withSuperFollowsTweetFields":true,"withReplays":true}|} in *)
  let query = [
    (
      "variables",
      params
    );
    (
      "features",
      (* {|{"spaces_2022_h2_clipping":true,"spaces_2022_h2_spaces_communities":false,"dont_mention_me_view_api_enabled":true,"responsive_web_uc_gql_enabled":true,"vibe_api_enabled":true,"responsive_web_edit_tweet_api_enabled":true,"graphql_is_translatable_rweb_tweet_is_translatable_enabled":false,"standardized_nudges_misinfo":true,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":false,"responsive_web_graphql_timeline_navigation_enabled":false,"interactive_text_enabled":true,"responsive_web_text_conversations_enabled":false,"responsive_web_enhance_cards_enabled":true}|} *)
      global_replace (regexp "[ \n]") "" {|
         {"spaces_2022_h2_clipping":true,
         "spaces_2022_h2_spaces_communities":false,
         "dont_mention_me_view_api_enabled":true,
         "responsive_web_uc_gql_enabled":true,
         "vibe_api_enabled":true,
         "responsive_web_edit_tweet_api_enabled":true,
         "graphql_is_translatable_rweb_tweet_is_translatable_enabled":false,
         "standardized_nudges_misinfo":true,
         "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":false,
         "responsive_web_graphql_timeline_navigation_enabled":false,
         "interactive_text_enabled":true,
         "responsive_web_text_conversations_enabled":false,
         "responsive_web_enhance_cards_enabled":true}
         |}
    )
  ] in
  let headers = Header.of_list [
      (
        "authorization",
        "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
      );
      (
        "x-guest-token",
        "1566726640129933312"
      )
    ]
  in
  let uri = with_query' (Uri.of_string "https://twitter.com/i/api/graphql/gMM94mZD6vm7pgAmurx0gQ/AudioSpaceById") query in
  (* print_endline (Uri.to_string uri); *)
  Client.get ~headers uri >>= fun (_, body) ->
  (* let code = resp |> Response.status |> Code.code_of_status in *)
  (* Format.fprintf Format.err_formatter "Response code: %d\n" code; *)
  (* Format.fprintf Format.err_formatter "Headers: %s\n" (resp |> Response.headers |> Header.to_string); *)
  body |> Cohttp_lwt.Body.to_string >|= fun body ->
  (* Format.fprintf Format.err_formatter "Body of length: %d\n" (String.length body); *)
  (* print_endline body; *)
  Yojson.Safe.from_string body

let metadata json =
  let open Yojson.Safe.Util in
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
  let start_date = root |> member "started_at" |> to_int_option in
  let state = root |> member "state" |> to_string in
  let available_for_replay = root |> member "is_space_available_for_replay" |> to_bool in
  let media_key = root |> member "media_key" |> to_string in
  let scheduled_start = root |> member "scheduled_start" |> to_int_option in
  {
    id;
    url;
    title;
    creator_name;
    start_date;
    scheduled_start;
    state;
    available_for_replay;
    media_key
  }

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
  Client.get ~headers (Uri.of_string url)>>= fun (_, body) ->
  (* let code = resp |> Response.status |> Code.code_of_status in *)
  (* Printf.printf "Response code: %d\n" code; *)
  (* Printf.printf "Headers: %s\n" (resp |> Response.headers |> Header.to_string); *)
  body |> Cohttp_lwt.Body.to_string >|= fun body ->
  (* Printf.printf "Body of length: %d\n" (String.length body); *)
  let json = Yojson.Safe.from_string body in
  let open Yojson.Safe.Util in
  json |> member "source" |> member "location" |> to_string

