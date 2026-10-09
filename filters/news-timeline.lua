-- Expand after project pre-render, so a fresh checkout needs no generated include.
function RawBlock(block)
  if block.format == "html" and block.text:find("FOX_LAB_NEWS_TIMELINE", 1, true) then
    local path = quarto.project.directory .. "/news/_timeline.qmd"
    local file = assert(io.open(path, "r"), "News generation did not create " .. path)
    local content = file:read("*a")
    file:close()
    content = content:gsub("^```{=html}\n", ""):gsub("\n```\n$", "")
    return pandoc.RawBlock("html", content)
  end
end
