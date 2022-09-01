(* Implementation of the command, we just print the args. *)

type input = Space of string
           | Dynamic of string
           | MetadataPath of string
let input_parsing arg =
  match%pcre arg with
  | {|spaces/\w*|} -> Ok(Space(arg))
  | {|dynamic_playlist|} -> Ok(Dynamic(arg))
  | {|.json$|} -> Ok(MetadataPath(arg))
  | _ -> Error (`Msg "Not a valid input")

let input_str = function
  | Space(x) -> "space: "^x
  | Dynamic(x) -> "dynamic: "^x
  | MetadataPath(x) -> "metadata: "^x

let twspace_dl input =
  match input_parsing input with
  | Ok x -> Format.printf "input = %s\n" (input_str x)
  | Error (`Msg x) ->
    Format.fprintf Format.err_formatter "%s\n" x;
    exit 123

(* Command line interface *)

open Cmdliner

let input =
  let doc = "Input" in
  let arg = Arg.(required & pos ~rev:true 0 (some string) None & info [] ~docv:"INPUT" ~doc) in
  arg


let cmd =
  let doc = "Script designed to help download twitter spaces" in
  let man = [
    `S Manpage.s_description;
    `P "$(tname) downloads Twitter spaces."
  ]
  in
  let info = Cmd.info "twspace-dl" ~version:"%%VERSION%%" ~doc ~man in
  Cmd.v info Term.(const twspace_dl $ input)

let main () = exit (Cmd.eval cmd)
let () = main ()
