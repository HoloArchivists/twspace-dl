let version = "2.0.0"
(* Implementation of the command, we just print the args. *)

open Metadata
open Download
open Input

(* Command line interface *)

open Cmdliner

(* Help sections common to all commands *)

let sdocs = Manpage.s_common_options

let input =
  let doc = "Can either be a $(b,space url) (e.g. https://twitter.com/i/spaces/1mnxeddoEYrJX?s=20),
a $(b,dynamic url) (e.g. https://prod-fastly-eu-west-3.video.pscp.tv/Transcoding/v1/hls/
nc2H9Y402i-QjOTliV9UT2VWqpZ33ZLuEF53oi1Fx37IIItWTJ6-Twl3yxaCQP8dbHoWr6JuioACTTA3V24OFA/
non_transcode/eu-west-3/periscope-replay-direct-prod-eu-west-3-public/audio-space/
dynamic_playlist.m3u8?type=live) or a $(b,metadata file) (which you can get using the metadata command)" in
  Arg.(required & pos ~rev:true 0 (some string) None & info [] ~docv:"INPUT" ~doc)

let input2 =
  let doc = "Second Input" in
  Arg.(value & pos ~rev:true 1 (some string) None & info [] ~docv:"INPUT2" ~doc)

let formatting_str =
  let doc = "Format for the output file path" in
  Arg.(value & opt (some string) None & info ["o"; "output"] ~docv:"FMT" ~doc)

let download_cmd =
  let doc = "Utility to download twitter spaces" in
  let info = Cmd.info "download" ~doc in
  Cmd.v info Term.(const download $ input $ input2 $ formatting_str)

let metadata_cmd =
  let doc = "Utility to save twitter space metadata" in
  let info = Cmd.info "metadata" ~doc in
  let func input = match input_parsing input with
    | Ok Space x -> Lwt_main.run (x |> metadata_json) |> Yojson.Safe.pretty_print Format.std_formatter
    | Error `Msg x -> print_endline x; exit 123
    | _ -> print_endline "Metadata only works with space URLs"; exit 123
  in
  Cmd.v info Term.(const func $ input)

let url_cmd =
  let doc = "Utility to get the media url of a twitter space (to play it in a media player for example)" in
  let info = Cmd.info "url" ~doc in
  let func input = match input_parsing input with
    | Ok x -> (match x with
        | Space x -> Lwt_main.run (Lwt_main.run(x |> metadata_json) |> metadata |> url) |> print_endline
        | MetadataPath x -> Lwt_main.run (x |> Yojson.Safe.from_file |> metadata |> url) |> print_endline
        | Dynamic _ -> print_endline "Metadata only works with space URLs and metadata files"; exit 123)
    | Error `Msg x -> print_endline x; exit 123
  in
  Cmd.v info Term.(const func $ input)

let main_cmd =
  let doc = "a revision control system" in
  let info = Cmd.info "twspace-dl" ~version ~doc ~sdocs in
  Cmd.group info [download_cmd; metadata_cmd; url_cmd]

let main () = exit (Cmd.eval main_cmd)
let () = main ()
