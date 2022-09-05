(lang dune 3.4)

(name twspace_dl)

(generate_opam_files true)

(source
 (github Ryu1845/twspace-dl))

(authors "Ryu1845 <ryu@tpgjbo.xyz")

(maintainers "Ryu1845 <ryu@tpgjbo.xyz")

(license LICENSE)

(documentation https://url/to/documentation)

(package
 (name twspace_dl)
 (synopsis "A downloader for Twitter Spaces")
 (description "A longer description")
 (depends ocaml dune cmdliner ppx_regexp cohttp cohttp-lwt-unix lwt yojson re)
 (tags
  (topics "to describe" your project)))

; See the complete stanza docs at https://dune.readthedocs.io/en/stable/dune-files.html#dune-project
