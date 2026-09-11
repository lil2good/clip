function key(entry) {
  return entry.type === "image" ? "image:" + entry.path : "text:" + entry.text
}

function parse(raw) {
  var values = JSON.parse(raw || "[]")
  if (!Array.isArray(values)) throw new Error("History must be an array")
  return values.map(function(value, index) {
    if (typeof value === "string") value = {type: "text", text: value}
    if (!value || (value.type !== "text" && value.type !== "image")) return null
    if (value.type === "text" && typeof value.text !== "string") return null
    if (value.type === "image" && typeof value.path !== "string") return null
    return {entry: value, historyIndex: index}
  }).filter(function(value) { return value !== null })
}

function paths(text) {
  return text.trim().split(/\r?\n/).map(function(line) {
    if (/^file:\/\/(localhost)?\//.test(line)) {
      try { return decodeURIComponent(line.replace(/^file:\/\/(localhost)?/, "")) } catch (_) { return "" }
    }
    return /^(\/|~\/)/.test(line) ? line : ""
  }).filter(function(path) { return path.length > 0 })
}

function kind(entry) {
  if (entry.type === "image") return "image"
  var text = entry.text.trim()
  if (/^#[\da-f]{3}([\da-f]{3})?$/i.test(text)) return "color"
  if (/^https?:\/\/[^\s]+$/i.test(text)) return "url"
  if (paths(text).length) return "path"
  return "text"
}

function rows(history, pins, filter, query) {
  var terms = query.toLowerCase().trim().split(/\s+/).filter(Boolean)
  return history.map(function(item) {
    var entry = item.entry
    var chip = kind(entry)
    var content = entry.type === "image" ? entry.path : entry.text
    var files = entry.type === "text" ? paths(entry.text) : []
    var identity = key(entry)
    var pinned = pins.indexOf(identity) !== -1
    var search = (content + " " + chip + " " + (entry.mime || "") + " " + (entry.capturedAt || "")).toLowerCase()
    if (filter === "Text" && entry.type !== "text") return null
    if (filter === "Images" && chip !== "image") return null
    if (filter === "Files" && chip !== "path") return null
    if (filter === "Pins" && !pinned) return null
    if (!terms.every(function(term) { return search.indexOf(term) !== -1 })) return null
    var image = entry.type === "image" ? entry.path : ""
    if (files.length === 1 && /\.(png|jpe?g|webp|gif|bmp)$/i.test(files[0]) && files[0][0] === "/") image = files[0]
    var title = entry.type === "image" ? (entry.capturedAt ? "Image · " + entry.capturedAt : "Image") : content.replace(/\s+/g, " ").trim()
    if (files.length) title = files.length > 1 ? files.length + " files" : files[0].split("/").pop() || files[0]
    return {identity: identity, historyIndex: item.historyIndex, entryType: entry.type,
      chip: chip, pinned: pinned, title: title.slice(0, 240), content: content,
      image: image, path: entry.path || "", mime: entry.mime || "image/png",
      metadata: entry.type === "image" ? (entry.mime || "image/png") :
        files.length ? files.length + (files.length === 1 ? " file path" : " file paths") :
        content.length + " characters · " + content.split("\n").length + " lines"}
  }).filter(function(row) { return row !== null })
}
