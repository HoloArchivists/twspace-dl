open Input

let input_str = function
  | Space(x) -> "space: "^x
  | Playlist(x) -> "dynamic: "^x
  | MetadataPath(x) -> "metadata: "^x

let print_input input fmt=
  match input_parsing input with
  | Ok x -> Format.printf "input = %s\nformat = %s\n" (input_str x) fmt
  | Error (`Msg x) ->
    Format.fprintf Format.err_formatter "%s\n" x;
    exit 123

open Metadata

let output_name ~name {creator_name; title; id; _} =
  match name with
  | Some name -> name
  | None -> [%string "[%{creator_name}]%{title}-%{id}.m4a"]


let _download stream output =
  let code = Sys.command (
      [%string "ffmpeg -i %{stream} -loglevel error -movflags faststart -stats -hide_banner -nostdin -c copy '%{output}'"]
    ) in
  if code != 0
  then print_endline "ffmpeg error"; exit 123

let download input input2 name_opt =
  let name = match name_opt with
    | Some x -> x
    | None -> "no_fmt"
  in
  (match input2 with
   | Some(x) -> print_input x name
   | None ->
     let input = input_parsing input in
     match input with
     | Ok x -> (match x with
         | Space x ->
           let fn = Lwt_main.run( x |> metadata_json ) |> metadata |> output_name ~name:name_opt in
           let url = Lwt_main.run (Lwt_main.run(x |> metadata_json) |> metadata |> url) in
           _download url fn
         | Playlist x ->
           (*TODO convert dynamic to master to playlist*)
           let open Re.Str in
           let name = List.nth (split (regexp "/") x) 6 in
           let name = name^".m4a" in
           print_endline name;
           _download x name
         | MetadataPath x ->
           let fn =  x |> Yojson.Safe.from_file|> metadata |> output_name ~name:name_opt in
           let url = Lwt_main.run (x |> Yojson.Safe.from_file |> metadata |> url) in
           _download url fn
       )
     | Error `Msg x -> print_endline x; exit 123
  )
