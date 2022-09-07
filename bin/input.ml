type input = Space of string
           | Playlist of string
           | MetadataPath of string

let input_parsing arg =
  match%pcre arg with
  | {|spaces/(?<id>\w{13})|} -> Ok(Space(id))
  | {|playlist.*\.m3u8|} -> Ok(Playlist(arg))
  | {|.json$|} -> Ok(MetadataPath(arg))
  | _ -> Error (`Msg "Not a valid input. Can either be a space url, a dynamic url, or a metadata file (more info with --help)")
