
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

let pring_input input fmt=
  match input_parsing input with
  | Ok x -> Format.printf "input = %s\nformat = %s\n" (input_str x) fmt
  | Error (`Msg x) ->
    Format.fprintf Format.err_formatter "%s\n" x;
    exit 123

let download input input2 fmt=
  match fmt with
  | Some(fmt) -> pring_input input fmt;
    (match input2 with
     | Some(x) -> pring_input x fmt
     | None -> ())
  | None -> pring_input input "";
    (match input2 with
     | Some(x) -> pring_input x ""
     | None -> ())
