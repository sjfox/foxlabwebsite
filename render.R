find_quarto <- function() {
  candidates <- c(
    Sys.getenv("QUARTO_PATH"),
    Sys.which("quarto"),
    if (requireNamespace("quarto", quietly = TRUE)) {
      tryCatch(quarto::quarto_path(), error = function(e) "")
    } else {
      ""
    },
    "/Applications/RStudio.app/Contents/Resources/app/quarto/bin/quarto"
  )

  candidates <- candidates[nzchar(candidates)]
  candidates[file.exists(candidates)][1]
}

quarto_bin <- find_quarto()

if (is.na(quarto_bin) || !nzchar(quarto_bin)) {
  stop("Could not find Quarto. Install Quarto or set QUARTO_PATH to the quarto executable.")
}

message("Using Quarto: ", quarto_bin)
status <- system2(quarto_bin, c("render", "."))

if (!identical(status, 0L)) {
  stop("Quarto render failed with status ", status, call. = FALSE)
}
